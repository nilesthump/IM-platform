import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;

public final class InfraPlaceholder {
    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !(args[0].equals("gateway") || args[0].equals("core") || args[0].equals("plugin-host"))) {
            throw new IllegalArgumentException("expected gateway, core, or plugin-host role");
        }
        String role = args[0];
        try (ServerSocket server = new ServerSocket(8080)) {
            while (true) {
                try (Socket socket = server.accept()) {
                    socket.setSoTimeout(5000);
                    handle(socket, role);
                } catch (Exception error) {
                    System.err.println("placeholder request failed: " + error.getClass().getSimpleName());
                }
            }
        }
    }

    private static void handle(Socket socket, String role) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.US_ASCII));
        String request = reader.readLine();
        if (request == null) return;
        String path = request.split(" ")[1];
        String key = null;
        boolean upgrade = false;
        String line;
        while ((line = reader.readLine()) != null && !line.isEmpty()) {
            int colon = line.indexOf(':');
            if (colon < 0) continue;
            String name = line.substring(0, colon).trim();
            String value = line.substring(colon + 1).trim();
            if (name.equalsIgnoreCase("Sec-WebSocket-Key")) key = value;
            if (name.equalsIgnoreCase("Upgrade") && value.equalsIgnoreCase("websocket")) upgrade = true;
        }
        OutputStream out = socket.getOutputStream();
        if (role.equals("gateway") && path.equals("/__infra/ws") && upgrade && key != null) {
            byte[] digest = MessageDigest.getInstance("SHA-1").digest((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").getBytes(StandardCharsets.US_ASCII));
            String accept = Base64.getEncoder().encodeToString(digest);
            out.write(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + accept + "\r\n\r\n").getBytes(StandardCharsets.US_ASCII));
        } else if (path.equals("/__infra/health")) {
            byte[] body = ("profile=java role=" + role + "\n").getBytes(StandardCharsets.UTF_8);
            out.write(("HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: " + body.length + "\r\nConnection: close\r\n\r\n").getBytes(StandardCharsets.US_ASCII));
            out.write(body);
        } else {
            out.write("HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".getBytes(StandardCharsets.US_ASCII));
        }
        out.flush();
    }
}
