package im.platform.core.auth;

import im.platform.shared.authsupport.Config;
import io.nats.client.Nats;
import org.springframework.jdbc.core.JdbcTemplate;
import java.net.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.*;

/** Real NATS traffic with only PONG delayed: no product mock or shared-server fault. */
public final class OutboxRecoveryProbe {
    public static void main(String[] args)throws Exception{
        Config config=Config.read(args[0]);JdbcTemplate db=new JdbcTemplate(config.database());
        UUID event=UUID.randomUUID(),sid=UUID.randomUUID();String original=config.natsUrl;
        try(PongDelay proxy=new PongDelay(URI.create(original));var observer=Nats.connect(original)){
            var subscription=observer.subscribe("session.revoked");observer.flush(Duration.ofSeconds(2));
            config.natsUrl="nats://127.0.0.1:"+proxy.server.getLocalPort();
            try(AutoCloseable cleanup=()->db.update("DELETE FROM outbox_events WHERE event_id=?",event);
                SessionOutbox worker=new SessionOutbox(config)){
                proxy.delay=true;
                db.update("INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload) VALUES(?,'session',?,'session.revoked',?::jsonb)",event,sid,"{\"sessionId\":\""+sid+"\",\"reason\":\"LOGOUT\"}");
                if(!proxy.delayed.await(5,TimeUnit.SECONDS))throw new AssertionError("No real PONG intercepted");
                Thread.sleep(2300); // Exceeds the actual 2s flush deadline; inspect committed state.
                if(db.queryForObject("SELECT published_at IS NULL AND attempts=0 FROM outbox_events WHERE event_id=?",Boolean.class,event)!=Boolean.TRUE)throw new AssertionError("Timed out batch was marked published");
                proxy.delay=false;proxy.release.countDown();
                long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(8);boolean published=false;
                while(System.nanoTime()<deadline){published=Boolean.TRUE.equals(db.queryForObject("SELECT published_at IS NOT NULL FROM outbox_events WHERE event_id=?",Boolean.class,event));if(published)break;Thread.sleep(50);}
                if(!published)throw new AssertionError("Outbox did not recover without process restart");
                boolean delivered=false;while(System.nanoTime()<deadline){var message=subscription.nextMessage(Duration.ofMillis(100));if(message!=null&&new String(message.getData(),StandardCharsets.UTF_8).contains(sid.toString())){delivered=true;break;}}
                if(!delivered)throw new AssertionError("Recovered event not delivered to real subscriber");
                proxy.check();System.out.println("OUTBOX real delayed PONG rollback and next-tick delivery PASS");
            }
        }
        // A non-publication failure must still reach the uncaught worker boundary.
        var mapper=new com.fasterxml.jackson.databind.ObjectMapper();
        var broken=(com.fasterxml.jackson.databind.node.ObjectNode)mapper.readTree(java.nio.file.Path.of(args[0]).toFile());
        try(ServerSocket unavailable=new ServerSocket(0,1,InetAddress.getLoopbackAddress())){broken.put("postgresPort",unavailable.getLocalPort());}
        java.nio.file.Path file=java.nio.file.Path.of(args[0]).getParent().resolve("unavailable-db-config.json");
        mapper.writeValue(file.toFile(),broken);CountDownLatch failed=new CountDownLatch(1);var errors=new ConcurrentLinkedQueue<Throwable>();
        var prior=Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{errors.add(error);failed.countDown();});
        try(AutoCloseable delete=()->java.nio.file.Files.delete(file);
            AutoCloseable restore=()->Thread.setDefaultUncaughtExceptionHandler(prior);
            SessionOutbox worker=new SessionOutbox(Config.read(file.toString()))){
            if(!failed.await(10,TimeUnit.SECONDS))throw new AssertionError("Unknown worker database failure was hidden");
            if(!(errors.peek() instanceof org.springframework.transaction.CannotCreateTransactionException))throw new AssertionError("Unexpected worker failure",errors.peek());
            System.out.println("OUTBOX non-publication failure reaches uncaught worker boundary PASS");
        }
    }
    static final class PongDelay implements AutoCloseable{
        final ServerSocket server=new ServerSocket(0,1,InetAddress.getLoopbackAddress());
        final CountDownLatch delayed=new CountDownLatch(1),release=new CountDownLatch(1);
        final ConcurrentLinkedQueue<Throwable> errors=new ConcurrentLinkedQueue<>();
        volatile boolean delay,closing;volatile Socket client,upstream;final Thread bridge;
        PongDelay(URI target)throws IOException{
            bridge=Thread.ofPlatform().uncaughtExceptionHandler((thread,error)->errors.add(error)).start(()->{
                try{
                    try{client=server.accept();}
                    catch(SocketException failure){if(closing && server.isClosed())return;throw failure;}
                    upstream=new Socket(target.getHost(),target.getPort());
                    Thread forward=Thread.ofPlatform().uncaughtExceptionHandler((thread,error)->errors.add(error)).start(()->{
                        try{client.getInputStream().transferTo(upstream.getOutputStream());}
                        catch(IOException failure){if(!closing || !(failure instanceof SocketException))errors.add(failure);}
                    });
                    try(AutoCloseable join=forward::join; Socket releaseUpstream=upstream; Socket releaseClient=client){
                        try{
                            var reader=new BufferedReader(new InputStreamReader(upstream.getInputStream(),StandardCharsets.US_ASCII));
                            String line;
                            while((line=reader.readLine())!=null){
                                if(line.equals("PONG") && delay){delayed.countDown();release.await();}
                                client.getOutputStream().write((line+"\r\n").getBytes(StandardCharsets.US_ASCII));
                                client.getOutputStream().flush();
                            }
                        }catch(SocketException failure){if(!closing)throw failure;}
                        finally{closing=true;}
                    }
                }catch(Exception failure){
                    errors.add(failure);
                    if(failure instanceof InterruptedException)Thread.currentThread().interrupt();
                }
            });
        }
        void check(){
            Throwable first=errors.poll();
            if(first==null)return;
            var failure=new AssertionError("NATS test proxy failed",first);
            for(Throwable later;(later=errors.poll())!=null;)failure.addSuppressed(later);
            throw failure;
        }
        public void close()throws Exception{
            closing=true;release.countDown();
            try(AutoCloseable inspect=this::check;
                AutoCloseable join=()->{bridge.join(5000);if(bridge.isAlive())throw new AssertionError("NATS test proxy did not stop");};
                Socket closeUpstream=upstream; Socket closeClient=client; ServerSocket listener=server){}
        }
    }
}
