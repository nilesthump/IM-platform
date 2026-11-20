package im.platform.tests.auth;
import im.platform.shared.authsupport.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.time.Instant;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

class CryptoTest {
    private final Tokens codec=new Tokens("test-only-signing-key-at-least-32-bytes".getBytes(StandardCharsets.UTF_8));
    private Tokens.Claims claims(long expiry){long now=Instant.now().getEpochSecond();return new Tokens.Claims(UUID.randomUUID().toString(),UUID.randomUUID().toString(),"WEB",1,now-1,expiry);}
    @Test void tokenRoundTripAndSignature()throws Exception {
        var c=claims(Instant.now().getEpochSecond()+900);String token=codec.sign(c);assertEquals(c,codec.parse(token));
        var other=new Tokens("different-test-only-signing-key-32bytes".getBytes(StandardCharsets.UTF_8));
        assertEquals("AUTH_TOKEN_INVALID",assertThrows(ApiFailure.class,()->other.parse(token)).code);
    }
    @Test void knownMalformedInputAndExpiry()throws Exception {
        for(String invalid:new String[]{"", "a.b.c", "a", "a.b.c.d"})assertEquals("AUTH_TOKEN_INVALID",assertThrows(ApiFailure.class,()->codec.parse(invalid)).code);
        long now=Instant.now().getEpochSecond();String expired=codec.sign(new Tokens.Claims(UUID.randomUUID().toString(),UUID.randomUUID().toString(),"WEB",1,now-20,now-1));
        assertEquals("AUTH_TOKEN_EXPIRED",assertThrows(ApiFailure.class,()->codec.parse(expired)).code);
    }
    @Test void fullPasswordNotTruncatedAndCorruptStorageFails(){
        String password="a".repeat(90)+"original";String hash=PasswordHash.create(password);
        assertTrue(hash.startsWith("$2a$10$"));assertTrue(PasswordHash.matches(password,hash));assertFalse(PasswordHash.matches("a".repeat(90)+"changed",hash));
        assertThrows(IllegalArgumentException.class,()->PasswordHash.matches(password,"malformed-persisted-hash"));
    }
    @Test void hashesUseCanonicalExistingMaterial(){assertEquals("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",Tokens.hash(""));assertEquals(43,Tokens.random().length());}
}
