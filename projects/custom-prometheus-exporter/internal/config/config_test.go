package config

import (
	"os"
	"testing"
)

func TestLoadConfig(t *testing.T) {
	content := []byte(`server:
  address: "0.0.0.0"
  port: 9108
logging:
  level: "debug"
scrape:
  interval: 15s
feature_flags:
  enable_api: true
`)
	file, err := os.CreateTemp(t.TempDir(), "config-*.yaml")
	if err != nil {
		t.Fatalf("create temp: %v", err)
	}
	if _, err := file.Write(content); err != nil {
		t.Fatalf("write config: %v", err)
	}
	if err := file.Close(); err != nil {
		t.Fatalf("close config: %v", err)
	}

	cfg, err := Load(file.Name())
	if err != nil {
		t.Fatalf("load config: %v", err)
	}
	if cfg.Server.Port != 9108 {
		t.Fatalf("expected port 9108, got %d", cfg.Server.Port)
	}
	if cfg.Logging.Level != "debug" {
		t.Fatalf("expected log level debug, got %s", cfg.Logging.Level)
	}
	if cfg.Scrape.Interval.String() != "15s" {
		t.Fatalf("expected 15s interval, got %s", cfg.Scrape.Interval)
	}
}
