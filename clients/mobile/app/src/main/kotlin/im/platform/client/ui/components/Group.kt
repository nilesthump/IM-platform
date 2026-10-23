package im.platform.client.ui.components
import androidx.compose.runtime.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import im.platform.client.ui.WorkspaceState
import im.platform.client.ui.i18n.useText
@Composable fun Group(state:WorkspaceState,conversation:String?,close:()->Unit,submit:(List<String>,String?)->Unit,retry:()->Unit){
 val t=useText();var selection by remember(state.session?.userId,conversation){mutableStateOf(emptyList<String>())}
 AlertDialog(onDismissRequest=close,title={Text(t(if(conversation==null)"group.create"else"group.add"))},text={LazyColumn(Modifier.heightIn(max=420.dp)){
  if(state.friends.isEmpty())item{Text(t("group.empty"))}
  items(state.friends,key={"friend:"+it.user.userId}){friend->Row{Checkbox(checked=friend.user.userId in selection,enabled=!state.groupBusy&&state.groupStatus!="unconfirmed",onCheckedChange={checked->selection=if(checked)selection+friend.user.userId else selection-friend.user.userId});Text(friend.user.displayName+" @"+friend.user.username)}}
  if(state.groupStatus.isNotEmpty())item{Text(t("group."+state.groupStatus))}
  if(state.groupError.isNotEmpty())item{Text(t(if(state.groupError=="GROUP_REQUEST_CONFLICT")"group.conflict"else"group.failure"))}
  if(conversation!=null){item{Text(t("group.members"))};items(state.groups.filter{it.conversationId==conversation},key={"member:"+it.user.userId}){Text(it.user.displayName+" @"+it.user.username)}}
 }},confirmButton={if(state.groupStatus=="unconfirmed")TextButton(onClick=retry,enabled=!state.groupBusy&&state.session!=null){Text(t("group.retry"))}else TextButton(onClick={submit(selection,conversation)},enabled=selection.size in 1..100&&!state.groupBusy&&state.session!=null){Text(t(if(conversation==null)"group.create"else"group.add"))}},dismissButton={TextButton(onClick=close){Text(t("nav.back"))}})
}