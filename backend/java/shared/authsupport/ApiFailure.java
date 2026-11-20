package im.platform.shared.authsupport;
/** Known canonical rejection, never an internal-failure fallback. */
public final class ApiFailure extends RuntimeException {
    public final int status;
    public final String code, publicMessage;
    public ApiFailure(int status,String code,String message){super(code);this.status=status;this.code=code;this.publicMessage=message;}
}
