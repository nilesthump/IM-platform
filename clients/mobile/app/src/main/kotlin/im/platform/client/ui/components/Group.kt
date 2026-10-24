package im.platform.client.ui.components

import androidx.compose.runtime.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import im.platform.client.ui.WorkspaceState
import im.platform.client.ui.i18n.useText

@Composable private fun GroupAvatar(name:String){
 Surface(shape=CircleShape,color=MaterialTheme.colorScheme.secondaryContainer,modifier=Modifier.size(36.dp)){
  Box(contentAlignment=Alignment.Center){Text(name.take(1))}
 }
}

@Composable fun Group(state:WorkspaceState,conversation:String?,selection:List<String>,select:(List<String>)->Unit,query:String,search:(String)->Unit,close:()->Unit,submit:(List<String>,String?)->Unit,retry:()->Unit){
 val t=useText()
 val locked=state.groupBusy||state.groupStatus=="unconfirmed"
 val friends=state.friends.filter{query.isBlank()||it.user.displayName.contains(query,true)||it.user.username.contains(query,true)||it.user.userId.contains(query,true)}
 Column(Modifier.fillMaxSize().padding(12.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
  Text(t(if(conversation==null)"group.create" else "group.add"),style=MaterialTheme.typography.titleLarge)
  Row(Modifier.weight(1f),horizontalArrangement=Arrangement.spacedBy(12.dp)){
   Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(8.dp)){
    OutlinedTextField(value=query,onValueChange=search,label={Text(t("group.search"))},singleLine=true,modifier=Modifier.fillMaxWidth())
    Text(t("friends.your"),style=MaterialTheme.typography.titleMedium)
    LazyColumn(Modifier.weight(1f)){
     if(state.friends.isEmpty())item{Text(t("group.empty"))}
     items(friends,key={"friend:"+it.user.userId}){friend->
      Row(Modifier.fillMaxWidth().padding(vertical=8.dp),verticalAlignment=Alignment.CenterVertically){
       Checkbox(modifier=Modifier.semantics{contentDescription=friend.user.displayName},checked=friend.user.userId in selection,enabled=!locked,onCheckedChange={checked->select(if(checked)selection+friend.user.userId else selection-friend.user.userId)})
       Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(4.dp)){GroupAvatar(friend.user.userId);Text(friend.user.displayName);Text("@"+friend.user.username,style=MaterialTheme.typography.bodySmall)}
      }
     }
    }
   }
   VerticalDivider()
   Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(8.dp)){
    Text(t("group.selected")+" ("+selection.size+")",style=MaterialTheme.typography.titleMedium)
    LazyColumn(Modifier.weight(1f)){
     items(selection,key={"selected:"+it}){id->
      val friend=state.friends.find{it.user.userId==id}
      Column(Modifier.fillMaxWidth().padding(vertical=8.dp)){
       Row(verticalAlignment=Alignment.CenterVertically){GroupAvatar(id);Spacer(Modifier.weight(1f));IconButton(onClick={select(selection-id)},enabled=!locked,modifier=Modifier.semantics{contentDescription=t("group.remove")}){Text("×")}}
       Text(friend?.user?.displayName?:id)
      }
     }
    }
   }
  }
  if(state.groupBusy||state.groupStatus=="unconfirmed"||state.groupStatus=="rejected")Text(t(if(state.groupBusy)"group.loading" else "group."+state.groupStatus))
  if(state.groupError.isNotEmpty())Text(t(if(state.groupError=="GROUP_REQUEST_CONFLICT")"group.conflict" else "group.failure"),color=MaterialTheme.colorScheme.error)
  Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.End){
   TextButton(onClick=close,enabled=!state.groupBusy){Text(t("group.cancel"))}
   Spacer(Modifier.width(8.dp))
   if(state.groupStatus=="unconfirmed")Button(onClick=retry,enabled=!state.groupBusy&&state.session!=null){Text(t("group.retry"))}
   else Button(onClick={submit(selection,conversation)},enabled=selection.size in 1..100&&!state.groupBusy&&state.session!=null){Text(t("group.confirm"))}
  }
 }
}

@Composable fun GroupMembers(state:WorkspaceState,conversation:String,add:()->Unit){
 val t=useText()
 Column(Modifier.fillMaxSize().padding(16.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){
  Text(t("group.title"),style=MaterialTheme.typography.titleLarge)
  Text(conversation,style=MaterialTheme.typography.bodySmall)
  Row(verticalAlignment=Alignment.CenterVertically){Text(t("group.members"),Modifier.weight(1f),style=MaterialTheme.typography.titleMedium);TextButton(onClick=add,enabled=state.session!=null&&!state.groupBusy){Text("+ "+t("group.add"))}}
  LazyColumn(Modifier.weight(1f)){
   items(state.groups.filter{it.conversationId==conversation},key={"member:"+it.user.userId}){member->
    Row(Modifier.fillMaxWidth().padding(vertical=10.dp),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.CenterVertically){GroupAvatar(member.user.userId);Column(Modifier.weight(1f)){Text(member.user.displayName);Text(member.user.userId,style=MaterialTheme.typography.bodySmall)}}
   }
  }
 }
}
