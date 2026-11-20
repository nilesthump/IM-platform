package im.platform.shared.authsupport;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Map;

public final class Tokens {
    private static final ObjectMapper JSON=new ObjectMapper();
    private static final Base64.Encoder ENCODER=Base64.getUrlEncoder().withoutPadding();
    private static final String HEADER=ENCODER.encodeToString("{\"alg\":\"HS256\",\"typ\":\"JWT\"}".getBytes(StandardCharsets.UTF_8));
    private final byte[] key;
    public record Claims(String userId,String sessionId,String clientType,long epoch,long issued,long expires) {}
    public Tokens(byte[] key){this.key=key.clone();}
    public static boolean validClient(String t){return "WEB".equals(t)||"DESKTOP".equals(t)||"MOBILE".equals(t);}
    public static String hash(String value){
        try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException error){throw new IllegalStateException(error);}
    }
    public static String random(){byte[] b=new byte[32];new SecureRandom().nextBytes(b);return ENCODER.encodeToString(b);}
    private byte[] mac(String data){
        try{Mac m=Mac.getInstance("HmacSHA256");m.init(new SecretKeySpec(key,"HmacSHA256"));return m.doFinal(data.getBytes(StandardCharsets.UTF_8));}
        catch(java.security.GeneralSecurityException error){throw new IllegalStateException(error);}
    }
    public String sign(Claims c)throws java.io.IOException {
        String body=HEADER+"."+ENCODER.encodeToString(JSON.writeValueAsBytes(Map.of("user_id",c.userId(),"session_id",c.sessionId(),"client_type",c.clientType(),"session_epoch",c.epoch(),"iat",c.issued(),"exp",c.expires())));
        return body+"."+ENCODER.encodeToString(mac(body));
    }
    private static ApiFailure invalid(){return new ApiFailure(401,"AUTH_TOKEN_INVALID","Access token is invalid.");}
    public Claims parse(String token){
        String[] p=token.split("\\.",-1);if(p.length!=3||!HEADER.equals(p[0]))throw invalid();
        byte[] sig,raw;
        try{sig=Base64.getUrlDecoder().decode(p[2]);raw=Base64.getUrlDecoder().decode(p[1]);}
        catch(IllegalArgumentException malformed){throw invalid();}
        if(!MessageDigest.isEqual(sig,mac(p[0]+"."+p[1])))throw invalid();
        JsonNode b;try{b=JSON.readTree(raw);}
        catch(com.fasterxml.jackson.core.JsonProcessingException malformed){throw invalid();}
        catch(java.io.IOException internal){throw new java.io.UncheckedIOException(internal);}
        if(b==null||!b.isObject())throw invalid();
        for(String f:new String[]{"user_id","session_id","client_type"})if(!b.path(f).isTextual()||b.path(f).textValue().isEmpty())throw invalid();
        for(String f:new String[]{"session_epoch","iat","exp"})if(!b.path(f).isIntegralNumber()||!b.path(f).canConvertToLong())throw invalid();
        Claims c=new Claims(b.get("user_id").textValue(),b.get("session_id").textValue(),b.get("client_type").textValue(),b.get("session_epoch").longValue(),b.get("iat").longValue(),b.get("exp").longValue());
        if(!c.userId().matches("[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")||!c.sessionId().matches("[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"))throw invalid();
        if(!validClient(c.clientType())||c.epoch()<1||c.issued()<1||c.expires()<=c.issued())throw invalid();
        if(java.time.Instant.now().getEpochSecond()>=c.expires())throw new ApiFailure(401,"AUTH_TOKEN_EXPIRED","Access token has expired.");
        return c;
    }
}
