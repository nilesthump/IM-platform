package im.platform.tests.auth;

import com.fasterxml.jackson.databind.ObjectMapper;
import im.platform.gateway.auth.Gateway;
import im.platform.shared.authsupport.Config;
import im.platform.shared.authsupport.Tokens;
import io.nats.client.Connection;
import io.nats.client.Nats;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.Duration;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

/** Real Gateway notification worker, with deterministic transport outcomes at the session boundary. */
public final class RevocationDeliveryProbe {
    private static final ObjectMapper JSON = new ObjectMapper();

    enum Outcome { DELIVER, DISCONNECT, CLOSE_RACE, INTERNAL }

    static final class Peer {
        final LinkedBlockingQueue<String> calls = new LinkedBlockingQueue<>();
        final IllegalStateException internal = new IllegalStateException("open transport invariant");
        boolean open = true;
        final WebSocketSession socket;

        Peer(Outcome outcome) {
            socket = (WebSocketSession) Proxy.newProxyInstance(WebSocketSession.class.getClassLoader(),
                new Class<?>[]{WebSocketSession.class}, (proxy, method, args) -> switch (method.getName()) {
                    case "hashCode" -> System.identityHashCode(proxy);
                    case "equals" -> proxy == args[0];
                    case "isOpen" -> open;
                    case "sendMessage" -> {
                        if (outcome == Outcome.INTERNAL) throw internal;
                        if (outcome != Outcome.DELIVER) {
                            open = false;
                            calls.add("send-failed");
                            if (outcome == Outcome.CLOSE_RACE) throw new IllegalStateException("closed");
                            throw new IOException("peer disconnected");
                        }
                        calls.add(((TextMessage)args[0]).getPayload());
                        yield null;
                    }
                    case "close" -> {
                        open = false;
                        calls.add("close");
                        if (outcome == Outcome.DISCONNECT) throw new IOException("peer disconnected");
                        if (outcome == Outcome.CLOSE_RACE) throw new IllegalStateException("closed");
                        yield null;
                    }
                    default -> throw new AssertionError(method.getName());
                });
        }
        String next() throws InterruptedException {
            var call = calls.poll(5, TimeUnit.SECONDS);
            if (call == null) throw new AssertionError("Timed out waiting for peer operation");
            return call;
        }
        void expect(String call) throws InterruptedException {
            if (!call.equals(next())) throw new AssertionError("Expected " + call);
        }
        void expectDelivery(String sid) throws Exception {
            var frame = JSON.readTree(next());
            if (!"session.revoked".equals(frame.path("type").asText())
                || !sid.equals(frame.at("/payload/sessionId").asText())
                || !"LOGOUT".equals(frame.at("/payload/reason").asText())) throw new AssertionError("Wrong revoke");
            expect("close");
        }
    }

    private static void checkRejectionFailures(Gateway gateway) throws Exception {
        var constructor = Class.forName(Gateway.class.getName() + "$Socket").getDeclaredConstructor(Gateway.class);
        constructor.setAccessible(true);
        var handler = (org.springframework.web.socket.WebSocketHandler)constructor.newInstance(gateway);
        for (String type : new String[]{"auth.bind", "message.send"}) {
            var primary = new IllegalStateException("send invariant");
            var secondary = new IOException("transport close failed");
            var socket = (WebSocketSession)Proxy.newProxyInstance(WebSocketSession.class.getClassLoader(),
                new Class<?>[]{WebSocketSession.class}, (proxy, method, args) -> switch (method.getName()) {
                    case "hashCode" -> System.identityHashCode(proxy);
                    case "sendMessage" -> throw primary;
                    case "close" -> throw secondary;
                    default -> throw new AssertionError(method.getName());
                });
            var frame = Map.of("protocolVersion","1.0","requestId",UUID.randomUUID().toString(),"type",type,"payload",Map.of());
            try {
                handler.handleMessage(socket, new TextMessage(JSON.writeValueAsString(frame)));
                throw new AssertionError("Failed rejection returned normally");
            } catch (IllegalStateException observed) {
                if (observed != primary || observed.getSuppressed().length != 1 || observed.getSuppressed()[0] != secondary) {
                    throw new AssertionError("Rejection masked send or close failure", observed);
                }
            }
        }
        System.out.println("GATEWAY both rejection paths preserve send and close failures PASS");
    }

    // Inspect the existing registry and subscription without introducing product-only test hooks.
    private static Object field(Gateway gateway, String name) throws ReflectiveOperationException {
        var field = Gateway.class.getDeclaredField(name);
        field.setAccessible(true);
        return field.get(gateway);
    }
    private static void publish(Connection nats, String sid) throws Exception {
        nats.publish("session.revoked", JSON.writeValueAsBytes(Map.of("sessionId", sid, "reason", "LOGOUT")));
        nats.flush(Duration.ofSeconds(2));
    }
    private static Tokens.Claims claims() {
        return new Tokens.Claims(UUID.randomUUID().toString(), UUID.randomUUID().toString(), "WEB", 1, 1, 2);
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        var config = Config.read(args[0]);
        var gateway = new Gateway(config);
        try (var publisher = Nats.connect(config.natsUrl)) {
            checkRejectionFailures(gateway);
            ((Connection)field(gateway, "nats")).flush(Duration.ofSeconds(2));
            var bound = (Map<WebSocketSession, Tokens.Claims>)field(gateway, "bound");
            var errors = new LinkedBlockingQueue<Throwable>();
            ((Thread)field(gateway, "events")).setUncaughtExceptionHandler((thread, error) -> errors.add(error));
            var first = claims();
            var lost = new Peer(Outcome.DISCONNECT);
            var closed = new Peer(Outcome.CLOSE_RACE);
            var survivor = new Peer(Outcome.DELIVER);
            for (var peer : new Peer[]{lost, closed, survivor}) bound.put(peer.socket, first);
            publish(publisher, first.sessionId());
            for (var peer : new Peer[]{lost, closed}) {
                peer.expect("send-failed");
                peer.expect("close");
            }
            survivor.expectDelivery(first.sessionId());
            var next = claims();
            var later = new Peer(Outcome.DELIVER);
            bound.put(later.socket, next);
            publish(publisher, next.sessionId());
            later.expectDelivery(next.sessionId());
            if (!bound.isEmpty()) throw new AssertionError("Revoked peer remains registered");

            var broken = new Peer(Outcome.INTERNAL);
            bound.put(broken.socket, next);
            publish(publisher, next.sessionId());
            if (errors.poll(5, TimeUnit.SECONDS) != broken.internal) throw new AssertionError("Internal failure lost");
            broken.expect("close");
            System.out.println("GATEWAY disconnected peers retired, same and next revokes delivered, internal failure propagated PASS");
        } finally {
            gateway.destroy();
        }
    }
}
