package main

import (
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/bcrypt"
)

const accessTTL = 900
const refreshTTL = 2592000

var usernamePattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]*$`)

type authService struct {
	db     *pgxpool.Pool
	key    []byte
	now    func() time.Time
	revoke func(string, string)
}

type clientInput struct {
	ClientType      string `json:"clientType"`
	DeviceID        string `json:"deviceId"`
	ClientVersion   string `json:"clientVersion"`
	ProtocolVersion string `json:"protocolVersion"`
}

type loginInput struct {
	Username string `json:"username"`
	Password string `json:"password"`
	clientInput
}

type registerInput struct {
	Username    string `json:"username"`
	Password    string `json:"password"`
	DisplayName string `json:"displayName"`
}

type refreshInput struct {
	clientInput
	RefreshToken string `json:"refreshToken,omitempty"`
}

type claims struct {
	UserID       string `json:"user_id"`
	SessionID    string `json:"session_id"`
	ClientType   string `json:"client_type"`
	SessionEpoch int64  `json:"session_epoch"`
	IssuedAt     int64  `json:"iat"`
	ExpiresAt    int64  `json:"exp"`
}

type apiError struct {
	status  int
	code    string
	message string
}

func (e apiError) Error() string { return e.code }

func fail(status int, code, message string) error { return apiError{status, code, message} }

func randomToken(n int) (string, error) {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(b), nil
}

func uuid() (string, error) {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	b[6] = b[6]&0x0f | 0x40
	b[8] = b[8]&0x3f | 0x80
	h := hex.EncodeToString(b)
	return h[:8] + "-" + h[8:12] + "-" + h[12:16] + "-" + h[16:20] + "-" + h[20:], nil
}

func hashToken(token string) string {
	h := sha256.Sum256([]byte(token))
	return hex.EncodeToString(h[:])
}

// Prehash keeps bcrypt's 72-byte input limit from truncating valid passwords.
func passwordMaterial(password string) []byte {
	h := sha256.Sum256([]byte("im-password-v1:" + password))
	return []byte(hex.EncodeToString(h[:]))
}

func (s *authService) sign(c claims) (string, error) {
	head := base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"HS256","typ":"JWT"}`))
	payload, err := json.Marshal(c)
	if err != nil {
		return "", err
	}
	data := head + "." + base64.RawURLEncoding.EncodeToString(payload)
	mac := hmac.New(sha256.New, s.key)
	mac.Write([]byte(data))
	return data + "." + base64.RawURLEncoding.EncodeToString(mac.Sum(nil)), nil
}

func (s *authService) parse(token string) (claims, error) {
	var c claims
	parts := strings.Split(token, ".")
	if len(parts) != 3 || parts[0] != base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"HS256","typ":"JWT"}`)) {
		return c, fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	mac := hmac.New(sha256.New, s.key)
	mac.Write([]byte(parts[0] + "." + parts[1]))
	sig, err := base64.RawURLEncoding.DecodeString(parts[2])
	if err != nil || !hmac.Equal(sig, mac.Sum(nil)) {
		return c, fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	payload, err := base64.RawURLEncoding.DecodeString(parts[1])
	if err != nil || json.Unmarshal(payload, &c) != nil || c.UserID == "" || c.SessionID == "" || c.SessionEpoch < 1 || !validClient(c.ClientType) || c.IssuedAt < 1 || c.ExpiresAt <= c.IssuedAt {
		return c, fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	if s.now().Unix() >= c.ExpiresAt {
		return c, fail(401, "AUTH_TOKEN_EXPIRED", "Access token has expired.")
	}
	return c, nil
}

func (s *authService) authenticate(ctx context.Context, token string) (claims, error) {
	c, err := s.parse(token)
	if err != nil {
		return c, err
	}
	var sid, typ, status string
	var epoch int64
	var expiry time.Time
	err = s.db.QueryRow(ctx, `SELECT session_id, client_type, session_epoch, status, expires_at FROM sessions WHERE user_id=$1 AND client_type=$2`, c.UserID, c.ClientType).Scan(&sid, &typ, &epoch, &status, &expiry)
	if errors.Is(err, pgx.ErrNoRows) {
		return c, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if err != nil {
		return c, err
	}
	if status != "ACTIVE" || !expiry.After(s.now()) {
		return c, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if epoch != c.SessionEpoch {
		return c, fail(401, "AUTH_SESSION_EPOCH_STALE", "Access token carries a stale session epoch.")
	}
	if sid != c.SessionID || typ != c.ClientType {
		return c, fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Access token does not match the active client session.")
	}
	return c, nil
}

func validClient(t string) bool { return t == "WEB" || t == "DESKTOP" || t == "MOBILE" }
func (v clientInput) valid() bool {
	return validClient(v.ClientType) && len(v.DeviceID) > 0 && len(v.DeviceID) <= 256 && len(v.ClientVersion) > 0 && len(v.ClientVersion) <= 64
}

func decode(r *http.Request, dst any) error {
	r.Body = http.MaxBytesReader(nil, r.Body, 65536)
	d := json.NewDecoder(r.Body)
	d.DisallowUnknownFields()
	if err := d.Decode(dst); err != nil {
		return fail(400, "VALIDATION_FAILED", "Request body is invalid.")
	}
	if d.Decode(new(any)) != io.EOF {
		return fail(400, "VALIDATION_FAILED", "Request body is invalid.")
	}
	return nil
}

func requestID(_ *http.Request) string {
	id, _ := uuid()
	return id
}
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
func writeError(w http.ResponseWriter, r *http.Request, err error) {
	e := apiError{500, "INTERNAL_ERROR", "Internal server error."}
	var a apiError
	if errors.As(err, &a) {
		e = a
	}
	writeJSON(w, e.status, map[string]any{"error": map[string]string{"code": e.code, "message": e.message}, "requestId": requestID(r)})
}

func (s *authService) handler() http.Handler {
	m := http.NewServeMux()
	m.HandleFunc("POST /v1/auth/register", s.register)
	m.HandleFunc("POST /v1/auth/login", s.login)
	m.HandleFunc("POST /v1/auth/refresh/web", s.refreshWeb)
	m.HandleFunc("POST /v1/auth/refresh/native", s.refreshNative)
	m.HandleFunc("POST /v1/auth/logout", s.logout)
	m.HandleFunc("GET /v1/users/me", s.me)
	m.HandleFunc("GET /v1/users/search", s.search)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		for key := range r.URL.Query() {
			lower := strings.ToLower(key)
			if strings.Contains(lower, "token") || strings.Contains(lower, "password") || strings.Contains(lower, "secret") || lower == "authorization" || lower == "cookie" {
				writeError(w, r, fail(400, "VALIDATION_FAILED", "Authentication material is not permitted in query parameters."))
				return
			}
		}
		m.ServeHTTP(w, r)
	})
}

func (s *authService) register(w http.ResponseWriter, r *http.Request) {
	var v registerInput
	if err := decode(r, &v); err != nil {
		writeError(w, r, err)
		return
	}
	if len(v.Username) < 3 || len(v.Username) > 64 || !usernamePattern.MatchString(v.Username) || len(v.Password) < 12 || len(v.Password) > 256 || len(v.DisplayName) < 1 || len(v.DisplayName) > 128 {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "Registration fields are invalid."))
		return
	}
	password, err := bcrypt.GenerateFromPassword(passwordMaterial(v.Password), bcrypt.DefaultCost)
	if err != nil {
		writeError(w, r, err)
		return
	}
	id, err := uuid()
	if err != nil {
		writeError(w, r, err)
		return
	}
	name := strings.ToLower(v.Username)
	_, err = s.db.Exec(r.Context(), `INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,$3,$4)`, id, name, v.DisplayName, string(password))
	if err != nil {
		var pgerr *pgconn.PgError
		if errors.As(err, &pgerr) && pgerr.Code == "23505" {
			writeError(w, r, fail(409, "USERNAME_ALREADY_EXISTS", "Username already exists."))
			return
		}
		writeError(w, r, err)
		return
	}
	writeJSON(w, 201, map[string]any{"user": map[string]string{"userId": id, "username": name, "displayName": v.DisplayName}})
}

func (s *authService) login(w http.ResponseWriter, r *http.Request) {
	var v loginInput
	if err := decode(r, &v); err != nil {
		writeError(w, r, err)
		return
	}
	if !v.valid() || len(v.Username) < 3 || len(v.Username) > 64 || !usernamePattern.MatchString(v.Username) || len(v.Password) < 12 || len(v.Password) > 256 {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "Login fields are invalid."))
		return
	}
	if v.ProtocolVersion != "1" {
		writeError(w, r, fail(426, "PROTOCOL_VERSION_UNSUPPORTED", "Protocol version is unsupported."))
		return
	}
	var id, hash string
	err := s.db.QueryRow(r.Context(), `SELECT user_id,password_hash FROM users WHERE username=$1`, strings.ToLower(v.Username)).Scan(&id, &hash)
	if errors.Is(err, pgx.ErrNoRows) {
		writeError(w, r, fail(401, "AUTH_INVALID_CREDENTIALS", "Credentials are invalid."))
		return
	}
	if err != nil {
		writeError(w, r, err)
		return
	}
	if bcrypt.CompareHashAndPassword([]byte(hash), passwordMaterial(v.Password)) != nil {
		writeError(w, r, fail(401, "AUTH_INVALID_CREDENTIALS", "Credentials are invalid."))
		return
	}
	sid, epoch, replaced, refresh, err := s.newSession(r.Context(), id, v.clientInput)
	if err != nil {
		writeError(w, r, err)
		return
	}
	s.authResponse(w, r, id, sid, v.ClientType, epoch, replaced, refresh)
}

func (s *authService) newSession(ctx context.Context, userID string, v clientInput) (sid string, epoch int64, replaced bool, refresh string, err error) {
	tx, err := s.db.Begin(ctx)
	if err != nil {
		return
	}
	defer tx.Rollback(ctx)
	// Locking the user serializes the absent-row first login as well as replacement.
	var locked string
	err = tx.QueryRow(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, userID).Scan(&locked)
	if err != nil {
		return
	}
	var oldID, status string
	var prior int64
	err = tx.QueryRow(ctx, `SELECT session_id,session_epoch,status FROM sessions WHERE user_id=$1 AND client_type=$2`, userID, v.ClientType).Scan(&oldID, &prior, &status)
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		return
	}
	if errors.Is(err, pgx.ErrNoRows) {
		err = nil
	}
	epoch = prior + 1
	replaced = status == "ACTIVE"
	sid, err = uuid()
	if err != nil {
		return
	}
	refresh, err = randomToken(32)
	if err != nil {
		return
	}
	_, err = tx.Exec(ctx, `INSERT INTO sessions(user_id,client_type,session_id,session_epoch,refresh_token_hash,status,device_id,expires_at) VALUES($1,$2,$3,$4,$5,'ACTIVE',$6,$7)
	ON CONFLICT(user_id,client_type) DO UPDATE SET session_id=EXCLUDED.session_id,session_epoch=EXCLUDED.session_epoch,refresh_token_hash=EXCLUDED.refresh_token_hash,status='ACTIVE',device_id=EXCLUDED.device_id,expires_at=EXCLUDED.expires_at,updated_at=now()`, userID, v.ClientType, sid, epoch, hashToken(refresh), v.DeviceID, s.now().Add(refreshTTL*time.Second))
	if err != nil {
		return
	}
	if replaced {
		err = writeRevocation(ctx, tx, userID, oldID, "REPLACED")
		if err != nil {
			return
		}
	}
	err = tx.Commit(ctx)
	if err != nil {
		return
	}
	if replaced && s.revoke != nil {
		s.revoke(oldID, "REPLACED")
	}
	return
}

func writeRevocation(ctx context.Context, tx pgx.Tx, userID, sid, reason string) error {
	id, err := uuid()
	if err != nil {
		return err
	}
	payload := map[string]string{"sessionId": sid, "reason": reason}
	b, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	_, err = tx.Exec(ctx, `INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload) VALUES($1,'session',$2,'session.revoked',$3)`, id, sid, b)
	if err != nil {
		return err
	}
	_, err = tx.Exec(ctx, `INSERT INTO user_sync_events(user_id,event_type,payload) VALUES($1,'session.revoked',$2)`, userID, b)
	return err
}

func (s *authService) authResponse(w http.ResponseWriter, r *http.Request, userID, sid, typ string, epoch int64, replaced bool, refresh string) {
	now := s.now().Unix()
	access, err := s.sign(claims{userID, sid, typ, epoch, now, now + accessTTL})
	if err != nil {
		writeError(w, r, err)
		return
	}
	tokens := map[string]any{"accessToken": access, "accessTokenExpiresInSeconds": accessTTL}
	if typ == "WEB" {
		http.SetCookie(w, &http.Cookie{Name: "__Host-im_refresh", Value: refresh, Path: "/", Secure: true, HttpOnly: true, SameSite: http.SameSiteStrictMode, MaxAge: refreshTTL})
		tokens["refreshTokenDelivery"] = "HTTP_ONLY_SECURE_COOKIE"
	} else {
		tokens["refreshToken"] = refresh
		tokens["refreshTokenExpiresInSeconds"] = refreshTTL
		tokens["refreshTokenDelivery"] = "RESPONSE_BODY_FOR_OS_SECURE_STORAGE"
	}
	writeJSON(w, 200, map[string]any{"session": map[string]any{"sessionId": sid, "userId": userID, "clientType": typ, "sessionEpoch": epoch, "status": "ACTIVE"}, "tokens": tokens, "replacedExistingSession": replaced})
}

func (s *authService) refreshWeb(w http.ResponseWriter, r *http.Request) {
	var v refreshInput
	if err := decode(r, &v); err != nil {
		writeError(w, r, err)
		return
	}
	if v.ClientType != "WEB" || !v.valid() || v.RefreshToken != "" {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "WEB refresh fields are invalid."))
		return
	}
	if v.ProtocolVersion != "1" {
		writeError(w, r, fail(426, "PROTOCOL_VERSION_UNSUPPORTED", "Protocol version is unsupported."))
		return
	}
	cookie, err := r.Cookie("__Host-im_refresh")
	if err != nil || cookie.Value == "" {
		writeError(w, r, fail(401, "AUTH_REQUIRED", "WEB refresh cookie is required."))
		return
	}
	s.refresh(w, r, v.clientInput, cookie.Value)
}

func (s *authService) refreshNative(w http.ResponseWriter, r *http.Request) {
	var v refreshInput
	if err := decode(r, &v); err != nil {
		writeError(w, r, err)
		return
	}
	if v.RefreshToken == "" {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "refreshToken is required."))
		return
	}
	if v.ClientType == "WEB" || !v.valid() {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "Native refresh fields are invalid."))
		return
	}
	if v.ProtocolVersion != "1" {
		writeError(w, r, fail(426, "PROTOCOL_VERSION_UNSUPPORTED", "Protocol version is unsupported."))
		return
	}
	s.refresh(w, r, v.clientInput, v.RefreshToken)
}

func (s *authService) refresh(w http.ResponseWriter, r *http.Request, v clientInput, presented string) {
	ctx := r.Context()
	tx, err := s.db.Begin(ctx)
	if err != nil {
		writeError(w, r, err)
		return
	}
	defer tx.Rollback(ctx)
	var userID, sid, stored, status, device string
	var epoch int64
	var expiry time.Time
	err = tx.QueryRow(ctx, `SELECT user_id,session_id,refresh_token_hash,status,session_epoch,expires_at,device_id FROM sessions WHERE refresh_token_hash=$1 AND client_type=$2 FOR UPDATE`, hashToken(presented), v.ClientType).Scan(&userID, &sid, &stored, &status, &epoch, &expiry, &device)
	if errors.Is(err, pgx.ErrNoRows) {
		writeError(w, r, fail(401, "AUTH_REFRESH_REVOKED", "Refresh token has been revoked."))
		return
	}
	if err != nil {
		writeError(w, r, err)
		return
	}
	if status != "ACTIVE" || !expiry.After(s.now()) {
		writeError(w, r, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked."))
		return
	}
	if device != v.DeviceID {
		writeError(w, r, fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Refresh token does not match the active client session."))
		return
	}
	newRefresh, err := randomToken(32)
	if err != nil {
		writeError(w, r, err)
		return
	}
	_, err = tx.Exec(ctx, `UPDATE sessions SET refresh_token_hash=$1,expires_at=$2,updated_at=now() WHERE user_id=$3 AND client_type=$4`, hashToken(newRefresh), s.now().Add(refreshTTL*time.Second), userID, v.ClientType)
	if err == nil {
		err = tx.Commit(ctx)
	}
	if err != nil {
		writeError(w, r, err)
		return
	}
	s.authResponse(w, r, userID, sid, v.ClientType, epoch, false, newRefresh)
}

func bearer(r *http.Request) (string, error) {
	h := r.Header.Get("Authorization")
	if !strings.HasPrefix(h, "Bearer ") || len(h) <= 7 {
		return "", fail(401, "AUTH_REQUIRED", "Bearer access token is required.")
	}
	return strings.TrimPrefix(h, "Bearer "), nil
}

func (s *authService) logout(w http.ResponseWriter, r *http.Request) {
	token, err := bearer(r)
	if err != nil {
		writeError(w, r, err)
		return
	}
	c, err := s.authenticate(r.Context(), token)
	if err != nil {
		writeError(w, r, err)
		return
	}
	tx, err := s.db.Begin(r.Context())
	if err != nil {
		writeError(w, r, err)
		return
	}
	defer tx.Rollback(r.Context())
	var sid, status string
	var epoch int64
	err = tx.QueryRow(r.Context(), `SELECT session_id,status,session_epoch FROM sessions WHERE user_id=$1 AND client_type=$2 FOR UPDATE`, c.UserID, c.ClientType).Scan(&sid, &status, &epoch)
	if err != nil {
		writeError(w, r, err)
		return
	}
	if sid != c.SessionID || epoch != c.SessionEpoch || status != "ACTIVE" {
		writeError(w, r, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked."))
		return
	}
	_, err = tx.Exec(r.Context(), `UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL,updated_at=now() WHERE user_id=$1 AND client_type=$2`, c.UserID, c.ClientType)
	if err == nil {
		err = writeRevocation(r.Context(), tx, c.UserID, sid, "LOGOUT")
	}
	if err == nil {
		err = tx.Commit(r.Context())
	}
	if err != nil {
		writeError(w, r, err)
		return
	}
	if s.revoke != nil {
		s.revoke(sid, "LOGOUT")
	}
	w.WriteHeader(204)
}

func (s *authService) me(w http.ResponseWriter, r *http.Request) {
	token, err := bearer(r)
	if err != nil {
		writeError(w, r, err)
		return
	}
	c, err := s.authenticate(r.Context(), token)
	if err != nil {
		writeError(w, r, err)
		return
	}
	var name, display string
	err = s.db.QueryRow(r.Context(), `SELECT username,display_name FROM users WHERE user_id=$1`, c.UserID).Scan(&name, &display)
	if err != nil {
		writeError(w, r, err)
		return
	}
	writeJSON(w, 200, map[string]any{"user": map[string]string{"userId": c.UserID, "username": name, "displayName": display}})
}

func (s *authService) search(w http.ResponseWriter, r *http.Request) {
	token, err := bearer(r)
	if err != nil {
		writeError(w, r, err)
		return
	}
	if _, err = s.authenticate(r.Context(), token); err != nil {
		writeError(w, r, err)
		return
	}
	values := r.URL.Query()
	name := values.Get("username")
	if len(values) != 1 || len(values["username"]) != 1 || len(name) < 3 || len(name) > 64 || !usernamePattern.MatchString(name) {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "username is invalid."))
		return
	}
	var id, canonical, display string
	err = s.db.QueryRow(r.Context(), `SELECT user_id,username,display_name FROM users WHERE username=$1`, strings.ToLower(name)).Scan(&id, &canonical, &display)
	if errors.Is(err, pgx.ErrNoRows) {
		writeJSON(w, 200, map[string]any{"users": []any{}})
		return
	}
	if err != nil {
		writeError(w, r, err)
		return
	}
	writeJSON(w, 200, map[string]any{"users": []any{map[string]string{"userId": id, "username": canonical, "displayName": display}}})
}
