package im.platform.tests.im;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.ObjectNode;
import im.platform.gateway.auth.Gateway;
import im.platform.shared.authsupport.Tokens;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.lang.reflect.*;
import java.util.*;
import static im.platform.tests.im.GroupFixtures.*;

/** Exercise the committed notification boundary with a real bound peer. */
final class MessageDeliveryProbe {
    @SuppressWarnings("unchecked")
    static void check(Gateway gateway,Tokens.Claims claims,WebSocketSession healthy,List<JsonNode> sent,JsonNode timestamps)throws Exception {
        var deliver=Gateway.class.getDeclaredMethod("deliver",String.class,JsonNode.class);
        deliver.setAccessible(true);
        var registry=Gateway.class.getDeclaredField("bound");
        registry.setAccessible(true);
        var bound=(Map<WebSocketSession,Tokens.Claims>)registry.get(gateway);
        String recipient=claims.userId();
        var event=(ObjectNode)MessageFixtures.frame("message.created",UUID.randomUUID().toString(),Map.of(
            "senderId",UUID.randomUUID().toString(),"conversationId",UUID.randomUUID().toString(),
            "messageId",UUID.randomUUID().toString(),"seq",1,"createdAt","2026-01-01T00:00:00Z",
            "content",Map.of("kind","TEXT","text","😀".repeat(4096))));
        sent.clear();
        for(String field:List.of("seq","messageId","createdAt","content","senderId","conversationId")) {
            var missing=event.deepCopy();
            ((ObjectNode)missing.get("payload")).remove(field);
            reject(deliver,gateway,recipient,missing);
        }
        for(String field:List.of("seq","messageId","content","requestId","kind","text","oversized","timestamp","extra","noncanonicalId")) {
            var malformed=event.deepCopy();
            var body=(ObjectNode)malformed.get("payload");
            var content=(ObjectNode)body.get("content");
            switch(field) {
                case "seq" -> body.put("seq",0);
                case "messageId" -> body.put("messageId","bogus");
                case "noncanonicalId" -> body.put("senderId","ABCDEFAB-0000-0000-0000-000000000000");
                case "content" -> body.put("content","TEXT");
                case "requestId" -> malformed.put("requestId",17);
                case "kind" -> content.put("kind","unknown");
                case "text" -> content.put("text",42);
                case "oversized" -> content.put("text","x".repeat(4097));
                case "timestamp" -> body.put("createdAt","yesterday");
                case "extra" -> malformed.put("unexpected",true);
                default -> throw new AssertionError(field);
            }
            reject(deliver,gateway,recipient,malformed);
        }
        for(var entry:timestamps.properties()) {
            var candidate=event.deepCopy();
            ((ObjectNode)candidate.get("payload")).put("createdAt",entry.getKey());
            if(entry.getValue().booleanValue()) {
                deliver.invoke(gateway,recipient,candidate);
                require(sent.size()==1 && sent.removeFirst().equals(candidate),"event timestamp "+entry.getKey());
            } else {
                reject(deliver,gateway,recipient,candidate);
            }
        }
        var defect=new IllegalStateException("fixture serialization failure");
        var broken=new ObjectNode(JSON.getNodeFactory()){
            @Override public void serialize(JsonGenerator output,SerializerProvider provider)throws IOException {
                throw JsonMappingException.from(output,"Cannot serialize fixture",defect);
            }
        };
        broken.setAll(event);
        try {deliver.invoke(gateway,recipient,broken);throw new AssertionError("serializer defect hidden");}
        catch(InvocationTargetException observed) {
            if(!(observed.getCause() instanceof JsonMappingException failure) || failure.getCause()!=defect) throw observed;
        }
        require(sent.isEmpty() && claims.equals(bound.get(healthy)),"invalid events preserve the healthy peer");

        var calls=new ArrayList<String>();
        var lost=(WebSocketSession)Proxy.newProxyInstance(WebSocketSession.class.getClassLoader(),
            new Class<?>[]{WebSocketSession.class},(peer,method,args)->switch(method.getName()) {
                case "hashCode" -> System.identityHashCode(peer);
                case "equals" -> peer==args[0];
                case "isOpen" -> true;
                case "sendMessage" -> {calls.add("send");throw new IOException("disconnected peer");}
                case "close" -> {calls.add("close");yield null;}
                default -> throw new AssertionError(method.getName());
            });
        bound.put(lost,claims);
        deliver.invoke(gateway,recipient,event);
        require(calls.equals(List.of("send","close")) && !bound.containsKey(lost),"retire disconnected peer");
        require(sent.equals(List.of(event)) && claims.equals(bound.get(healthy)),"healthy peer receives complete event");
    }

    private static void reject(Method deliver,Gateway gateway,String recipient,ObjectNode invalid)throws Exception {
        try {deliver.invoke(gateway,recipient,invalid);throw new AssertionError("delivered malformed committed event");}
        catch(InvocationTargetException observed) {
            if(!(observed.getCause() instanceof IllegalStateException ||
                observed.getCause() instanceof java.time.format.DateTimeParseException)) throw observed;
        }
    }
}
