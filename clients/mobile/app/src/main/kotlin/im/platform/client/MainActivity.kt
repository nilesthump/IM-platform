package im.platform.client
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import im.platform.client.ui.Workspace
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        actionBar?.hide()
        setContent { Workspace() }
    }
}
