package im.platform.core.im;

import im.platform.shared.authsupport.ApiFailure;
import java.io.*;

/** Bounds the JSON buffer while retaining the exact integrality and capped value of every number. */
final class SyncInput {
    private final BufferedInputStream source;
    private int next;
    SyncInput(InputStream input) { source=new BufferedInputStream(input); }
    private void advance() throws IOException { next=source.read(); }
    private static boolean digit(int ch) { return ch>='0' && ch<='9'; }
    private static ApiFailure invalid(){return new ApiFailure(400,"VALIDATION_FAILED","Invalid Sync JSON.");}
    byte[] normalized() throws IOException {
        var result=new ByteArrayOutputStream();
        boolean quoted=false,escaped=false,space=false;
        advance();
        while(next!=-1) {
            if(quoted) {
                result.write(next);
                if(escaped) escaped=false;
                else if(next=='\\') escaped=true;
                else if(next=='"') quoted=false;
                advance();
            } else if(next==' ' || next=='\t' || next=='\n' || next=='\r') {
                if(!space) result.write(' ');
                space=true;
                advance();
            } else {
                space=false;
                if(digit(next) || next=='-') result.writeBytes(number().getBytes(java.nio.charset.StandardCharsets.US_ASCII));
                else {quoted=next=='"';result.write(next);advance();}
            }
            if(result.size()>65536) throw invalid();
        }
        return result.toByteArray();
    }
    private String number() throws IOException {
        boolean negative=next=='-';
        if(negative) advance();
        if(!digit(next)) throw invalid();
        var prefix=new StringBuilder(19);
        long digits=0,trailing=0,fraction=0;
        boolean initialZero=next=='0',decimal=false;
        do {
            if(next=='.') {
                if(decimal) throw invalid();
                decimal=true;
                advance();
                if(!digit(next)) throw invalid();
            }
            if(decimal) fraction++;
            if(digits>0 || next!='0') {
                digits++;
                if(prefix.length()<19) prefix.append((char)next);
                trailing=next=='0'?trailing+1:0;
            }
            advance();
            if(initialZero && !decimal && digit(next)) throw invalid();
        } while(digit(next)||next=='.');
        boolean minus=false;
        long exponent=0;
        if(next=='e'||next=='E') {
            advance();
            if(next=='-'||next=='+'){minus=next=='-';advance();}
            if(!digit(next)) throw invalid();
            while(digit(next)){
                int d=next-'0';
                exponent=exponent>(Long.MAX_VALUE-d)/10?Long.MAX_VALUE:exponent*10+d;
                advance();
            }
        }
        if(digits==0) return "0";
        if(negative) return "-1";
        if(minus && exponent>trailing) return "0.5";
        long shift=(minus?-exponent:exponent)-fraction;
        if(shift<0 && -shift>trailing) return "0.5";
        if(shift>19-digits) return Long.toString(Long.MAX_VALUE);
        int count=(int)(digits+shift);
        String bounded=prefix.substring(0,Math.min(count,prefix.length()))+"0".repeat(Math.max(0,count-prefix.length()));
        return count==19 && bounded.compareTo("9223372036854775807")>0?"9223372036854775807":bounded;
    }
}
