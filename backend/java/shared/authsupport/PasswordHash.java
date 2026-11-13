package im.platform.shared.authsupport;
import org.springframework.security.crypto.bcrypt.BCrypt;
public final class PasswordHash {
    private PasswordHash() {}
    public static String create(String password){return BCrypt.hashpw(Tokens.hash("im-password-v1:"+password),BCrypt.gensalt(10));}
    public static boolean matches(String password,String stored){return BCrypt.checkpw(Tokens.hash("im-password-v1:"+password),stored);}
}
