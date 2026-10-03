package im.platform.client.storage
// Internal storage models; canonical wire authority remains contracts/.
data class LocalMessage(val conversationId: String, val requestId: String, val senderId: String, val text: String)
data class ServerMessage(val conversationId: String, val requestId: String?, val senderId: String, val text: String,
    val messageId: String, val seq: Long, val createdAt: String)
data class Committed(val conversationId: String, val messageId: String, val seq: Long, val createdAt: String)
data class UserEvent(val kind: String, val subjectId: String, val revision: Long)
