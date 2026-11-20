package im.platform.tests.im;

import com.fasterxml.jackson.databind.*;

import im.platform.shared.authsupport.Config;
import java.nio.file.*;
import java.util.*;
import static im.platform.tests.im.GroupFixtures.*;

public final class ProfileContinuity {
    public static void main(String[] args)throws Exception {
        var f=new GroupFixtures(Config.read(args[2]),args[0]);
        var state=Path.of(args[3]);
        if(args[1].equals("write")) {
            f.prepareUsers();
            String actor=f.user(1), second=f.user(2),newMember=f.user(3);

            // Set up two friend pairs through the actual public route.
            for(var pair:List.of(List.of(actor,second),List.of(second,newMember))){
                var request=java.net.http.HttpRequest.newBuilder(java.net.URI.create(f.base+"/v1/friends/"+pair.get(1)))
                    .header("Authorization","Bearer "+f.tokens.get(pair.get(0))).PUT(java.net.http.HttpRequest.BodyPublishers.noBody()).build();
                require(f.http.send(request,java.net.http.HttpResponse.BodyHandlers.discarding()).statusCode()==201,"friend setup");
            }
            String body=GroupTransactions.mutation(UUID.randomUUID().toString(),List.of(second));
            var create=f.call("/v1/groups",body,f.tokens.get(actor));
            require(create.statusCode()==201,"create group");
            var original=JSON.readTree(create.body());
            String conv=original.get("conversationId").asText(),id=UUID.randomUUID().toString();
            var frame=MessageFixtures.frame("message.send",id,Map.of("conversationId",conv,"content",Map.of("kind","TEXT","text","before member joined")));
            JsonNode ack;
            try(var sender=new MessageFixtures.Peer(f.base,f.tokens.get(actor))){sender.send(frame);ack=sender.next();}
            require(ack.at("/payload/status").asText().equals("committed"),"pre-join durable ACK");
            String add=GroupTransactions.mutation(UUID.randomUUID().toString(),List.of(newMember));
            require(f.call("/v1/groups/"+conv+"/members",add,f.tokens.get(second)).statusCode()==200,"member add");
            var query=JSON.createObjectNode().put("type","sync.user.request").put("syncVersion","1.0").put("requestId",UUID.randomUUID().toString()).put("limit",1).put("cursor","0");
            var first=JSON.readTree(f.call("/v1/sync/user",query.toString(),f.tokens.get(actor)).body());
            require(first.path("hasMore").booleanValue(),"first cursor");
            query.put("cursor",first.get("nextCursor").textValue());
            var expected=JSON.readTree(f.call("/v1/sync/user",query.toString(),f.tokens.get(actor)).body());
            var saved=JSON.createObjectNode().put("actorToken",f.tokens.get(actor)).put("newMemberToken",f.tokens.get(newMember)).put("create",body);
            saved.set("result",original);saved.set("ack",ack);saved.set("frame",frame);saved.set("query",query);saved.set("page",expected);
            Files.writeString(state,saved.toString(),StandardOpenOption.CREATE_NEW);
        } else if(args[1].equals("read")) {
            var saved=JSON.readTree(state.toFile());String token=saved.get("actorToken").asText();
            var replay=f.call("/v1/groups",saved.get("create").asText(),token);
            var result=JSON.readTree(replay.body());var original=saved.get("result");
            normalizeTimes(result);normalizeTimes(original);
            require(replay.statusCode()==201 && original.equals(result),"cross-profile receipt replay");
            require(JSON.readTree(f.call("/v1/sync/user",saved.get("query").toString(),token).body()).equals(saved.get("page")),"cross-profile opaque cursor");
            var history=Map.of("syncVersion","1.0","type","sync.conversation.request","conversationId",result.get("conversationId"),
                "afterSeq",0,"limit",1,"requestId",UUID.randomUUID());
            var page=JSON.readTree(f.call("/v1/sync/conversation",JSON.writeValueAsString(history),saved.get("newMemberToken").asText()).body());
            require(page.path("messages").size()==1 && page.at("/messages/0/messageId").equals(saved.at("/ack/payload/messageId")),"joined member cannot read earlier history");
            try(var sender=new MessageFixtures.Peer(f.base,token)){
                sender.send(saved.get("frame"));
                var reply=sender.next();var prior=saved.get("ack");normalizeTimes(reply);normalizeTimes(prior);
                require(reply.equals(prior),"cross-profile message ACK replay");
            }
            System.out.println("PASS cursor, group receipt, prior history, credentials and same committed ACK after profile switch");
        } else throw new IllegalArgumentException("Expected read or write");
    }
}

