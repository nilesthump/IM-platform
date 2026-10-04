package im.platform.client.ui
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import im.platform.client.send.*
import im.platform.client.send.Wire as SendWire
import im.platform.client.storage.Repository
import im.platform.client.sync.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
data class WorkspaceState(val appearance:Appearance=Appearance(),val busy:Boolean=false,val error:String?=null,val session:SendSession?=null,val offlineAccount:String?=null,val profile:User?=null,val friends:List<Friend> = emptyList(),val results:List<User> = emptyList(),val conversations:List<String> = emptyList(),val selected:String="",val messages:List<List<String?>> = emptyList(),val connection:String="offline",val sync:String="idle",val unavailable:List<String> = emptyList(),val endpoint:String="https://localhost:8443")
class WorkspaceViewModel(application:Application):AndroidViewModel(application) {
    private val scope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate)
    private val preferences=Preferences(application)
    private var auth:Auth?=null;private var sync:SyncViewModel?=null;private var offlineRepository:Repository?=null;private var generation=0L;private var operation=0L;private var observers:Job?=null;private var refreshTimer:Job?=null
    private val mutable=MutableStateFlow(WorkspaceState());val state:StateFlow<WorkspaceState> = mutable.asStateFlow()
    private fun publish(change:(WorkspaceState)->WorkspaceState){mutable.value=change(mutable.value)}
    init{scope.launch{try{val value=withContext(Dispatchers.IO){preferences.loadAppearance()};publish{it.copy(appearance=value)}}catch(_:Exception){publish{it.copy(error="Appearance unavailable")}}}}
    private val appearanceWrites=Mutex()
    fun appearance(value:Appearance){publish{it.copy(appearance=value,error=null)};scope.launch{appearanceWrites.withLock{try{withContext(Dispatchers.IO){preferences.saveAppearance(value)}}catch(_:Exception){publish{it.copy(error="Appearance could not be saved")}}}}}
    private suspend fun stop(){generation++;refreshTimer?.cancel();refreshTimer=null;observers?.cancel();observers=null;val old=sync;sync=null;val offline=offlineRepository;offlineRepository=null;publish{WorkspaceState(appearance=it.appearance,endpoint=it.endpoint,busy=it.busy)};withContext(Dispatchers.IO){old?.dispose();offline?.close()}}
    private fun fail(e:Exception){val kind=if(e is ApiFailure)e.kind else "Operation unavailable";publish{it.copy(error=kind)};if(kind=="Session expired")expire()}
    private suspend fun bind(session:SendSession,op:Long){
        if(op!=operation)return;stop();if(op!=operation)return;val g=generation;val authOwner=auth
        val repo=withContext(Dispatchers.IO){Repository(getApplication(),session.userId).also{it.initialize()}}
        if(g!=generation || op!=operation){repo.close();return}
        val send=SendViewModel(repo,session,factory={url,open,message,end->Wss(url,open,{raw->
            val frame=try{SendWire.decode(raw)}catch(_:Exception){null}
            if(frame?.type=="session.revoked" || frame?.type=="auth.ack" && frame.payload["status"]=="rejected")scope.launch{if(g==generation)expire()}else message(raw)
        },end)},ownsRepository=true)
        val owner=SyncViewModel(send,repo,SyncHttps(state.value.endpoint,session));sync=owner
        val ids=withContext(Dispatchers.IO){repo.conversationIds()};if(g!=generation || op!=operation)return;publish{it.copy(session=session,conversations=ids,selected=ids.firstOrNull()?:"",error=null)}
        observers=scope.launch {
            launch{send.state.collect{s->if(g==generation)publish{it.copy(messages=s.messages,connection=s.connection,error=s.error?:it.error)}}}
            launch{owner.state.collect{s->if(g==generation){publish{it.copy(sync=s.status,unavailable=s.unavailable,error=s.error?.let{"Sync "+it}?:it.error)};if(s.error=="authentication")expire();if(s.status=="idle"){val rows=withContext(Dispatchers.IO){repo.conversationIds()};if(g==generation)publish{it.copy(conversations=rows)}}}}}
        }
        if(ids.isNotEmpty())send.openConversation(ids.first());if(g!=generation)return
        send.connect(state.value.endpoint.replaceFirst("https:","wss:")+"/v1/ws")
        refreshTimer=scope.launch{while(isActive){delay(30000);if(g==generation && auth?.needsRefresh()==true && !state.value.busy)refresh()}}
        try{val profile=authOwner!!.profile();if(g!=generation || op!=operation)return;val friends=authOwner.friends();if(g==generation && op==operation)publish{it.copy(profile=profile,friends=friends)}}catch(e:Exception){if(g==generation && op==operation)fail(e)}
    }
    fun login(endpoint:String,username:String,password:String){if(state.value.busy)return;val op=++operation;scope.launch{publish{it.copy(busy=true,error=null)};try{stop();withContext(Dispatchers.IO){auth?.clear()};if(op!=operation)return@launch;val base=serverOrigin(endpoint);publish{it.copy(endpoint=base)};val owner=Auth(base,preferences);auth=owner;val session=owner.login(username,password);if(op==operation)bind(session,op)}catch(e:Exception){if(op==operation)fail(e)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun restore(endpoint:String){if(state.value.busy)return;val op=++operation;scope.launch{publish{it.copy(busy=true,error=null)};try{stop();val g=generation;val base=serverOrigin(endpoint);publish{it.copy(endpoint=base)};val owner=Auth(base,preferences);auth=owner;val account=withContext(Dispatchers.IO){owner.savedAccount()};if(op!=operation)return@launch;if(account==null){publish{it.copy(error="No saved session for this server")};return@launch};val repo=withContext(Dispatchers.IO){Repository(getApplication(),account).also{it.initialize()}};val ids=withContext(Dispatchers.IO){repo.conversationIds()};val selected=ids.firstOrNull()?:"";val messages=withContext(Dispatchers.IO){if(selected.isNotEmpty())repo.messages(selected)else emptyList()};if(op!=operation){repo.close();return@launch};offlineRepository=repo;publish{it.copy(offlineAccount=account,conversations=ids,selected=selected,messages=messages,error="Showing saved history while the secure session resumes")};val session=withContext(Dispatchers.IO){owner.refresh()};if(op==operation)bind(session,op)}catch(e:Exception){if(op==operation)fail(e)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun refresh(){if(state.value.busy)return;val op=++operation;scope.launch{publish{it.copy(busy=true,error=null)};try{auth?.let{val session=withContext(Dispatchers.IO){it.refresh()};if(op==operation)bind(session,op)}}catch(e:Exception){if(op==operation)fail(e)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun expire(){val op=++operation;val owner=auth;auth=null;scope.launch{stop();try{withContext(Dispatchers.IO){owner?.clear()};if(op==operation)publish{it.copy(busy=false,error="Session expired. Sign in again.")}}catch(_:Exception){if(op==operation)publish{it.copy(busy=false,error="Session expired; secure cleanup failed")}}}}
    fun logout(){val op=++operation;scope.launch{publish{it.copy(busy=true)};val owner=auth;auth=null;val remote=async(Dispatchers.IO,start=CoroutineStart.UNDISPATCHED){owner?.logout()};stop();try{remote.await();if(op==operation)publish{it.copy(error=null)}}catch(e:Exception){if(op==operation)fail(e)}finally{if(op==operation)publish{it.copy(busy=false)}}}}
    fun open(id:String){val owner=sync;val offline=offlineRepository;val g=generation;publish{it.copy(selected=id,error=null)};scope.launch{try{if(offline!=null){val messages=withContext(Dispatchers.IO){offline.messages(id)};if(g==generation)publish{it.copy(messages=messages)}}else owner?.openConversation(id)}catch(_:Exception){if(g==generation)publish{it.copy(error="Sync unavailable; showing local history")}}}}
    fun send(text:String){val owner=sync?:return;val c=state.value.selected;val g=generation;scope.launch{try{withContext(Dispatchers.IO){owner.send.send(c,text)}}catch(_:Exception){if(g==generation)publish{it.copy(error="Message could not be saved")}}}}
    fun retry(id:String){val owner=sync?:return;val c=state.value.selected;val g=generation;scope.launch{try{withContext(Dispatchers.IO){owner.send.retry(c,id)}}catch(_:Exception){if(g==generation)publish{it.copy(error="Retry unavailable")}}}}
    fun disconnect(){scope.launch{sync?.send?.disconnect()}}
    fun reconnect(){val owner=sync?:return;val g=generation;scope.launch{try{owner.send.connect(state.value.endpoint.replaceFirst("https:","wss:")+"/v1/ws");owner.synchronize()}catch(_:Exception){if(g==generation)publish{it.copy(error="Connection unavailable")}}}}
    fun search(query:String){val owner=auth?:return;val g=generation;publish{it.copy(busy=true,results=emptyList(),error=null)};scope.launch{try{val results=owner.search(query);if(g==generation)publish{it.copy(results=results)}}catch(e:Exception){if(g==generation)fail(e)}finally{if(g==generation)publish{it.copy(busy=false)}}}}
    fun add(id:String){val owner=auth?:return;val g=generation;publish{it.copy(busy=true,error=null)};scope.launch{try{val c=owner.add(id);if(g!=generation)return@launch;val friends=owner.friends();if(g==generation){publish{it.copy(friends=friends,conversations=(it.conversations+c).distinct())};open(c)}}catch(e:Exception){if(g==generation)fail(e)}finally{if(g==generation)publish{it.copy(busy=false)}}}}
    override fun onCleared(){generation++;observers?.cancel();refreshTimer?.cancel();val owner=sync;val offline=offlineRepository;sync=null;offlineRepository=null;scope.launch{try{withContext(Dispatchers.IO){owner?.dispose();offline?.close()}}finally{scope.cancel()}}}
}
