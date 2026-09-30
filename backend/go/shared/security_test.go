package shared

import (
	"testing"
	"time"
)

func TestTokenTamperAndExpiry(t *testing.T) {
	s := &Codec{Key: []byte("test-only-signing-key-at-least-32-bytes"), Now: func() time.Time { return time.Unix(1000, 0) }}
	c := Claims{"10000000-0000-4000-8000-000000000001", "50000000-0000-4000-8000-000000000001", "WEB", 1, 999, 1001}
	token, err := s.Sign(c)
	if err != nil {
		t.Fatal(err)
	}
	if _, err = s.Parse(token); err != nil {
		t.Fatal(err)
	}
	if _, err = s.Parse(token + "x"); err == nil {
		t.Fatal("tampered signature accepted")
	}
	s.Now = func() time.Time { return time.Unix(1001, 0) }
	if _, err = s.Parse(token); err == nil || err.(Error).Code != "AUTH_TOKEN_EXPIRED" {
		t.Fatalf("expired token: %v", err)
	}
}
