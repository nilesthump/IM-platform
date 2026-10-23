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
import androidx.compose.ui.unit.Dp
internal fun messageBody(row:List<String?>):String=checkNotNull(row[2]){"Message content missing"}
internal fun messageIdentity(row:List<String?>):String=row[0]?:row[4]?:error("Message identity missing")
internal fun messageState(value:String?):String=when(value){"SENT"->"chat.sent";"SENDING"->"chat.sending";"FAILED"->"chat.failed";else->error("Unknown message state")}
@Composable fun Messages(state:WorkspaceState,spacing:Dp,retry:(String)->Unit,modifier:Modifier){
    val t=useText()
LazyColumn(modifier.fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(spacing)) {
            if(state.messages.isEmpty())item{Column(Modifier.fillMaxWidth().padding(35.dp),horizontalAlignment=Alignment.CenterHorizontally){Text(if(state.selected.isEmpty())t("chat.place")else t("chat.fresh"),style=MaterialTheme.typography.titleMedium);Text(if(state.selected.isEmpty())t("chat.choose")else t("chat.hello"),style=MaterialTheme.typography.bodyMedium)}}
            items(state.messages,key={messageIdentity(it)}){m->val own=m[1]==(state.session?.userId?:state.offlineAccount);Column(Modifier.fillMaxWidth(),horizontalAlignment=if(own)Alignment.End else Alignment.Start){val member=state.groups.find{it.conversationId==state.selected&&it.user.userId==m[1]}?.user;Text(if(member!=null)member.displayName+" @"+member.username else m[1]?:"",style=MaterialTheme.typography.bodySmall);Surface(color=if(own)MaterialTheme.colorScheme.secondaryContainer else MaterialTheme.colorScheme.surface,shape=RoundedCornerShape(14.dp),modifier=Modifier.widthIn(max=310.dp)){Text(messageBody(m),modifier=Modifier.padding((14*state.appearance.density).dp))};Row(verticalAlignment=Alignment.CenterVertically){Text(t(messageState(m[3])),style=MaterialTheme.typography.bodyMedium);if(own&&m[3]=="FAILED"&&m[0]!=null)TextButton(onClick={retry(m[0]!!)},enabled=state.session!=null){Text(t("chat.retry"))}}}}
        }}
