package im.platform.shared.authsupport;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.DeserializationFeature;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import javax.sql.DataSource;
import org.postgresql.ds.PGSimpleDataSource;

public final class Config {
    public String postgresHost,postgresUser,postgresDatabase,postgresPasswordFile,jwtSigningKeyFile,coreUrl,natsUrl;
    public int postgresPort;
    public int accessTokenSeconds=900, refreshTokenSeconds=2592000;
    public String publicOrigin;
    private byte[] key;
    private DataSource database;
    public static Config read(String filename)throws java.io.IOException {
        if(filename==null||filename.isBlank())throw new IllegalArgumentException("IM_CONFIG_FILE is required");
        Path file=Path.of(filename);
        Config cfg=new ObjectMapper().enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS).readValue(Files.readAllBytes(file),Config.class);
        if(cfg.postgresPort<1||cfg.postgresPort>65535)throw new IllegalArgumentException("Invalid database port");
        for(String v:new String[]{cfg.postgresHost,cfg.postgresUser,cfg.postgresDatabase,cfg.postgresPasswordFile,cfg.jwtSigningKeyFile,cfg.coreUrl,cfg.natsUrl})
            if(v==null||v.isBlank())throw new IllegalArgumentException("Runtime configuration incomplete");
        if(cfg.accessTokenSeconds<=0||cfg.refreshTokenSeconds<=cfg.accessTokenSeconds)throw new IllegalArgumentException("Token durations must be positive; refresh must outlive access");
        if(cfg.publicOrigin!=null){
            java.net.URI origin=java.net.URI.create(cfg.publicOrigin);
            if(!"https".equals(origin.getScheme())||origin.getHost()==null||origin.getRawUserInfo()!=null||origin.getRawQuery()!=null||origin.getRawFragment()!=null||!origin.getRawPath().isEmpty())throw new IllegalArgumentException("publicOrigin must be an exact HTTPS origin");
        }
        Path parent=file.toAbsolutePath().getParent();
        String password=Files.readString(parent.resolve(cfg.postgresPasswordFile)).strip();
        cfg.key=Files.readString(parent.resolve(cfg.jwtSigningKeyFile)).strip().getBytes(StandardCharsets.UTF_8);
        if(password.isEmpty()||cfg.key.length<32)throw new IllegalArgumentException("Runtime credentials invalid");
        PGSimpleDataSource db=new PGSimpleDataSource();db.setServerNames(new String[]{cfg.postgresHost});db.setPortNumbers(new int[]{cfg.postgresPort});
        db.setDatabaseName(cfg.postgresDatabase);db.setUser(cfg.postgresUser);db.setPassword(password);cfg.database=db;return cfg;
    }
    public DataSource database(){return database;}
    public byte[] signingKey(){return key.clone();}
}
