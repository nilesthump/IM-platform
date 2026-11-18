package im.platform;
import im.platform.core.auth.CoreAuth;
import im.platform.core.auth.SessionOutbox;
import im.platform.gateway.auth.Gateway;
import im.platform.pluginhost.Health;
import im.platform.shared.authsupport.Config;
import org.springframework.boot.SpringApplication;
import java.util.Map;

public final class Main {
    public static void main(String[] args)throws Exception {
        if(args.length!=1)throw new IllegalArgumentException("Exactly one service role is required");
        Class<?> role=switch(args[0]){case "core"->CoreAuth.class;case "gateway"->Gateway.class;case "plugin-host"->Health.class;default->throw new IllegalArgumentException("Unknown role");};
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{
            System.err.println("Service worker failed: "+error.getClass().getName());
            // Spring's shutdown hook joins role workers. Let the failed thread finish first.
            Thread.ofPlatform().name("service-failure-exit").daemon(false).start(()->System.exit(1));
        });
        SpringApplication app=new SpringApplication(role);
        Config config=args[0].equals("plugin-host")?null:Config.read(System.getenv("IM_CONFIG_FILE"));
        if(config!=null)app.addInitializers(context->context.getBeanFactory().registerSingleton("runtimeConfig",config));
        app.setDefaultProperties(Map.of("server.port",System.getenv().getOrDefault("IM_LISTEN_PORT","8080"),"server.error.include-message","never","server.error.include-stacktrace","never","spring.main.banner-mode","off"));
        var context=app.run();
        if(args[0].equals("core")){SessionOutbox outbox=new SessionOutbox(config);context.addApplicationListener(event->{if(event instanceof org.springframework.context.event.ContextClosedEvent){try{outbox.close();}catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new IllegalStateException(interrupted);}}});}
    }
}
