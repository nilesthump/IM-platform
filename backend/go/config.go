package main

import (
	"encoding/json"
	"errors"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
)

// Runtime settings are read from an operator-provided file. The file names the
// credential files; it never contains the PostgreSQL password or JWT key.
type runtimeConfig struct {
	PostgresHost         string `json:"postgresHost"`
	PostgresPort         uint16 `json:"postgresPort"`
	PostgresUser         string `json:"postgresUser"`
	PostgresDatabase     string `json:"postgresDatabase"`
	PostgresPasswordFile string `json:"postgresPasswordFile"`
	JWTSigningKeyFile    string `json:"jwtSigningKeyFile"`
	CoreURL              string `json:"coreUrl"`
	NATSURL              string `json:"natsUrl"`
}

func readConfig(path string) (runtimeConfig, []byte, *pgxpool.Config, error) {
	var cfg runtimeConfig
	if path == "" {
		return cfg, nil, nil, errors.New("IM_CONFIG_FILE is required")
	}
	f, err := os.Open(path)
	if err != nil {
		return cfg, nil, nil, err
	}
	defer f.Close()
	d := json.NewDecoder(f)
	d.DisallowUnknownFields()
	if err = d.Decode(&cfg); err != nil {
		return cfg, nil, nil, err
	}
	if d.Decode(new(any)) != io.EOF {
		return cfg, nil, nil, errors.New("runtime configuration has trailing content")
	}
	if cfg.PostgresHost == "" || cfg.PostgresPort == 0 || cfg.PostgresUser == "" || cfg.PostgresDatabase == "" || cfg.PostgresPasswordFile == "" || cfg.JWTSigningKeyFile == "" || cfg.CoreURL == "" || cfg.NATSURL == "" {
		return cfg, nil, nil, errors.New("runtime configuration is incomplete")
	}
	resolve := func(p string) string {
		if filepath.IsAbs(p) {
			return p
		}
		return filepath.Join(filepath.Dir(path), p)
	}
	password, err := os.ReadFile(resolve(cfg.PostgresPasswordFile))
	if err != nil {
		return cfg, nil, nil, err
	}
	key, err := os.ReadFile(resolve(cfg.JWTSigningKeyFile))
	if err != nil {
		return cfg, nil, nil, err
	}
	passwordText := strings.TrimSpace(string(password))
	key = []byte(strings.TrimSpace(string(key)))
	if passwordText == "" || len(key) < 32 {
		return cfg, nil, nil, errors.New("runtime credentials are invalid")
	}
	pg, err := pgxpool.ParseConfig("")
	if err != nil {
		return cfg, nil, nil, err
	}
	pg.ConnConfig.Host = cfg.PostgresHost
	pg.ConnConfig.Port = cfg.PostgresPort
	pg.ConnConfig.User = cfg.PostgresUser
	pg.ConnConfig.Database = cfg.PostgresDatabase
	pg.ConnConfig.Password = passwordText
	return cfg, key, pg, nil
}
