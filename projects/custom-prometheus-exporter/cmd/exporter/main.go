package main

import (
	"context"
	"flag"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/example/custom-prometheus-exporter/internal/collector"
	"github.com/example/custom-prometheus-exporter/internal/config"
	"github.com/example/custom-prometheus-exporter/internal/server"
)

func main() {
	configPath := flag.String("config", "configs/config.yaml", "Path to configuration file")
	flag.Parse()

	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))

	cfg, err := config.Load(*configPath)
	if err != nil {
		logger.Error("failed to load config", "err", err)
		os.Exit(1)
	}

	logger = newLogger(cfg.Logging.Level)

	registry := prometheus.NewRegistry()
	registry.MustRegister(prometheus.NewProcessCollector(prometheus.ProcessCollectorOpts{}))
	registry.MustRegister(prometheus.NewGoCollector())

	exporter := collector.New(cfg, logger)
	exporter.Register(registry)

	mux := http.NewServeMux()
	mux.Handle("/metrics", promhttp.HandlerFor(registry, promhttp.HandlerOpts{}))
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	srv := server.New(cfg.Server.Address, cfg.Server.Port, mux)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	go func() {
		logger.Info("starting server", "address", cfg.Server.Address, "port", cfg.Server.Port)
		if err := srv.Start(); err != nil && err != http.ErrServerClosed {
			logger.Error("server failed", "err", err)
			stop()
		}
	}()

	ticker := time.NewTicker(cfg.Scrape.Interval)
	defer ticker.Stop()

	exporter.Scrape(context.Background())

	for {
		select {
		case <-ctx.Done():
			shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()
			if err := srv.Shutdown(shutdownCtx); err != nil {
				logger.Error("shutdown error", "err", err)
			}
			logger.Info("shutdown complete")
			return
		case <-ticker.C:
			exporter.Scrape(context.Background())
		}
	}
}

func newLogger(level string) *slog.Logger {
	var lvl slog.Level
	switch level {
	case "debug":
		lvl = slog.LevelDebug
	case "warn":
		lvl = slog.LevelWarn
	case "error":
		lvl = slog.LevelError
	default:
		lvl = slog.LevelInfo
	}
	return slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: lvl}))
}
