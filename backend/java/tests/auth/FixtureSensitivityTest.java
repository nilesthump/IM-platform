package im.platform.tests.auth;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FixtureSensitivityTest {
    @Test void expectedStatusAndErrorMutationAreDetected()throws Exception{
        var expected=AuthFixtureRunner.JSON.readTree("{\"error\":{\"code\":\"AUTH_REQUIRED\"},\"status\":401}");
        var normalizer=new AuthFixtureRunner.Normalize("alice");
        normalizer.check(expected,expected,"body");
        var wrong=expected.deepCopy();((com.fasterxml.jackson.databind.node.ObjectNode)wrong).put("status",200);
        assertThrows(AssertionError.class,()->normalizer.check(expected,wrong,"body"));
        var wrongError=expected.deepCopy();((com.fasterxml.jackson.databind.node.ObjectNode)wrongError.get("error")).put("code","AUTH_TOKEN_INVALID");
        assertThrows(AssertionError.class,()->normalizer.check(expected,wrongError,"body"));
    }
}
