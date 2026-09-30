package shared

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"strings"
	"time"
)

type Claims struct {
	UserID       string `json:"user_id"`
	SessionID    string `json:"session_id"`
	ClientType   string `json:"client_type"`
	SessionEpoch int64  `json:"session_epoch"`
	IssuedAt     int64  `json:"iat"`
	ExpiresAt    int64  `json:"exp"`
}

type Error struct {
	Status  int
	Code    string
	Message string
}

func (e Error) Error() string { return e.Code }

func Fail(status int, code, message string) error { return Error{status, code, message} }

type Codec struct {
	Key []byte
	Now func() time.Time
}

func RandomToken(n int) (string, error) {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(b), nil
}

func UUID() (string, error) {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	b[6] = b[6]&0x0f | 0x40
	b[8] = b[8]&0x3f | 0x80
	h := hex.EncodeToString(b)
	return h[:8] + "-" + h[8:12] + "-" + h[12:16] + "-" + h[16:20] + "-" + h[20:], nil
}

func HashToken(token string) string {
	h := sha256.Sum256([]byte(token))
	return hex.EncodeToString(h[:])
}

// Prehash keeps bcrypt's 72-byte input limit from truncating valid passwords.
func (s *Codec) Sign(c Claims) (string, error) {
	head := base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"HS256","typ":"JWT"}`))
	payload, err := json.Marshal(c)
	if err != nil {
		return "", err
	}
	data := head + "." + base64.RawURLEncoding.EncodeToString(payload)
	mac := hmac.New(sha256.New, s.Key)
	mac.Write([]byte(data))
	return data + "." + base64.RawURLEncoding.EncodeToString(mac.Sum(nil)), nil
}

func (s *Codec) Parse(token string) (Claims, error) {
	var c Claims
	parts := strings.Split(token, ".")
	if len(parts) != 3 || parts[0] != base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"HS256","typ":"JWT"}`)) {
		return c, Fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	mac := hmac.New(sha256.New, s.Key)
	mac.Write([]byte(parts[0] + "." + parts[1]))
	sig, err := base64.RawURLEncoding.DecodeString(parts[2])
	if err != nil || !hmac.Equal(sig, mac.Sum(nil)) {
		return c, Fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	payload, err := base64.RawURLEncoding.DecodeString(parts[1])
	if err != nil || json.Unmarshal(payload, &c) != nil || c.UserID == "" || c.SessionID == "" || c.SessionEpoch < 1 || !ValidClient(c.ClientType) || c.IssuedAt < 1 || c.ExpiresAt <= c.IssuedAt {
		return c, Fail(401, "AUTH_TOKEN_INVALID", "Access token is invalid.")
	}
	if s.Now().Unix() >= c.ExpiresAt {
		return c, Fail(401, "AUTH_TOKEN_EXPIRED", "Access token has expired.")
	}
	return c, nil
}

func ValidClient(t string) bool { return t == "WEB" || t == "DESKTOP" || t == "MOBILE" }
