package shared

import (
	"os"
	"strings"
	"testing"
)

func TestConfigReadsExternalCredentialFiles(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(dir+"/pg_password", []byte("local-test-password\n"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(dir+"/jwt_key", []byte("test-only-signing-key-at-least-32-bytes\n"), 0600); err != nil {
		t.Fatal(err)
	}
	config := []byte(`{"postgresHost":"localhost","postgresPort":5432,"postgresUser":"test","postgresDatabase":"test","postgresPasswordFile":"pg_password","jwtSigningKeyFile":"jwt_key","coreUrl":"http://localhost:8080","natsUrl":"nats://localhost:4222"}`)
	if err := os.WriteFile(dir+"/config.json", config, 0600); err != nil {
		t.Fatal(err)
	}
	_, key, pg, err := ReadConfig(dir + "/config.json")
	if err != nil {
		t.Fatal(err)
	}
	if string(key) != "test-only-signing-key-at-least-32-bytes" || pg.ConnConfig.Password != "local-test-password" {
		t.Fatal("credential files were not loaded")
	}
	if strings.Contains(string(config), "local-test-password") || strings.Contains(string(config), string(key)) {
		t.Fatal("credential embedded in configuration")
	}
	if err := os.Remove(dir + "/jwt_key"); err != nil {
		t.Fatal(err)
	}
	if _, _, _, err := ReadConfig(dir + "/config.json"); err == nil {
		t.Fatal("missing signing key accepted")
	}
}
