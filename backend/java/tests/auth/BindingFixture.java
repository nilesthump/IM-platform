package im.platform.tests.auth;

import im.platform.shared.authsupport.Config;
import im.platform.shared.authsupport.PasswordHash;
import im.platform.shared.authsupport.Tokens;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Files;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.UUID;

/** Two fresh synthetic accounts in a disposable target database, seeded before its roles start. */
public final class BindingFixture {
    static UUID owner(UUID subject) {
        return UUID.nameUUIDFromBytes(("fixture-owner-" + subject).getBytes(StandardCharsets.UTF_8));
    }
    static String username(UUID id) { return "binding" + id.toString().replace("-", ""); }

    static void insert(Connection db, UUID user, UUID session) throws SQLException {
        try (var account = db.prepareStatement("INSERT INTO users(user_id, username, display_name, password_hash) VALUES(?,?,?,?)");
             var slot = db.prepareStatement("INSERT INTO sessions(user_id, client_type, session_id, session_epoch, refresh_token_hash, status, device_id, expires_at) VALUES(?,'WEB',?,1,?,'ACTIVE','binding-fixture',now()+interval '1 hour')")) {
            account.setObject(1,user);
            account.setString(2,username(user));
            account.setString(3,"Binding fixture");
            account.setString(4,PasswordHash.create(UUID.randomUUID().toString()));
            account.executeUpdate();
            slot.setObject(1,user);
            slot.setObject(2,session);
            slot.setString(3,Tokens.hash(Tokens.random()));
            slot.executeUpdate();
        }
    }
    static void verify(Connection db, Tokens.Claims issued) throws SQLException {
        UUID subject=UUID.fromString(issued.userId()), session=UUID.fromString(issued.sessionId());
        try(var q=db.prepareStatement("SELECT user_id,session_id FROM sessions WHERE user_id IN (?,?) AND client_type='WEB' AND session_epoch=1 AND status='ACTIVE' AND device_id='binding-fixture'")) {
            q.setObject(1,subject);q.setObject(2,owner(subject));
            boolean subjectSlot=false, ownerSlot=false;
            try(var rows=q.executeQuery()) {
                while(rows.next()){
                    UUID user=rows.getObject(1,UUID.class), id=rows.getObject(2,UUID.class);
                    if(user.equals(subject))subjectSlot=!id.equals(session);
                    if(user.equals(owner(subject)))ownerSlot=id.equals(session);
                }
            }
            AuthFixtureRunner.require(subjectSlot && ownerSlot,"Missing distinct synthetic subject and session owner");
        }
    }
    public static void main(String[] args) throws Exception {
        Config config=Config.read(args[1]);
        Tokens.Claims issued=new Tokens(config.signingKey()).parse(Files.readString(Path.of(args[2])));
        AuthFixtureRunner.require(issued.epoch()==1 && issued.clientType().equals("WEB"),"Expected newly issued fixture session");
        UUID subject=UUID.fromString(issued.userId()), owner=owner(subject);
        try(var db=config.database().getConnection()){
            db.setAutoCommit(false);
            if(args[0].equals("prepare")){
                insert(db,subject,UUID.randomUUID());
                insert(db,owner,UUID.fromString(issued.sessionId()));
                verify(db,issued);
            }else if(args[0].equals("cleanup")){
                try(var slots=db.prepareStatement("DELETE FROM sessions WHERE user_id IN (?,?) AND device_id='binding-fixture'");
                    var users=db.prepareStatement("DELETE FROM users WHERE user_id=? AND username=?")){
                    slots.setObject(1,subject);slots.setObject(2,owner);
                    AuthFixtureRunner.require(slots.executeUpdate()==2,"Synthetic slot cleanup");
                    for(UUID id:new UUID[]{subject,owner}){
                        users.setObject(1,id);users.setString(2,username(id));
                        AuthFixtureRunner.require(users.executeUpdate()==1,"Synthetic account cleanup");
                    }
                }
            }else throw new IllegalArgumentException("Unknown fixture operation");
            db.commit();
        }
        System.out.println("BINDING fixture "+args[0]+" complete");
    }
}
