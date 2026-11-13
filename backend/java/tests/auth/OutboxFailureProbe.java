package im.platform.core.auth;
import im.platform.shared.authsupport.Config;
import io.nats.client.Nats;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import java.util.UUID;

/** Real closed NATS connection, actual PostgreSQL rollback, before any role starts. */
public class OutboxFailureProbe {
    public static void main(String[] args)throws Exception{
        Config config=Config.read(args[0]);var db=new JdbcTemplate(config.database());
        var transaction=new TransactionTemplate(new DataSourceTransactionManager(config.database()));
        UUID event=UUID.randomUUID(),session=UUID.randomUUID();
        db.update("INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload) VALUES(?,'session',?,'session.revoked',?::jsonb)",event,session,"{\"sessionId\":\""+session+"\",\"reason\":\"LOGOUT\"}");
        try{
            var connection=Nats.connect(config.natsUrl);connection.close();
            boolean failed=false;try{SessionOutbox.publishBatch(db,transaction,connection);}catch(IllegalStateException closed){if(!closed.getMessage().toLowerCase().contains("closed"))throw closed;failed=true;}
            if(!failed)throw new AssertionError("Closed NATS publication reported success");
            var row=db.queryForMap("SELECT published_at,attempts FROM outbox_events WHERE event_id=?",event);
            if(row.get("published_at")!=null||((Number)row.get("attempts")).intValue()!=0)throw new AssertionError("Failed publication changed outbox state");
            System.out.println("OUTBOX closed NATS leaves real PostgreSQL event pending PASS");
        }finally{db.update("DELETE FROM outbox_events WHERE event_id=?",event);}
    }
}
