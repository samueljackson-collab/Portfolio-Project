package config

import (
	"errors"
	"fmt"
	"os"
	"strconv"
	"time"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Server       ServerConfig       `yaml:"server"`
	Logging      LoggingConfig      `yaml:"logging"`
	Scrape       ScrapeConfig       `yaml:"scrape"`
	Labels       map[string]string  `yaml:"labels"`
	APIEndpoints []APIEndpoint      `yaml:"api_endpoints"`
	FileMetrics  []FileMetric       `yaml:"file_metrics"`
	SQLMetrics   []SQLMetric        `yaml:"sql_metrics"`
	FeatureFlags FeatureFlags       `yaml:"feature_flags"`
	MetricFilter MetricFilterConfig `yaml:"metric_filter"`
}

type ServerConfig struct {
	Address string `yaml:"address"`
	Port    int    `yaml:"port"`
}

type LoggingConfig struct {
	Level string `yaml:"level"`
}

type ScrapeConfig struct {
	Interval time.Duration `yaml:"interval"`
}

type APIEndpoint struct {
	Name        string            `yaml:"name"`
	URL         string            `yaml:"url"`
	Method      string            `yaml:"method"`
	Timeout     time.Duration     `yaml:"timeout"`
	ValuePath   string            `yaml:"value_path"`
	Labels      map[string]string `yaml:"labels"`
	Headers     map[string]string `yaml:"headers"`
	MetricType  string            `yaml:"metric_type"`
	BucketHints []float64         `yaml:"bucket_hints"`
}

type FileMetric struct {
	Name       string            `yaml:"name"`
	Path       string            `yaml:"path"`
	Labels     map[string]string `yaml:"labels"`
	TrimSpace  bool              `yaml:"trim_space"`
	MetricType string            `yaml:"metric_type"`
}

type SQLMetric struct {
	Name       string            `yaml:"name"`
	Driver     string            `yaml:"driver"`
	DSN        string            `yaml:"dsn"`
	Query      string            `yaml:"query"`
	Labels     map[string]string `yaml:"labels"`
	MetricType string            `yaml:"metric_type"`
}

type FeatureFlags struct {
	EnableAPI   bool `yaml:"enable_api"`
	EnableFiles bool `yaml:"enable_files"`
	EnableSQL   bool `yaml:"enable_sql"`
}

type MetricFilterConfig struct {
	Disabled []string `yaml:"disabled"`
}

func Load(path string) (*Config, error) {
	payload, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config: %w", err)
	}

	cfg := &Config{}
	if err := yaml.Unmarshal(payload, cfg); err != nil {
		return nil, fmt.Errorf("parse config: %w", err)
	}

	applyDefaults(cfg)
	applyEnvOverrides(cfg)

	if cfg.Server.Port == 0 {
		return nil, errors.New("server.port is required")
	}

	return cfg, nil
}

func applyDefaults(cfg *Config) {
	if cfg.Server.Address == "" {
		cfg.Server.Address = "0.0.0.0"
	}
	if cfg.Logging.Level == "" {
		cfg.Logging.Level = "info"
	}
	if cfg.Scrape.Interval == 0 {
		cfg.Scrape.Interval = 30 * time.Second
	}
}

func applyEnvOverrides(cfg *Config) {
	if value, ok := os.LookupEnv("EXPORTER_ADDRESS"); ok {
		cfg.Server.Address = value
	}
	if value, ok := os.LookupEnv("EXPORTER_PORT"); ok {
		if port, err := strconv.Atoi(value); err == nil {
			cfg.Server.Port = port
		}
	}
	if value, ok := os.LookupEnv("EXPORTER_LOG_LEVEL"); ok {
		cfg.Logging.Level = value
	}
	if value, ok := os.LookupEnv("EXPORTER_SCRAPE_INTERVAL"); ok {
		if interval, err := time.ParseDuration(value); err == nil {
			cfg.Scrape.Interval = interval
		}
	}
	if value, ok := os.LookupEnv("EXPORTER_ENABLE_API"); ok {
		cfg.FeatureFlags.EnableAPI = value == "true"
	}
	if value, ok := os.LookupEnv("EXPORTER_ENABLE_FILES"); ok {
		cfg.FeatureFlags.EnableFiles = value == "true"
	}
	if value, ok := os.LookupEnv("EXPORTER_ENABLE_SQL"); ok {
		cfg.FeatureFlags.EnableSQL = value == "true"
	}
}
