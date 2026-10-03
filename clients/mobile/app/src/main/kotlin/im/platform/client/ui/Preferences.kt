package im.platform.client.ui
import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import java.util.Base64
data class Appearance(val theme:String="cold",val fontSize:Int=16,val density:Float=1f)
class Preferences(context:Context) {
    private val appearance=context.getSharedPreferences("appearance",Context.MODE_PRIVATE)
    private val credentials=context.getSharedPreferences("secure-refresh",Context.MODE_PRIVATE)
    fun loadAppearance():Appearance {val value=Appearance(appearance.getString("theme","cold")!!,appearance.getInt("fontSize",16),appearance.getFloat("density",1f));validate(value);return value}
    private fun validate(v:Appearance){require(v.theme in listOf("cold","warm") && v.fontSize in 14..22 && listOf(.8f,1f,1.2f).any {kotlin.math.abs(v.density-it)<.001f})}
    fun saveAppearance(v:Appearance){validate(v);check(appearance.edit().putString("theme",v.theme).putInt("fontSize",v.fontSize).putFloat("density",v.density).commit())}
    private fun key():SecretKey {
        val store=KeyStore.getInstance("AndroidKeyStore");store.load(null);(store.getKey("im-platform-refresh",null) as? SecretKey)?.let {return it}
        val generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");generator.init(KeyGenParameterSpec.Builder("im-platform-refresh",KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).setRandomizedEncryptionRequired(true).build());return generator.generateKey()
    }
    @Synchronized fun write(slot:String,value:String){require(slot.length<=256 && value.length<=8192);val cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key());cipher.updateAAD(slot.toByteArray());val ciphertext=cipher.doFinal(value.toByteArray());check(credentials.edit().putString(slot,Base64.getEncoder().encodeToString(cipher.iv)+":"+Base64.getEncoder().encodeToString(ciphertext)).commit())}
    @Synchronized fun read(slot:String):String? {val saved=credentials.getString(slot,null)?:return null;val parts=saved.split(':');require(parts.size==2);val cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(),GCMParameterSpec(128,Base64.getDecoder().decode(parts[0])));cipher.updateAAD(slot.toByteArray());return cipher.doFinal(Base64.getDecoder().decode(parts[1])).toString(Charsets.UTF_8)}
    @Synchronized fun remove(slot:String){check(credentials.edit().remove(slot).commit())}
}
