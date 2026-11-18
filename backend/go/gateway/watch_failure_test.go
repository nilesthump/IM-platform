package gateway

import (
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgproto3"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
)

func watchFixture(t *testing.T, db *pgxpool.Pool) (*hub, shared.Claims, string) {
	t.Helper()
	codec := &shared.Codec{Key: []byte("public-controlled-fixture-key-32-bytes"), Now: time.Now}
	cl := shared.Claims{UserID: "11111111-1111-4111-8111-111111111111", SessionID: "22222222-2222-4222-8222-222222222222", ClientType: "DESKTOP", SessionEpoch: 1, IssuedAt: time.Now().Unix(), ExpiresAt: time.Now().Add(time.Hour).Unix()}
	token, err := codec.Sign(cl)
	if err != nil {
		t.Fatal(err)
	}
	return newHub(&validator{db: db, codec: codec, now: time.Now}), cl, token
}

func watchPool(t *testing.T, host string, port int) *pgxpool.Pool {
	t.Helper()
	cfg, err := pgxpool.ParseConfig(fmt.Sprintf("host=%s port=%d user=public_fixture dbname=public_fixture sslmode=disable connect_timeout=1", host, port))
	if err != nil {
		t.Fatal(err)
	}
	pool, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(pool.Close)
	return pool
}

// Model an already-bound connection whose later safety check loses its DB.
// The validator/pgx/watch/close and loopback WebSocket consumer are production.
func observeWatchFailure(t *testing.T, h *hub, cl shared.Claims, token string) error {
	t.Helper()
	returned := make(chan error, 1)
	connections := make(chan *connection, 1)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ws, err := (&websocket.Upgrader{}).Upgrade(w, r, nil)
		if err != nil {
			return
		}
		c := &connection{ws: ws, done: make(chan struct{}), bound: &cl, token: token}
		h.add(cl.SessionID, c)
		defer h.remove(cl.SessionID, c)
		defer c.close()
		connections <- c
		returned <- h.watch(c, cl)
	}))
	t.Cleanup(server.Close)
	peer, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer peer.Close()
	c := <-connections
	if err = peer.SetReadDeadline(time.Now().Add(5 * time.Second)); err != nil {
		t.Fatal(err)
	}
	_, data, readErr := peer.ReadMessage()
	if readErr == nil {
		t.Fatalf("validation unavailability invented a business frame: %s", data)
	}
	if n, ok := readErr.(net.Error); ok && n.Timeout() {
		t.Fatal("unverified connection remained open")
	}
	select {
	case <-c.done:
	case <-time.After(time.Second):
		t.Fatal("connection not retired")
	}
	select {
	case err = <-returned:
	case <-time.After(time.Second):
		t.Fatal("watch failed to return original validation result")
	}
	return err
}

func TestWatchDefaultPGXRefusalClosesWithoutRevocation(t *testing.T) {
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	port := listener.Addr().(*net.TCPAddr).Port
	listener.Close()
	h, cl, token := watchFixture(t, watchPool(t, "127.0.0.1", port))
	result := observeWatchFailure(t, h, cl, token)
	var connect *pgconn.ConnectError
	var network net.Error
	if !errors.As(result, &connect) || !errors.As(result, &network) || !watchTransportFailure(result) {
		t.Fatalf("default refused connection lost its real transport result: %T %v", result, result)
	}
	if _, auth := result.(shared.Error); auth {
		t.Fatal("DB unavailable became authentication fact")
	}
	t.Log("actual default pgx refusal -> watch returns original transport root; actual WS closes without session.revoked")
}

// Default pgx builds the actual single/multiple connection-attempt error tree.
// This endpoint is a controlled PostgreSQL wire producer, not a live database.
func watchInternalEndpoint(t *testing.T) int {
	t.Helper()
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	done := make(chan struct{})
	go func() {
		defer close(done)
		for {
			conn, err := listener.Accept()
			if err != nil {
				return
			}
			func() {
				defer conn.Close()
				conn.SetDeadline(time.Now().Add(2 * time.Second))
				var header [4]byte
				if _, err := io.ReadFull(conn, header[:]); err != nil {
					return
				}
				length := binary.BigEndian.Uint32(header[:])
				if length < 8 || length > 65536 {
					return
				}
				if _, err := io.CopyN(io.Discard, conn, int64(length-4)); err != nil {
					return
				}
				payload := []byte("SFATAL\x00CXX000\x00Mcontrolled internal PostgreSQL failure\x00\x00")
				packet := make([]byte, 5+len(payload))
				packet[0] = 'E'
				binary.BigEndian.PutUint32(packet[1:5], uint32(4+len(payload)))
				copy(packet[5:], payload)
				conn.Write(packet)
			}()
		}
	}()
	t.Cleanup(func() { listener.Close(); <-done })
	return listener.Addr().(*net.TCPAddr).Port
}

func TestWatchActualClosedPoolReturnsExactInternalRoot(t *testing.T) {
	pool := watchPool(t, "127.0.0.1", 1)
	pool.Close()
	h, cl, token := watchFixture(t, pool)
	_, original := h.auth.authenticate(context.Background(), token)
	if original == nil || watchTransportFailure(original) {
		t.Fatal("actual closed-pool producer was not an internal failure")
	}
	result := observeWatchFailure(t, h, cl, token)
	if result != original || watchTransportFailure(result) {
		t.Fatal("watch replaced or recovered actual closed-pool root")
	}
	t.Log("actual closed pool remains exact internal error after fail-closed transport retirement; no invented auth cause")
}

func TestWatchDefaultPGXInternalAndMixedRootsRemainFailures(t *testing.T) {
	for _, host := range []string{"127.0.0.1", "localhost"} {
		t.Run(host, func(t *testing.T) {
			if host == "localhost" {
				addresses, err := net.LookupHost(host)
				if err != nil {
					t.Fatal(err)
				}
				v4, v6 := false, false
				for _, address := range addresses {
					ip := net.ParseIP(address)
					if ip != nil && ip.IsLoopback() {
						if ip.To4() != nil {
							v4 = true
						} else {
							v6 = true
						}
					}
				}
				if !v4 || !v6 {
					t.Skipf("default dual-address pgx producer unavailable: %v", addresses)
				}
			}
			h, cl, token := watchFixture(t, watchPool(t, host, watchInternalEndpoint(t)))
			result := observeWatchFailure(t, h, cl, token)
			var internal *pgconn.PgError
			var connect *pgconn.ConnectError
			if !errors.As(result, &connect) || !errors.As(result, &internal) || internal.Code != "XX000" || watchTransportFailure(result) {
				t.Fatalf("watch hid actual internal root: %T %v", result, result)
			}
			if host == "localhost" {
				var network net.Error
				if !errors.As(result, &network) {
					t.Fatal("default mixed tree missing real network branch")
				}
			}
			for _, failure := range []error{result, fmt.Errorf("actual wrapper: %w", result), errors.Join(context.DeadlineExceeded, result)} {
				if watchTransportFailure(failure) || !errors.Is(failure, result) {
					t.Fatal("wrapped/joined internal root became known transport")
				}
			}
		})
	}
}

func TestWatchTransportClassificationKeepsEveryBranch(t *testing.T) {
	network := &net.OpError{Op: "dial", Net: "tcp", Err: os.ErrDeadlineExceeded}
	unknown := errors.New("unknown internal fixture")
	for _, tc := range []struct {
		name  string
		err   error
		known bool
	}{
		{"network", network, true}, {"deadline", context.DeadlineExceeded, true}, {"wrapped-network", fmt.Errorf("wrapped: %w", network), true}, {"all-network", errors.Join(network, context.DeadlineExceeded), true},
		{"unknown", unknown, false}, {"cancelled", context.Canceled, false}, {"nil", nil, false}, {"mixed", errors.Join(network, unknown), false}, {"nested-mixed", fmt.Errorf("wrapped: %w", errors.Join(context.DeadlineExceeded, errors.Join(network, unknown))), false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if got := watchTransportFailure(tc.err); got != tc.known {
				t.Fatalf("known=%v want %v", got, tc.known)
			}
		})
	}
}

func TestWatchExpiredCredentialClosesWithoutRevocation(t *testing.T) {
	h, cl, token := watchFixture(t, nil)
	h.auth.codec.Now = func() time.Time { return time.Now().Add(2 * time.Hour) }
	returned := make(chan error, 1)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ws, err := (&websocket.Upgrader{}).Upgrade(w, r, nil)
		if err != nil {
			return
		}
		c := &connection{ws: ws, done: make(chan struct{}), bound: &cl, token: token}
		h.add(cl.SessionID, c)
		returned <- h.watch(c, cl)
	}))
	defer server.Close()
	peer, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer peer.Close()
	peer.SetReadDeadline(time.Now().Add(5 * time.Second))
	if _, _, err = peer.ReadMessage(); !websocket.IsCloseError(err, websocket.CloseAbnormalClosure, websocket.CloseNormalClosure) {
		t.Fatalf("want connection closure without a Session event, got %v", err)
	}
	if err = <-returned; err != nil {
		t.Fatal(err)
	}
}

// A real bound serve->watch goroutine must not silently return an internal DB
// failure. The parent owns and drops this disposable test-only schema.
func TestPostgresWatchInternalFailureEscapesActualGoroutine(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with disposable PostgreSQL")
	}
	schema := os.Getenv("IM_WATCH_PANIC_SCHEMA")
	if schema != "" {
		cfg, err := pgxpool.ParseConfig("")
		if err != nil {
			t.Fatal(err)
		}
		cfg.ConnConfig.RuntimeParams["search_path"] = schema
		db, err := pgxpool.NewWithConfig(context.Background(), cfg)
		if err != nil {
			t.Fatal(err)
		}
		defer db.Close()
		h, cl, token := watchFixture(t, db)
		server := httptest.NewServer(http.HandlerFunc(h.serve))
		defer server.Close()
		peer, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
		if err != nil {
			t.Fatal(err)
		}
		defer peer.Close()
		id := "10000000-0000-4000-8000-000000000001"
		if err = peer.WriteJSON(frame("auth.bind", id, map[string]string{"accessToken": token})); err != nil {
			t.Fatal(err)
		}
		var ack struct {
			Type    string `json:"type"`
			Payload struct {
				Status string `json:"status"`
			} `json:"payload"`
		}
		if err = peer.ReadJSON(&ack); err != nil {
			t.Fatal(err)
		}
		if ack.Type != "auth.ack" || ack.Payload.Status != "bound" {
			t.Fatalf("fixture did not bind: %+v", ack)
		}
		if _, err = db.Exec(context.Background(), `ALTER TABLE sessions ALTER COLUMN session_epoch TYPE text USING 'not-an-epoch'`); err != nil {
			t.Fatal(err)
		}
		peer.SetReadDeadline(time.Now().Add(5 * time.Second))
		_, _, _ = peer.ReadMessage()
		time.Sleep(100 * time.Millisecond)
		t.Fatalf("actual watch goroutine did not fail for invalid authoritative epoch; %s", cl.SessionID)
	}
	db, err := pgxpool.New(context.Background(), "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	uid, err := shared.UUID()
	if err != nil {
		t.Fatal(err)
	}
	schema = "watch_" + strings.ReplaceAll(uid, "-", "")
	if _, err = db.Exec(context.Background(), "CREATE SCHEMA "+schema); err != nil {
		t.Fatal(err)
	}
	defer func() {
		if _, err := db.Exec(context.Background(), "DROP SCHEMA "+schema+" CASCADE"); err != nil {
			t.Error(err)
		}
	}()
	_, cl, _ := watchFixture(t, nil)
	if _, err = db.Exec(context.Background(), "CREATE TABLE "+schema+".sessions(user_id uuid,session_id uuid,client_type text,session_epoch bigint,status text,expires_at timestamptz)"); err != nil {
		t.Fatal(err)
	}
	if _, err = db.Exec(context.Background(), "INSERT INTO "+schema+".sessions VALUES($1,$2,'DESKTOP',1,'ACTIVE',now()+interval '1 hour')", cl.UserID, cl.SessionID); err != nil {
		t.Fatal(err)
	}
	exe, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	command := exec.CommandContext(ctx, exe, "-test.run=^TestPostgresWatchInternalFailureEscapesActualGoroutine$")
	command.Env = append(os.Environ(), "IM_WATCH_PANIC_SCHEMA="+schema)
	output, err := command.CombinedOutput()
	if err == nil || ctx.Err() != nil {
		t.Fatalf("expected actual goroutine panic, got %v: %s", err, output)
	}
	if !strings.Contains(string(output), "panic: ERROR: cached plan must not change result type (SQLSTATE 0A000)") || !strings.Contains(string(output), "created by im-platform/backend/go/gateway.(*hub).serve") {
		t.Fatalf("internal root lost in actual goroutine result: %s", output)
	}
	t.Log("actual successful auth.bind then PostgreSQL invalid epoch -> watch closes transport and original cached-plan PgError0A000 escapes actual serve goroutine; child failure expected")
}

// Exercise the actual serve -> bind -> watch -> socket-close lifecycle. The
// controlled wire endpoint supplies one session row, then stalls the next pgx
// constructor. It is not a database or a replacement for the live PG suite.
func TestServeJoinsInflightWatchBeforePoolClose(t *testing.T) {
	if os.Getenv("IM_WATCH_JOIN_CHILD") != "1" {
		exe, err := os.Executable()
		if err != nil {
			t.Fatal(err)
		}
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		command := exec.CommandContext(ctx, exe, "-test.run=^TestServeJoinsInflightWatchBeforePoolClose$", "-test.v")
		command.Env = append(os.Environ(), "IM_WATCH_JOIN_CHILD=1")
		output, err := command.CombinedOutput()
		if err != nil || ctx.Err() != nil {
			t.Fatalf("serve returned before its watch retired, allowing pool teardown to cancel it: %v: %s", err, output)
		}
		if !strings.Contains(string(output), "handler completed before pool released; in-flight watch retired") {
			t.Fatalf("child did not complete the lifecycle: %s", output)
		}
		return
	}
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()
	cfg, err := pgxpool.ParseConfig(fmt.Sprintf("host=127.0.0.1 port=%d user=public_fixture dbname=public_fixture sslmode=disable", listener.Addr().(*net.TCPAddr).Port))
	if err != nil {
		t.Fatal(err)
	}
	cfg.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol
	// Every acquisition starts a fresh connection; the second constructor is
	// exactly the ownership boundary involved in the hosted cancellation failure.
	cfg.AfterRelease = func(*pgx.Conn) bool { return false }
	pool, err := pgxpool.NewWithConfig(context.Background(), cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer pool.Close()
	h, cl, token := watchFixture(t, pool)
	startup := make(chan struct{})
	endpointDone := make(chan error, 1)
	go func() {
		endpointDone <- func() error {
			first, err := listener.Accept()
			if err != nil {
				return err
			}
			defer first.Close()
			backend := pgproto3.NewBackend(first, first)
			if _, err = backend.ReceiveStartupMessage(); err != nil {
				return err
			}
			backend.Send(&pgproto3.AuthenticationOk{})
			backend.Send(&pgproto3.ParameterStatus{Name: "client_encoding", Value: "UTF8"})
			backend.Send(&pgproto3.ParameterStatus{Name: "standard_conforming_strings", Value: "on"})
			backend.Send(&pgproto3.ReadyForQuery{TxStatus: 'I'})
			if err = backend.Flush(); err != nil {
				return err
			}
			query, err := backend.Receive()
			if err != nil {
				return err
			}
			if _, ok := query.(*pgproto3.Query); !ok {
				return fmt.Errorf("expected binding session query, got %T", query)
			}
			backend.Send(&pgproto3.RowDescription{Fields: []pgproto3.FieldDescription{
				{Name: []byte("session_id"), DataTypeOID: 25, DataTypeSize: -1},
				{Name: []byte("client_type"), DataTypeOID: 25, DataTypeSize: -1},
				{Name: []byte("session_epoch"), DataTypeOID: 20, DataTypeSize: 8},
				{Name: []byte("status"), DataTypeOID: 25, DataTypeSize: -1},
				{Name: []byte("expires_at"), DataTypeOID: 1184, DataTypeSize: 8},
			}})
			backend.Send(&pgproto3.DataRow{Values: [][]byte{[]byte(cl.SessionID), []byte(cl.ClientType), []byte("1"), []byte("ACTIVE"), []byte(time.Now().Add(time.Hour).UTC().Format("2006-01-02 15:04:05.999999999Z07:00"))}})
			backend.Send(&pgproto3.CommandComplete{CommandTag: []byte("SELECT 1")})
			backend.Send(&pgproto3.ReadyForQuery{TxStatus: 'I'})
			if err = backend.Flush(); err != nil {
				return err
			}
			second, err := listener.Accept()
			if err != nil {
				return err
			}
			defer second.Close()
			if _, err = pgproto3.NewBackend(second, second).ReceiveStartupMessage(); err != nil {
				return err
			}
			close(startup)
			_, err = io.Copy(io.Discard, second)
			return err
		}()
	}()
	handlerDone := make(chan struct{})
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer close(handlerDone)
		h.serve(w, r)
	}))
	defer server.Close()
	peer, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer peer.Close()
	if err = peer.SetReadDeadline(time.Now().Add(5 * time.Second)); err != nil {
		t.Fatal(err)
	}
	if err = peer.WriteJSON(frame("auth.bind", "10000000-0000-4000-8000-000000000001", map[string]string{"accessToken": token})); err != nil {
		t.Fatal(err)
	}
	var ack struct {
		Type    string `json:"type"`
		Payload struct {
			Status string `json:"status"`
		} `json:"payload"`
	}
	if err = peer.ReadJSON(&ack); err != nil {
		t.Fatal(err)
	}
	if ack.Type != "auth.ack" || ack.Payload.Status != "bound" {
		t.Fatalf("fixture did not bind: %+v", ack)
	}
	select {
	case <-startup:
	case err := <-endpointDone:
		t.Fatalf("endpoint failed before watch constructor: %v", err)
	case <-time.After(5 * time.Second):
		t.Fatal("watch did not start constructor")
	}
	if err = peer.Close(); err != nil {
		t.Fatal(err)
	}
	select {
	case <-handlerDone:
	case <-time.After(5 * time.Second):
		t.Fatal("handler did not finish its watch")
	}
	pool.Close()
	if err = <-endpointDone; err != nil {
		t.Fatal(err)
	}
	t.Log("handler completed before pool released; in-flight watch retired")
}
