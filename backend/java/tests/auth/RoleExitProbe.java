package im.platform.tests.auth;

import im.platform.Main;

/** Run on the role's packaged classpath in a disposable JVM with its production shutdown hooks. */
public final class RoleExitProbe {
    public static void main(String[] args) throws Exception {
        String role = args[0];
        Main.main(new String[]{role});
        String name = role.equals("core") ? "session-outbox" : "session-notifications";
        Thread worker = Thread.getAllStackTraces().keySet().stream()
            .filter(thread -> thread.getName().equals(name)).findFirst().orElseThrow();
        System.out.println("ROLE_EXIT_READY " + role + " " + args[1]);
        if (args[1].equals("normal")) {
            System.exit(0);
        } else {
            worker.interrupt(); // Unexpected while running, in contrast to an ordinary context close.
        }
    }
}
