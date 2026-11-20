package im.platform.core.auth;
import im.platform.shared.authsupport.Config;
import io.nats.client.Connection;
import io.nats.client.Nats;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

/** Session and Message delivery. The DB transaction remains pending if publication fails. */
public final class SessionOutbox implements AutoCloseable {
    private final Connection nats;
    private final Thread worker;
    private volatile boolean stopping;
    public SessionOutbox(Config config)throws java.io.IOException,InterruptedException {
        this(config,Nats.connect(config.natsUrl));
    }
    SessionOutbox(Config config,Connection nats){
        this.nats=nats;
        JdbcTemplate db=new JdbcTemplate(config.database());
        TransactionTemplate transaction=new TransactionTemplate(new DataSourceTransactionManager(config.database()));
        worker=Thread.ofPlatform().name("session-outbox").unstarted(()->{
            try{
                while(!stopping){
                    var status=nats.getStatus();
                    if(status==Connection.Status.CLOSED)throw new IllegalStateException("Session Outbox NATS connection permanently closed");
                    if(status==Connection.Status.CONNECTED){
                        try{publishBatch(db,transaction,nats);}
                        catch(PublicationTimeout timeout){System.err.println("Session publication timed out; transaction rolled back; retrying next tick");}
                    }
                    Thread.sleep(500);
                }
            }catch(InterruptedException interrupted){if(!stopping){Thread.currentThread().interrupt();throw new IllegalStateException(interrupted);}}
        });
        worker.start();
    }
    private static final class PublicationTimeout extends RuntimeException { PublicationTimeout(java.util.concurrent.TimeoutException cause){super(cause);} }
    static void publishBatch(JdbcTemplate db,TransactionTemplate transaction,Connection nats){
        transaction.executeWithoutResult(status->{
            var rows=db.queryForList("SELECT event_id,event_type,conversation_id,payload::text AS payload FROM outbox_events WHERE event_type IN ('session.revoked','message.created') AND published_at IS NULL ORDER BY created_at,event_id LIMIT 32 FOR UPDATE SKIP LOCKED");
            for(var row:rows) {
                byte[] data=row.get("payload").toString().getBytes(StandardCharsets.UTF_8);
                if("session.revoked".equals(row.get("event_type"))) nats.publish("session.revoked",data);
                else {
                    var users=db.queryForList("SELECT user_id FROM conversation_members WHERE conversation_id=? AND left_at IS NULL",java.util.UUID.class,row.get("conversation_id"));
                    for(var user:users) nats.publish("message.created."+user,data);
                }
            }
            if(!rows.isEmpty()){
                try{nats.flush(Duration.ofSeconds(2));}
                catch(java.util.concurrent.TimeoutException failure){throw new PublicationTimeout(failure);}
                catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new IllegalStateException(interrupted);}
                for(var row:rows)db.update("UPDATE outbox_events SET published_at=now(),attempts=attempts+1 WHERE event_id=?",row.get("event_id"));
            }
        });
    }
    @Override public void close()throws InterruptedException {stopping=true;try(nats){worker.join();}}
}
