package im.platform.client.ui
import androidx.compose.runtime.*
import androidx.activity.compose.BackHandler
import androidx.compose.ui.res.painterResource
import im.platform.client.R
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.*

@Composable fun Workspace(vm:WorkspaceViewModel=viewModel()) {
    val state by vm.state.collectAsStateWithLifecycle();val prefs=state.appearance;val warm=prefs.theme=="warm"
    val scheme=lightColorScheme(primary=if(warm)Color(0xffaa4c39)else Color(0xff285bc2),background=if(warm)Color(0xfff4ece7)else Color(0xffe8edf6),surface=if(warm)Color(0xfffffbf6)else Color(0xfff8faff),onSurface=if(warm)Color(0xff392c32)else Color(0xff17283f),onBackground=if(warm)Color(0xff392c32)else Color(0xff17283f),secondaryContainer=if(warm)Color(0xfff8ded2)else Color(0xffdae5ff))
    val typography=Typography(bodyLarge=Typography().bodyLarge.copy(fontSize=prefs.fontSize.sp),bodyMedium=Typography().bodyMedium.copy(fontSize=(prefs.fontSize-2).sp),titleLarge=Typography().titleLarge.copy(fontSize=(prefs.fontSize+6).sp),titleMedium=Typography().titleMedium.copy(fontSize=(prefs.fontSize+2).sp),labelLarge=Typography().labelLarge.copy(fontSize=(prefs.fontSize-2).sp))
    MaterialTheme(colorScheme=scheme,typography=typography) {
        val nav=rememberNavController();val entry by nav.currentBackStackEntryAsState();val page=entry?.destination?.route?:"Chat"
        val authenticated=state.session!=null||state.offlineAccount!=null
        val inConversation=page=="Chat"&&state.selected.isNotEmpty()
        BackHandler(enabled=inConversation){vm.closeConversation()}
        if(!authenticated){Column(Modifier.fillMaxSize().background(scheme.background).statusBarsPadding().navigationBarsPadding().padding(20.dp)){
            Row(verticalAlignment=Alignment.CenterVertically){Image(painterResource(R.drawable.project_logo),"IM+ logo",Modifier.size(56.dp));Text("IM+",fontSize=27.sp,fontWeight=FontWeight.ExtraBold,color=scheme.primary)}
            state.error?.let{Text(it,color=scheme.error,modifier=Modifier.padding(vertical=8.dp))}
            Login(state,vm)
        };return@MaterialTheme}
        Scaffold(containerColor=scheme.background,topBar={Column(Modifier.fillMaxWidth().padding(horizontal=20.dp,vertical=10.dp)){Row(verticalAlignment=Alignment.CenterVertically){Image(painterResource(R.drawable.project_logo),"IM+ logo",Modifier.size(40.dp));Text("IM+",fontSize=27.sp,fontWeight=FontWeight.ExtraBold,color=scheme.primary);Spacer(Modifier.weight(1f));TextButton(onClick={vm.appearance(prefs.copy(theme=if(warm)"cold" else "warm"))}){Text(if(warm)"Warm Creative" else "Cold AI")}};Row(verticalAlignment=Alignment.CenterVertically){if(inConversation)TextButton(onClick=vm::closeConversation){Text("← Chat")};Text(if(inConversation)state.friends.find{it.directConversationId==state.selected}?.user?.displayName?:"Conversation" else page,Modifier.weight(1f),style=MaterialTheme.typography.titleLarge);Text(if(state.sync=="syncing")"Syncing…"else if(state.connection=="ready")"Connected"else"Offline",fontSize=12.sp,modifier=Modifier.padding(start=8.dp))}}},bottomBar={if(!inConversation)NavigationBar{listOf("Chat","Friends","AI","Plugin","Settings").forEachIndexed {i,p->NavigationBarItem(selected=page==p,onClick={nav.navigate(p){launchSingleTop=true;popUpTo("Chat"){saveState=true};restoreState=true}},icon={Text(listOf("◫","♧","✧","⊞","⚙")[i])},label={Text(p,maxLines=1,fontSize=12.sp)})}}}) {padding->
            Column(Modifier.fillMaxSize().padding(padding).padding(horizontal=16.dp)) {
                state.error?.let{Surface(color=scheme.errorContainer,shape=RoundedCornerShape(12.dp),modifier=Modifier.fillMaxWidth().padding(bottom=12.dp)){Column(Modifier.padding(12.dp)){Text(it,color=scheme.onErrorContainer);if(state.session!=null || state.offlineAccount!=null)TextButton(onClick=vm::reconnect,enabled=state.session!=null){Text("Reconnect")}}}}
                NavHost(navController=nav,startDestination="Chat",modifier=Modifier.weight(1f)) {
                    composable("Chat"){if(state.session==null && state.offlineAccount==null)Login(state,vm)else Chat(state,vm)}
                    composable("Friends"){if(state.session==null && state.offlineAccount==null)Login(state,vm)else Friends(state,vm){id->vm.open(id);nav.navigate("Chat"){launchSingleTop=true}}}
                    composable("AI"){Future("✧","Intelligence, in conversation.","An AI space is planned for IM+. It is not available in this release.","No AI service is connected. Your conversations are not sent to an AI provider.",prefs)}
                    composable("Plugin"){Future("⊞","Your workspace, extended.","Plugin capabilities unavailable","No plugin runtime or installation service is connected in this release.",prefs)}
                    composable("Settings"){Settings(state,vm)}
                }
            }
        }
    }
}
@Composable private fun Panel(modifier:Modifier=Modifier,appearance:Appearance,content:@Composable ColumnScope.()->Unit){Surface(modifier=modifier,shape=RoundedCornerShape(20.dp),color=MaterialTheme.colorScheme.surface,border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant)){Column(Modifier.padding((20*appearance.density).dp),verticalArrangement=Arrangement.spacedBy((12*appearance.density).dp),content=content)}}
@Composable private fun Login(state:WorkspaceState,vm:WorkspaceViewModel) {
    var registering by remember{mutableStateOf(false)};var username by remember{mutableStateOf("")};var password by remember{mutableStateOf("")};var confirmation by remember{mutableStateOf("")}
    LaunchedEffect(state.registered){if(state.registered){registering=false;password="";confirmation=""}}
    Column(Modifier.fillMaxWidth().imePadding().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(14.dp)){
        Text("Stay close. Think beyond.",fontSize=(state.appearance.fontSize+10).sp,fontWeight=FontWeight.Bold)
        Panel(Modifier.fillMaxWidth(),state.appearance){
            Text(if(registering)"Create your account"else"Open your workspace",style=MaterialTheme.typography.titleLarge)
            if(state.registered&&!registering)Text("Account created. Sign in to continue.")
            OutlinedTextField(value=username,onValueChange={username=it},label={Text("Username")},singleLine=true,modifier=Modifier.fillMaxWidth())
            OutlinedTextField(value=password,onValueChange={password=it},label={Text("Password")},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth())
            if(registering){OutlinedTextField(value=confirmation,onValueChange={confirmation=it},label={Text("Confirm password")},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth());Text("Use 12–256 characters for your password.",style=MaterialTheme.typography.bodyMedium)}
            Button(onClick={if(registering)vm.register(username,password,confirmation)else{vm.login(state.endpoint,username,password);password=""}},enabled=!state.busy&&username.isNotEmpty()&&password.isNotEmpty()&&(!registering||confirmation.isNotEmpty()),modifier=Modifier.fillMaxWidth()){Text(if(state.busy)"Please wait…"else if(registering)"Create account"else"Sign in")}
            TextButton(onClick={registering=!registering;password="";confirmation=""},enabled=!state.busy,modifier=Modifier.fillMaxWidth()){Text(if(registering)"Already have an account? Sign in"else"New here? Create an account")}
            if(!registering)TextButton(onClick={vm.restore(state.endpoint)},enabled=!state.busy,modifier=Modifier.fillMaxWidth()){Text("Resume saved session")}
        }
    }
}
@Composable private fun Chat(state:WorkspaceState,vm:WorkspaceViewModel) {
    if(state.selected.isEmpty()){
        LazyColumn(Modifier.fillMaxSize(),verticalArrangement=Arrangement.spacedBy(8.dp)){
            if(state.conversations.isEmpty())item{Panel(Modifier.fillMaxWidth(),state.appearance){Text("Your next conversation starts here",style=MaterialTheme.typography.titleLarge);Text("Find a friend to open a private chat.")}}
            items(state.conversations,key={it}){id->Surface(onClick={vm.open(id)},shape=RoundedCornerShape(16.dp),color=MaterialTheme.colorScheme.surface,modifier=Modifier.fillMaxWidth()){
                Column(Modifier.padding((16*state.appearance.density).dp)){Text(state.friends.find{it.directConversationId==id}?.user?.displayName?:"Conversation "+id.take(8),fontWeight=FontWeight.SemiBold);Text(if(state.unavailable.contains(id))"Access unavailable"else state.previews[id]?.text?:"No messages yet",maxLines=1,style=MaterialTheme.typography.bodyMedium)}
            }}
        };return
    }
    var draft by remember(state.session?.userId){mutableStateOf("")};val selected=state.friends.find{it.directConversationId==state.selected};val spacing=(10*state.appearance.density).dp
    Column(Modifier.fillMaxSize(),verticalArrangement=Arrangement.spacedBy(spacing)){
        if(state.conversations.isEmpty()){Panel(Modifier.fillMaxWidth(),state.appearance){Text("Your next conversation starts here",style=MaterialTheme.typography.titleLarge);Text("Find a friend to open a private chat.")}}else {
            Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(selected?.user?.displayName?:"Conversation",style=MaterialTheme.typography.titleMedium);Text(if(state.connection=="ready")"Messages sync automatically"else"Offline · Showing saved history",style=MaterialTheme.typography.bodyMedium)};TextButton(onClick=vm::reconnect,enabled=state.session!=null){Text("Reconnect")}}
        }
        LazyColumn(Modifier.weight(1f).fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(spacing)) {
            if(state.messages.isEmpty())item{Column(Modifier.fillMaxWidth().padding(35.dp),horizontalAlignment=Alignment.CenterHorizontally){Text(if(state.selected.isEmpty())"Good conversations have a place"else"A fresh start",style=MaterialTheme.typography.titleMedium);Text(if(state.selected.isEmpty())"Choose a conversation to begin."else"No messages yet. Say hello.",style=MaterialTheme.typography.bodyMedium)}}
            items(state.messages){m->val own=m[1]==(state.session?.userId?:state.offlineAccount);Column(Modifier.fillMaxWidth(),horizontalAlignment=if(own)Alignment.End else Alignment.Start){Surface(color=if(own)MaterialTheme.colorScheme.secondaryContainer else MaterialTheme.colorScheme.surface,shape=RoundedCornerShape(14.dp),modifier=Modifier.widthIn(max=310.dp)){Text(m[2]?:"",modifier=Modifier.padding((14*state.appearance.density).dp))};Row(verticalAlignment=Alignment.CenterVertically){Text(when(m[3]){"SENT"->"Sent";"SENDING"->"Sending…";else->"Failed"},style=MaterialTheme.typography.bodyMedium);if(own&&m[3]=="FAILED"&&m[0]!=null)TextButton(onClick={vm.retry(m[0]!!)},enabled=state.session!=null){Text("Retry")}}}}
        }
        Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(8.dp)){OutlinedTextField(value=draft,onValueChange={if(it.codePointCount(0,it.length)<=4096)draft=it},label={Text("Message")},modifier=Modifier.weight(1f),enabled=state.selected.isNotEmpty()&&state.session!=null,maxLines=3);Button(onClick={vm.send(draft);draft=""},enabled=state.selected.isNotEmpty()&&state.session!=null&&draft.isNotBlank()){Text("Send ↑")}};Spacer(Modifier.height(5.dp))
    }
}
@Composable private fun Friends(state:WorkspaceState,vm:WorkspaceViewModel,open:(String)->Unit) {
    var query by remember{mutableStateOf("")}
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){
        Panel(Modifier.fillMaxWidth(),state.appearance){Text("People, within reach.",style=MaterialTheme.typography.titleLarge);Text("Find someone by their exact username.",style=MaterialTheme.typography.bodyMedium);OutlinedTextField(value=query,onValueChange={query=it},label={Text("Username")},singleLine=true,modifier=Modifier.fillMaxWidth());Button(onClick={vm.search(query)},enabled=state.session!=null&&!state.busy&&query.isNotBlank()){Text(if(state.busy)"Searching…"else"Search")};state.results.forEach{u->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(u.displayName,fontWeight=FontWeight.SemiBold);Text("@"+u.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={vm.add(u.userId)},enabled=state.session!=null&&u.userId!=state.session?.userId&&!state.busy){Text("Add friend")}}};if(query.isNotEmpty() && state.results.isEmpty() && !state.busy)Text("No matching user shown.",style=MaterialTheme.typography.bodyMedium)}
        Panel(Modifier.fillMaxWidth(),state.appearance){Text("Your friends",style=MaterialTheme.typography.titleLarge);if(state.friends.isEmpty())Text("Your circle is waiting to grow.");state.friends.forEach{f->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(f.user.displayName,fontWeight=FontWeight.SemiBold);Text("@"+f.user.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={open(f.directConversationId)}){Text("Message")}}}}
    }
}
@Composable private fun Future(symbol:String,title:String,description:String,detail:String,prefs:Appearance){Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){Panel(Modifier.fillMaxWidth(),prefs){Text(symbol,fontSize=60.sp,color=MaterialTheme.colorScheme.primary);Text(title,style=MaterialTheme.typography.titleLarge);Text(description);AssistChip(onClick={},label={Text("Coming later")});Text(detail,style=MaterialTheme.typography.bodyMedium)}}}
@OptIn(ExperimentalLayoutApi::class)
@Composable private fun Settings(state:WorkspaceState,vm:WorkspaceViewModel){val p=state.appearance;Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){
    Panel(Modifier.fillMaxWidth(),p){Text("Appearance",style=MaterialTheme.typography.titleLarge);Text("Color, type and spacing are independent.",style=MaterialTheme.typography.bodyMedium);FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){listOf("cold","warm").forEach{theme->FilterChip(selected=p.theme==theme,onClick={vm.appearance(p.copy(theme=theme))},label={Text(if(theme=="cold")"Cold AI"else"Warm Creative")})}};Row(verticalAlignment=Alignment.CenterVertically){Text("Font size: ${p.fontSize}px",Modifier.weight(1f));OutlinedButton(onClick={vm.appearance(p.copy(fontSize=p.fontSize-1))},enabled=p.fontSize>14){Text("−")};Spacer(Modifier.width(8.dp));OutlinedButton(onClick={vm.appearance(p.copy(fontSize=p.fontSize+1))},enabled=p.fontSize<22){Text("+")}};Text("Spacing");FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){listOf(.8f,1f,1.2f).forEachIndexed{i,d->FilterChip(selected=kotlin.math.abs(p.density-d)<.01f,onClick={vm.appearance(p.copy(density=d))},label={Text(listOf("Compact","Standard","Comfort")[i],fontSize=12.sp)})}};Text("Saved on this device. Switching themes preserves type and spacing.",style=MaterialTheme.typography.bodyMedium)}
    Panel(Modifier.fillMaxWidth(),p){Text("Profile & session",style=MaterialTheme.typography.titleLarge);Text(state.profile?.displayName?:"Profile unavailable",fontWeight=FontWeight.SemiBold);Text(state.profile?.let{"@"+it.username}?:(if(state.session!=null)"Reconnect to load your profile"else"Sign in to load your profile"));FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){OutlinedButton(onClick=vm::refresh,enabled=!state.busy&&(state.session!=null||state.offlineAccount!=null)){Text("Refresh session")};OutlinedButton(onClick=vm::disconnect,enabled=state.session!=null){Text("Go offline")}};FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){OutlinedButton(onClick=vm::reconnect,enabled=state.session!=null){Text("Reconnect")};Button(onClick=vm::logout,enabled=!state.busy&&(state.session!=null||state.offlineAccount!=null)){Text("Sign out")}}}
}}
