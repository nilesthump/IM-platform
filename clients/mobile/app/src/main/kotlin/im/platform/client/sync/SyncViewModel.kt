package im.platform.client.sync
import androidx.lifecycle.ViewModel
import im.platform.client.send.SendViewModel
import im.platform.client.send.SendSession
import im.platform.client.send.Wire as SendWire
import im.platform.client.storage.Repository
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.atomic.AtomicBoolean

data class SyncState(val status:String="idle",val error:String?=null,val unavailable:List<String> = emptyList())
class SyncViewModel(val send:SendViewModel,private val repo:Repository,private val http:SyncHttps):ViewModel() {
    private val scope=CoroutineScope(SupervisorJob()+Dispatchers.IO)
    @Volatile private var opened=""
    private val lock=Mutex();private val pending=AtomicBoolean(false)
    @Volatile private var generation=0L
    @Volatile private var retired=false
    @Volatile private var stopped=false
    @Volatile private var pull:Job?=null
    private val mutableState=MutableStateFlow(SyncState())
    val state:StateFlow<SyncState> = mutableState.asStateFlow()
    private val detach:()->Unit
    init {
        require(send.matchesRepository(repo) && http.matchesSession {send.matchesSession(it)}) {"Mismatched Sync session"}
        detach=send.observeDelivery {_,_->if(send.state.value.connection=="ready")enqueue()}
        scope.launch {
            var ready=false
            send.state.collect {s->
                val now=s.connection=="ready"
                if(!now && ready){generation++;pull?.cancel()}
                if(now && !ready && !stopped)enqueue()
                ready=now
            }
        }
    }
    private fun enqueue(){scope.launch {try{synchronize()}catch(_:Exception){/* Failure already observable. */}}}
    suspend fun openConversation(c:String){val selected=SendWire.uuid(c);send.openConversation(selected);opened=selected;synchronize()}
    suspend fun synchronize() {
        if(retired || stopped)return;pending.set(true)
        lock.withLock {
            if(!pending.getAndSet(false) || retired || stopped)return
            val g=generation;val job=currentCoroutineContext()[Job];pull=job
            fun active()=!retired && !stopped && generation==g && job?.isActive!=false
            val unavailable=mutableListOf<String>();mutableState.value=SyncState("syncing")
            try {
                while(active()){
                    val cursor=repo.cursor();val page=http.user(cursor);if(!active())return
                    send.mergeUserPage(page.events,page.nextCursor,cursor,::active);if(!active())return
                    if(!page.hasMore)break;if(repo.cursor()==cursor)throw SyncFailure("protocol")
                }
                for(c in (repo.conversationIds()+listOfNotNull(opened.takeIf {it.isNotEmpty()})).distinct()){
                    try {
                        while(active()){
                            val after=repo.contiguous(c);val page=http.conversation(c,after);if(!active())return
                            send.mergeMessages(page.messages,::active);if(!active())return
                            if(!page.hasMore)break;if(repo.contiguous(c)<=after)throw SyncFailure("protocol")
                        }
                    }catch(error:SyncFailure){if(error.kind=="unavailable"){unavailable.add(c);continue};throw error}
                }
                if(active())mutableState.value=SyncState(unavailable=unavailable.toList())
            }catch(error:Exception){
                if(!active())return
                val kind=if(error is SyncFailure)error.kind else "storage"
                if(kind=="authentication"){stopped=true;generation++;send.disconnect()}
                mutableState.value=SyncState("failed",kind,unavailable.toList());throw SyncFailure(kind)
            }finally{if(pull===job)pull=null}
        }
    }
    suspend fun dispose(){
        if(retired)return;retired=true;generation++;detach();scope.coroutineContext[Job]?.cancelAndJoin()
        pull?.cancelAndJoin();mutableState.value=SyncState("retired");send.dispose()
    }
    override fun onCleared(){retired=true;generation++;detach();pull?.cancel();scope.launch {try {pull?.cancelAndJoin();send.dispose()} finally {scope.cancel()}}}
}
suspend fun accountSync(context:android.content.Context,session:SendSession,endpoint:String):SyncViewModel=withContext(Dispatchers.IO){
    val http=SyncHttps(endpoint,session);val repository=Repository(context,session.userId)
    try{repository.initialize();SyncViewModel(SendViewModel(repository,session,ownsRepository=true),repository,http)}
    catch(_:Exception){repository.close();throw SyncFailure("storage")}
}
