package im.platform.client.ui
import android.app.Application
import im.platform.client.group.*
import im.platform.client.ui.i18n.errorKey
import androidx.lifecycle.AndroidViewModel
import im.platform.client.send.*
import im.platform.client.send.Wire as SendWire
import im.platform.client.storage.Repository
import im.platform.client.sync.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
data class ConversationPreview(val text:String,val time:Long)
data class WorkspaceState(val groups:List<MemberRow> = emptyList(),val groupBusy:Boolean=false,val groupStatus:String="",val groupError:String="",val language:String="en",val languageStored:Boolean=true,val appearance:Appearance=Appearance(),val busy:Boolean=false,val error:String?=null,val session:SendSession?=null,val offlineAccount:String?=null,val profile:User?=null,val friends:List<Friend> = emptyList(),val results:List<User> = emptyList(),val searchComplete:Boolean=false,val conversations:List<String> = emptyList(),val selected:String="",val messages:List<List<String?>> = emptyList(),val connection:String="offline",val sync:String="idle",val unavailable:List<String> = emptyList(),val endpoint:String="https://localhost:8443",val previews:Map<String,ConversationPreview> = emptyMap(),val registered:Boolean=false)
class WorkspaceViewModel(application:Application):AndroidViewModel(application) {
    private val scope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate)
    private val preferences=Preferences(application)
    private var friendRevision=0L;private var friendCursor="";private var repository:Repository?=null;private var listRevision=0L;private val activity=mutableMapOf<String,Long>()
    private var auth:Auth?=null;private var sync:SyncViewModel?=null;private var offlineRepository:Repository?=null;private var generation=0L;private var operation=0L;private var observers:Job?=null;private var refreshTimer:Job?=null
    private val mutable=MutableStateFlow(WorkspaceState());val state:StateFlow<WorkspaceState> = mutable.asStateFlow()
    private fun publish(change:(WorkspaceState)->WorkspaceState){mutable.value=change(mutable.value)}
    private var languageRevision=0L
    init{val revision=languageRevision;scope.launch{val language=withContext(Dispatchers.IO){preferences.loadLanguage()};if(revision==languageRevision)publish{it.copy(language=language)};try{val value=withContext(Dispatchers.IO){preferences.loadAppearance()};publish{it.copy(appearance=value)}}catch(e:Exception){fail(e);publish{it.copy(error="error.appearanceLoad")}}}}
    private val languageWrites=Mutex()
    fun language(value:String){if(!im.platform.client.ui.i18n.validLocale(value))return;val revision=++languageRevision;publish{it.copy(language=value,languageStored=true)};scope.launch{languageWrites.withLock{try{withContext(Dispatchers.IO){preferences.saveLanguage(value)};publish{if(revision==languageRevision)it.copy(languageStored=true)else it}}catch(e:Exception){fail(e);publish{if(revision==languageRevision)it.copy(languageStored=false)else it}}}}}
    private val appearanceWrites=Mutex()
    fun appearance(value:Appearance){publish{it.copy(appearance=value,error=null)};scope.launch{appearanceWrites.withLock{try{withContext(Dispatchers.IO){preferences.saveAppearance(value)}}catch(e:Exception){fail(e);publish{it.copy(error="Appearance could not be saved")}}}}}
    private suspend fun stop(preserveGroup:Boolean=false){if(!preserveGroup)groupOperation=null;groupScanning=false;groupDirty=false;generation++;listRevision++;repository=null;friendCursor="";friendRevision++;activity.clear();refreshTimer?.cancel();refreshTimer=null;observers?.cancel();observers=null;val old=sync;sync=null;val offline=offlineRepository;offlineRepository=null;publish{WorkspaceState(groups=if(preserveGroup)it.groups else emptyList(),groupStatus=if(preserveGroup&&groupOperation!=null)"unconfirmed" else "",language=it.language,languageStored=it.languageStored,appearance=it.appearance,endpoint=it.endpoint,busy=it.busy)};withContext(Dispatchers.IO){old?.dispose();offline?.close()}}
    private fun fail(e:Exception,active:Boolean=true){if(e !is ApiFailure && e !is SyncFailure && e !is WireFailure && e !is SendStorageFailure && e !is java.io.IOException && e !is java.security.GeneralSecurityException)throw e;if(!active)return;publish{it.copy(error=if(e is ApiFailure)e.message else "Operation unavailable")};if(e is ApiFailure&&e.kind=="session_expired")expire()}
    private fun accountRepository(account:String):Repository {
        // Preserve the existing initialization failure projection at its actual
        // invocation. No Repository operation, write recovery or SQL changes.
        val repo=try {Repository(getApplication(),account)}catch(error:android.database.sqlite.SQLiteException){throw SendStorageFailure(error)}
        try {repo.initialize()}catch(error:android.database.sqlite.SQLiteException){throw SendStorageFailure(error)}
        return repo
    }
    private suspend fun bind(session:SendSession,op:Long){
        if(op!=operation)return;stop(state.value.session?.userId==session.userId);if(op!=operation)return;val g=generation;val authOwner=auth
        val repo=withContext(Dispatchers.IO){accountRepository(session.userId)}
        if(g!=generation || op!=operation){repo.close();return}
        val send=SendViewModel(repo,session,factory={url,open,message,end->Wss(url,open,{raw->
            val frame=try{SendWire.decode(raw)}catch(_:WireFailure){null}
            if(frame?.type=="session.revoked" || frame?.type=="auth.ack" && frame.payload["status"]=="rejected")scope.launch{if(g==generation)expire()}else message(raw)
        },end)},ownsRepository=true)
        repository=repo;val owner=SyncViewModel(send,repo,SyncHttps(state.value.endpoint,session));sync=owner
        val ids=withContext(Dispatchers.IO){repositoryRead {repo.conversationIds()}};if(g!=generation || op!=operation)return;publish{it.copy(session=session,conversations=ids,selected="",error=null)}
        observers=scope.launch {
            launch{send.state.collect{s->if(g==generation){publish{it.copy(connection=s.connection,error=s.error?:it.error)};updateList(repo,g)}}}
            launch{owner.state.collect{s->if(g==generation){publish{it.copy(sync=s.status,unavailable=s.unavailable,error=s.error?.let{"Sync "+it}?:it.error)};if(s.error=="authentication")expire();if(s.status=="idle"){updateList(repo,g);refreshFriends(repo,g);refreshGroups()}}}}
        }
        updateList(repo,g);if(g!=generation)return
        send.connect(state.value.endpoint.replaceFirst("https:","wss:")+"/v1/ws")
        refreshTimer=scope.launch{while(isActive){delay(30000);if(g==generation && auth?.needsRefresh()==true && !state.value.busy)refresh()}}
        try{val profile=authOwner!!.profile();if(g!=generation || op!=operation)return;publish{it.copy(profile=profile)};refreshFriends(repo,g);refreshGroups()}catch(e:Exception){fail(e,g==generation && op==operation)}
    }
    private suspend fun refreshFriends(repo:Repository,g:Long){
        val owner=auth?:return;val revision=++friendRevision
        try{val cursor=withContext(Dispatchers.IO){repositoryRead {repo.cursor()}};if(g!=generation||cursor==friendCursor)return
            val friends=owner.friends();if(g!=generation||owner!==auth||revision!=friendRevision)return
            friendCursor=cursor;publish{it.copy(friends=friends)};updateList(repo,g)
        }catch(e:CancellationException){throw e}catch(e:Exception){fail(e,g==generation&&revision==friendRevision)}
    }
    private suspend fun updateList(repo:Repository,g:Long){
        val revision=++listRevision
        try {val friendIds=state.value.friends.map{it.directConversationId}+state.value.groups.map{it.conversationId};val localActivity=activity.toMap()
            val entries=withContext(Dispatchers.IO){(repositoryRead {repo.conversationIds()}+friendIds).distinct().map{id->val rows=repositoryRead {repo.messages(id)};val time=rows.mapNotNull{it[6]?.let{v->java.time.Instant.parse(v).toEpochMilli()}}.maxOrNull()?:0L;Triple(id,ConversationPreview(rows.lastOrNull()?.get(2)?:"",maxOf(time,localActivity[id]?:0L)),rows)}}
            if(g!=generation||revision!=listRevision)return
            val previews=entries.associate{it.first to it.second};val ids=previews.keys.sortedWith(compareByDescending<String>{previews[it]!!.time}.thenBy{it});publish{it.copy(conversations=ids,previews=previews,messages=entries.find{row->row.first==it.selected}?.third?:emptyList())}
        }catch(e:CancellationException){throw e}catch(e:Exception){fail(e,g==generation&&revision==listRevision);if(g==generation&&revision==listRevision)publish{it.copy(error="Conversation history unavailable")}}
    }
    fun register(username:String,password:String,confirmation:String){
        if(state.value.busy)return
        if(password!=confirmation){publish{it.copy(error="Passwords do not match")};return}
        if(!Regex("^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$").matches(username)||password.codePointCount(0,password.length) !in 12..256){publish{it.copy(error="Use a 3–64 character username and a 12–256 character password")};return}
        val op=++operation;publish{it.copy(busy=true,error=null,registered=false)}
        scope.launch{try{Auth(state.value.endpoint,preferences).register(username,password);if(op==operation)publish{it.copy(registered=true)}}catch(e:CancellationException){throw e}catch(e:Exception){fail(e,op==operation)}finally{if(op==operation)publish{it.copy(busy=false)}}}
    }
    fun login(endpoint:String,username:String,password:String){if(state.value.busy)return;val op=++operation;scope.launch{publish{it.copy(busy=true,error=null)};try{stop();withContext(Dispatchers.IO){auth?.clear()};if(op!=operation)return@launch;val base=serverOrigin(endpoint);publish{it.copy(endpoint=base)};val owner=Auth(base,preferences);auth=owner;val session=owner.login(username,password);if(op==operation)bind(session,op)}catch(e:Exception){fail(e,op==operation)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun restore(endpoint:String){if(state.value.busy)return;val op=++operation;scope.launch{publish{it.copy(busy=true,error=null)};try{stop();val g=generation;val base=serverOrigin(endpoint);publish{it.copy(endpoint=base)};val owner=Auth(base,preferences);auth=owner;val account=withContext(Dispatchers.IO){owner.savedAccount()};if(op!=operation)return@launch;if(account==null){publish{it.copy(error="No saved session for this server")};return@launch};val repo=withContext(Dispatchers.IO){accountRepository(account)};val ids=withContext(Dispatchers.IO){repositoryRead {repo.conversationIds()}};val selected="";val messages=withContext(Dispatchers.IO){if(selected.isNotEmpty())repositoryRead {repo.messages(selected)}else emptyList()};if(op!=operation){repo.close();return@launch};offlineRepository=repo;publish{it.copy(offlineAccount=account,conversations=ids,selected=selected,messages=messages,error="Showing saved history while the secure session resumes")};updateList(repo,g);val session=withContext(Dispatchers.IO){owner.refresh()};if(op==operation)bind(session,op)}catch(e:Exception){fail(e,op==operation)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun refresh(){if(state.value.busy)return;val owner=auth?:return;val op=++operation;val g=generation;scope.launch{publish{it.copy(busy=true,error=null)};try{val session=withContext(Dispatchers.IO){owner.refresh()};if(op==operation)bind(session,op)}catch(e:Throwable){
        var failure=e
        if(op==operation && owner===auth && g==generation && owner.session==null){auth=null;try{withContext(NonCancellable){stop()}}catch(cleanup:Throwable){if(cleanup!==e)failure=IllegalStateException("Refresh and retirement failed",e).also{it.addSuppressed(cleanup)}}}
        if(failure is Exception)fail(failure,op==operation)else throw failure
    }finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun expire(){val op=++operation;val owner=auth;auth=null;scope.launch{stop();try{withContext(Dispatchers.IO){owner?.clear()};if(op==operation)publish{it.copy(busy=false,error="Session expired. Sign in again.")}}catch(e:Exception){fail(e,op==operation);if(op==operation)publish{it.copy(busy=false,error="error.cleanup")}}}}
    fun logout(){val op=++operation;scope.launch{publish{it.copy(busy=true)};val owner=auth;auth=null;val remote=async(Dispatchers.IO){try{owner?.logout();null}catch(e:CancellationException){throw e}catch(e:Exception){e}};stop();try{remote.await()?.let{throw it};if(op==operation)publish{it.copy(error=null)}}catch(e:Exception){fail(e,op==operation)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun closeConversation(){publish{it.copy(selected="",messages=emptyList())}}
    fun open(id:String){val owner=sync;val offline=offlineRepository;val g=generation;publish{it.copy(selected=id,messages=emptyList(),error=null)};scope.launch{try{if(offline!=null){val messages=withContext(Dispatchers.IO){repositoryRead {offline.messages(id)}};if(g==generation&&state.value.selected==id)publish{it.copy(messages=messages)}}else owner?.openConversation(id)}catch(e:Exception){fail(e,g==generation);if(g==generation)publish{it.copy(error="Sync unavailable; showing local history")}}}}
    fun send(text:String){val owner=sync?:return;val c=state.value.selected;val g=generation;scope.launch{try{withContext(Dispatchers.IO){owner.send.send(c,text)};if(g==generation){activity[c]=System.currentTimeMillis();repository?.let{updateList(it,g)}}}catch(e:Exception){fail(e,g==generation);if(g==generation)publish{it.copy(error="Message could not be saved")}}}}
    fun retry(id:String){val owner=sync?:return;val c=state.value.selected;val g=generation;scope.launch{try{withContext(Dispatchers.IO){owner.send.retry(c,id)}}catch(e:Exception){fail(e,g==generation);if(g==generation)publish{it.copy(error="Retry unavailable")}}}}
    fun disconnect(){scope.launch{sync?.send?.disconnect()}}
    fun reconnect(){val owner=sync?:return;val g=generation;scope.launch{try{owner.send.connect(state.value.endpoint.replaceFirst("https:","wss:")+"/v1/ws");owner.synchronize()}catch(e:Exception){fail(e,g==generation);if(g==generation)publish{it.copy(error="Connection unavailable")}}}}
    fun search(query:String){val owner=auth?:return;val g=generation;publish{it.copy(busy=true,results=emptyList(),searchComplete=false,error=null)};scope.launch{try{val results=owner.search(query);if(g==generation)publish{it.copy(results=results,searchComplete=true)}}catch(e:Exception){fail(e,g==generation)}finally{if(g==generation)publish{it.copy(busy=false)}}}}
    fun add(id:String){val owner=auth?:return;val g=generation;publish{it.copy(busy=true,error=null)};scope.launch{try{val c=owner.add(id);if(g!=generation)return@launch;val revision=++friendRevision;val friends=owner.friends();if(g==generation&&owner===auth){if(revision==friendRevision)publish{it.copy(friends=friends,conversations=(it.conversations+c).distinct())};open(c)}}catch(e:Exception){fail(e,g==generation)}finally{if(g==generation)publish{it.copy(busy=false)}}}}
    private var groupOperation:GroupOperation?=null
    private var groupScanning=false;private var groupDirty=false
    fun createGroup(ids:List<String>,conversation:String?){val session=state.value.session?:return;if(state.value.groupBusy||groupOperation!=null)return
        groupOperation=GroupOperation(session.userId,java.util.UUID.randomUUID().toString(),GroupWire.targets(ids,session.userId).toList(),conversation);retryGroup()}
    fun retryGroup(){val op=groupOperation?:return;val owner=auth?:return;val session=state.value.session?:return;val g=generation;if(op.account!=session.userId||state.value.groupBusy)return
        publish{it.copy(groupBusy=true,groupStatus="loading",groupError="")};scope.launch{try{val c=GroupHttp(owner).mutate(op);if(g!=generation)return@launch;groupOperation=null;publish{it.copy(groupBusy=false,groupStatus="success")};refreshGroups();if(g==generation)open(c)}
        catch(e:CancellationException){throw e}catch(e:Exception){fail(e,g==generation);if(g==generation){val rejected=e is ApiFailure&&e.kind in listOf("VALIDATION_FAILED","AUTHORIZATION_DENIED","GROUP_REQUEST_CONFLICT");if(rejected)groupOperation=null;publish{it.copy(groupBusy=false,groupStatus=if(rejected)"rejected"else"unconfirmed",groupError=if(e is ApiFailure)e.kind else "protocol")}}}}
    }
    private suspend fun refreshGroups(){val owner=auth?:return;val g=generation;if(state.value.session==null)return;groupDirty=true;if(groupScanning)return;groupScanning=true
        try{val http=GroupHttp(owner);while(groupDirty&&g==generation){groupDirty=false;var c="";var u="";val rows=linkedMapOf<String,MemberRow>();var last:MemberRow?=null
            while(true){val page=http.members(c,u);if(g!=generation)return;for(row in page.items){val prior=last;if(prior?.conversationId==row.conversationId&&(prior.kind!=row.kind||prior.createdBy!=row.createdBy||prior.createdAt!=row.createdAt))throw im.platform.client.send.WireFailure();rows[row.conversationId+"/"+row.user.userId]=row;last=row};if(!page.more)break;c=page.afterConversation;u=page.afterMember}
            publish{it.copy(groups=rows.values.filter{row->row.kind=="GROUP"},groupError="")};repository?.let{updateList(it,g)}
        }}catch(e:CancellationException){throw e}catch(e:Exception){fail(e,g==generation);if(g==generation)publish{it.copy(groupError=if(e is ApiFailure)e.kind else "protocol")}}
        finally{if(g==generation)groupScanning=false}
    }
    override fun onCleared(){generation++;observers?.cancel();refreshTimer?.cancel();val owner=sync;val offline=offlineRepository;sync=null;offlineRepository=null;scope.launch{try{withContext(Dispatchers.IO){owner?.dispose();offline?.close()}}finally{scope.cancel()}}}
}
