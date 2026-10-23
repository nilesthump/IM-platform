package im.platform.client.ui
import androidx.compose.runtime.*
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import im.platform.client.ui.components.Shell
import im.platform.client.ui.i18n.LocalLanguage

@Composable fun Workspace(vm:WorkspaceViewModel=viewModel()){
    val state by vm.state.collectAsStateWithLifecycle()
    CompositionLocalProvider(LocalLanguage provides state.language){Shell(state,createGroup=vm::createGroup,retryGroup=vm::retryGroup,language=vm::language,add=vm::add,appearance=vm::appearance,closeConversation=vm::closeConversation,disconnect=vm::disconnect,login=vm::login,logout=vm::logout,open=vm::open,reconnect=vm::reconnect,refresh=vm::refresh,register=vm::register,restore=vm::restore,retry=vm::retry,search=vm::search,send=vm::send)}
}
