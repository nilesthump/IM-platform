package im.platform.client.send
import java.io.BufferedInputStream
import java.io.Closeable
import java.net.URI
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64
import javax.net.ssl.SSLSocket
import javax.net.ssl.SSLSocketFactory

interface SendSocket: Closeable { fun send(text: String) }
// Android's standard TLS socket plus the narrow RFC6455 text/control framing
// needed here. Platform trust and HTTPS hostname verification are mandatory.
class Wss(endpoint: String, private val opened: ()->Unit, private val message:(String)->Unit, private val ended:()->Unit,
    private val tls: SSLSocketFactory=SSLSocketFactory.getDefault() as SSLSocketFactory): SendSocket {
    private val uri=URI(endpoint)
    @Volatile private var closed=false
    @Volatile private var socket: SSLSocket?=null
    private val random=SecureRandom()
    init {
        require(uri.scheme=="wss" && uri.host!=null && uri.rawQuery==null && uri.rawFragment==null && uri.rawUserInfo==null) { "Invalid WSS endpoint" }
        Thread({
            try {
                val s=tls.createSocket(uri.host,if(uri.port<0) 443 else uri.port) as SSLSocket
                socket=s; if(closed) { s.close(); return@Thread }
                s.soTimeout=15000
                val parameters=s.sslParameters; parameters.endpointIdentificationAlgorithm="HTTPS"; s.sslParameters=parameters; s.startHandshake()
                val input=BufferedInputStream(s.inputStream)
                val key=Base64.getEncoder().encodeToString(ByteArray(16).also(random::nextBytes))
                val host=uri.host+(if(uri.port<0) "" else ":${uri.port}")
                val path=uri.rawPath.ifEmpty { "/" }
                val header="GET $path HTTP/1.1\r\nHost: $host\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: $key\r\nSec-WebSocket-Version: 13\r\n\r\n"
                s.outputStream.write(header.toByteArray(Charsets.US_ASCII)); s.outputStream.flush()
                val bytes=ArrayList<Byte>(); while(bytes.size<16384) { val b=input.read(); require(b>=0); bytes.add(b.toByte()); if(bytes.size>=4 && bytes.takeLast(4)==listOf(13.toByte(),10.toByte(),13.toByte(),10.toByte())) break }
                val lines=bytes.toByteArray().toString(Charsets.US_ASCII).split("\r\n")
                require(lines.first().matches(Regex("HTTP/1\\.[01] 101(?: .*)?")))
                val headers=mutableMapOf<String,String>()
                lines.drop(1).filter { it.isNotEmpty() }.forEach { val parts=it.split(':',limit=2); require(parts.size==2); val name=parts[0].lowercase(); require(!headers.containsKey(name)); headers[name]=parts[1].trim() }
                val accept=Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-1").digest((key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").toByteArray(Charsets.US_ASCII)))
                require(headers["sec-websocket-accept"]==accept && headers["upgrade"]?.lowercase()=="websocket" && headers["connection"]?.split(',')?.any { it.trim().equals("upgrade",true) }==true)
                require(headers["sec-websocket-extensions"]==null && headers["sec-websocket-protocol"]==null)
                s.soTimeout=0; if(closed) return@Thread; opened()
                val fragments=java.io.ByteArrayOutputStream(); var fragmented=false
                fun read(): Int { val b=input.read(); require(b>=0); return b }
                while(!closed) {
                    val first=read(); val second=read(); require(first and 0x70==0 && second and 0x80==0)
                    val fin=first and 0x80!=0; val op=first and 15
                    var length=(second and 127).toLong()
                    if(length==126L) length=((read() shl 8) or read()).toLong()
                    else if(length==127L) { length=0; repeat(8) { val b=read(); require(length<=131072); length=(length shl 8) or b.toLong() } }
                    require(length<=131072 && (op<8 || (fin && length<=125)))
                    val body=ByteArray(length.toInt()); var n=0; while(n<body.size) { val count=input.read(body,n,body.size-n); require(count>0); n+=count }
                    when(op) {
                        8 -> break
                        9 -> frame(10,body)
                        10 -> Unit
                        1,0 -> {
                            require((op==1 && !fragmented) || (op==0 && fragmented)); require(fragments.size()+body.size<=131072)
                            fragments.write(body); fragmented=!fin
                            if(fin) { val decoder=Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT); message(decoder.decode(ByteBuffer.wrap(fragments.toByteArray())).toString()); fragments.reset() }
                        }
                        else -> error("Invalid WSS frame")
                    }
                }
            } catch(_: Exception) { /* No endpoint, token, or frame in exceptions. */ }
            finally { close(); ended() }
        },"im-wss").apply { isDaemon=true; start() }
    }
    @Synchronized private fun frame(op: Int,body: ByteArray) {
        check(!closed); val s=socket ?: error("WSS unavailable")
        val output=s.outputStream; val bytes=java.io.ByteArrayOutputStream(); bytes.write(0x80 or op)
        when { body.size<126 -> bytes.write(0x80 or body.size); body.size<=65535 -> {bytes.write(0x80 or 126); bytes.write(body.size ushr 8); bytes.write(body.size and 255)}
            else -> {bytes.write(0x80 or 127); repeat(4) {bytes.write(0)}; for(shift in listOf(24,16,8,0)) bytes.write(body.size ushr shift and 255)} }
        val mask=ByteArray(4).also(random::nextBytes); bytes.write(mask)
        bytes.write(ByteArray(body.size) { (body[it].toInt() xor mask[it%4].toInt()).toByte() }); output.write(bytes.toByteArray()); output.flush()
    }
    override fun send(text: String) { frame(1,text.toByteArray(Charsets.UTF_8)) }
    override fun close() { closed=true; try { socket?.close() } catch(_:Exception) {} }
}
