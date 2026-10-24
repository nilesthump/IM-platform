package im.platform.client.ui.components
import androidx.compose.runtime.*
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.*

import im.platform.client.ui.*
import im.platform.client.ui.i18n.*
@Composable fun Shell(state:WorkspaceState,createGroup:(List<String>,String?)->Unit,retryGroup:()->Unit,language:(String)->Unit,closeConversation:()->Unit,open:(String)->Unit,reconnect:()->Unit,login:(String,String,String)->Unit,register:(String,String,String)->Unit,restore:(String)->Unit,send:(String)->Unit,retry:(String)->Unit,search:(String)->Unit,add:(String)->Unit,appearance:(Appearance)->Unit,refresh:()->Unit,disconnect:()->Unit,logout:()->Unit) {
    var draft by remember(state.session?.userId,state.offlineAccount){mutableStateOf("")}
    val t=useText()
    var groupPage by remember(state.session?.userId,state.offlineAccount){mutableStateOf("")}
    var groupTarget by remember(state.session?.userId,state.offlineAccount){mutableStateOf<String?>(null)}
    var groupSelection by remember(state.session?.userId,state.offlineAccount){mutableStateOf(emptyList<String>())}
    var groupQuery by remember(state.session?.userId,state.offlineAccount){mutableStateOf("")}
    var submitted by remember(state.session?.userId,state.offlineAccount){mutableStateOf(false)}
    var newChatMenu by remember{mutableStateOf(false)}

    val prefs=state.appearance;val warm=prefs.theme=="warm"
    val scheme=lightColorScheme(primary=if(warm)Color(0xffaa4c39)else Color(0xff285bc2),background=if(warm)Color(0xfff4ece7)else Color(0xffe8edf6),surface=if(warm)Color(0xfffffbf6)else Color(0xfff8faff),onSurface=if(warm)Color(0xff392c32)else Color(0xff17283f),onBackground=if(warm)Color(0xff392c32)else Color(0xff17283f),secondaryContainer=if(warm)Color(0xfff8ded2)else Color(0xffdae5ff))
    val typography=Typography(bodyLarge=Typography().bodyLarge.copy(fontSize=prefs.fontSize.sp),bodyMedium=Typography().bodyMedium.copy(fontSize=(prefs.fontSize-2).sp),titleLarge=Typography().titleLarge.copy(fontSize=(prefs.fontSize+6).sp),titleMedium=Typography().titleMedium.copy(fontSize=(prefs.fontSize+2).sp),labelLarge=Typography().labelLarge.copy(fontSize=(prefs.fontSize-2).sp))
    MaterialTheme(colorScheme=scheme,typography=typography) {
        val nav=rememberNavController();val entry by nav.currentBackStackEntryAsState();val page=entry?.destination?.route?:"Chat"
        val authenticated=state.session!=null||state.offlineAccount!=null
        val inConversation=page=="Chat"&&state.selected.isNotEmpty()
        val groupConversation=state.selected.takeIf{page=="Chat"&&state.groups.any{row->row.conversationId==it}}
        fun showSelector(target:String?){
            val pending=state.groupPending
            if(pending!=null){groupTarget=pending.conversation;groupSelection=pending.targets}else{groupTarget=target;groupSelection=emptyList();groupQuery="";submitted=false}
            groupPage="select"
        }
        fun closeGroup(){if(!state.groupBusy)groupPage=if(groupPage=="select"&&groupTarget!=null)"members" else ""}
        LaunchedEffect(state.groupSuccessRevision){if(submitted){submitted=false;groupPage="";nav.navigate("Chat"){launchSingleTop=true}}}
        BackHandler(enabled=groupPage.isNotEmpty()||inConversation){if(groupPage.isNotEmpty())closeGroup()else closeConversation()}
        if(!authenticated){Column(Modifier.fillMaxSize().background(scheme.background).statusBarsPadding().navigationBarsPadding().padding(20.dp)){
            state.error?.let{Text(displayText(LocalLanguage.current,it),color=scheme.error,modifier=Modifier.padding(vertical=8.dp))}
            Login(state,login,register,restore)
        };return@MaterialTheme}
        if(groupPage.isNotEmpty()){
            Column(Modifier.fillMaxSize().background(scheme.background).statusBarsPadding().navigationBarsPadding()){
                Row(Modifier.fillMaxWidth().padding(horizontal=12.dp),verticalAlignment=Alignment.CenterVertically){TextButton(onClick={closeGroup()},enabled=!state.groupBusy){Text("← "+t("group.cancel"))};Spacer(Modifier.weight(1f));Text("PlugWorldIM",style=MaterialTheme.typography.titleMedium)}
                if(groupPage=="select")Group(state,groupTarget,groupSelection,{groupSelection=it},groupQuery,{groupQuery=it},{closeGroup()},{ids,target->submitted=true;createGroup(ids,target)},{submitted=true;retryGroup()})
                else GroupMembers(state,groupTarget!!){showSelector(groupTarget)}
            }
            return@MaterialTheme
        }
        Scaffold(containerColor=scheme.background,topBar={Column(Modifier.fillMaxWidth().padding(horizontal=20.dp,vertical=10.dp)){Row(verticalAlignment=Alignment.CenterVertically){if(inConversation)TextButton(onClick=closeConversation,modifier=Modifier.semantics{contentDescription=t("nav.back")}){Text("←",fontSize=MaterialTheme.typography.labelLarge.fontSize*1.5f)};Text(if(inConversation)state.friends.find{it.directConversationId==state.selected}?.user?.displayName?:t("chat.conversation") else t("nav."+page.lowercase()),Modifier.weight(1f),style=MaterialTheme.typography.titleLarge);if(page=="Chat"&&!inConversation){Box{TextButton(onClick={newChatMenu=true}){Text("+ "+t("chat.new"))};DropdownMenu(expanded=newChatMenu,onDismissRequest={newChatMenu=false}){DropdownMenuItem(text={Text(t("friends.add"))},onClick={newChatMenu=false;nav.navigate("Friends"){launchSingleTop=true}});DropdownMenuItem(text={Text(t("group.create"))},enabled=state.session!=null,onClick={newChatMenu=false;showSelector(null)})}}}
                if(groupConversation!=null)IconButton(onClick={groupTarget=groupConversation;groupPage="members"},modifier=Modifier.semantics{contentDescription=t("group.members")}){Text("⋯")}
                Text(if(state.sync=="syncing")t("sync.syncing")else if(state.connection=="ready")t("connection.connected")else t("connection.offlineShort"),fontSize=12.sp,modifier=Modifier.padding(start=8.dp))}}},bottomBar={if(!inConversation)Navigation(page){p->nav.navigate(p){launchSingleTop=true;popUpTo("Chat"){saveState=true};restoreState=true}}}) {padding->
            Column(Modifier.fillMaxSize().padding(padding).padding(horizontal=if(page=="Chat"&&!inConversation)0.dp else 16.dp)) {
                state.error?.let{Surface(color=scheme.errorContainer,shape=RoundedCornerShape(12.dp),modifier=Modifier.fillMaxWidth().padding(bottom=12.dp)){Column(Modifier.padding(12.dp)){Text(displayText(LocalLanguage.current,it),color=scheme.onErrorContainer);if(state.session!=null || state.offlineAccount!=null)TextButton(onClick=reconnect,enabled=state.session!=null){Text(t("auth.reconnect"))}}}}
                NavHost(navController=nav,startDestination="Chat",modifier=Modifier.weight(1f)) {
                    composable("Chat"){if(state.session==null && state.offlineAccount==null)Login(state,login,register,restore)else Chat(state,open,reconnect,retry,send,draft,{draft=it})}
                    composable("Friends"){if(state.session==null && state.offlineAccount==null)Login(state,login,register,restore)else Friends(state,add,search){id->open(id);nav.navigate("Chat"){launchSingleTop=true}}}
                    composable("AI"){Future("✧",t("ai.title"),t("ai.description"),t("ai.detail"),prefs)}
                    composable("Plugin"){Future("⊞",t("plugin.workspace"),t("plugin.unavailable"),t("plugin.detail"),prefs)}
                    composable("Settings"){Settings(state,language,appearance,disconnect,logout,reconnect,refresh)}
                }
            }
        }
    }
}
