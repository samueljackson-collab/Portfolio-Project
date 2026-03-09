package collector

import (
	"context"
	"errors"
	"log/slog"
	"strings"
	"time"

	"github.com/prometheus/client_golang/prometheus"

	"github.com/example/custom-prometheus-exporter/internal/config"
)

type Exporter struct {
	cfg      *config.Config
	logger   *slog.Logger
	disabled map[string]struct{}
	metrics  *ExporterMetrics
	api      *APICollector
	files    *FileCollector
	sql      *SQLCollector
}

type ExporterMetrics struct {
	Up                 prometheus.Gauge
	LastScrape         prometheus.Gauge
	ScrapeDuration     prometheus.Histogram
	ScrapeErrorsTotal  prometheus.Counter
	APIRequestTotal    *prometheus.CounterVec
	APIRequestDuration *prometheus.HistogramVec
	APIResponseSize    *prometheus.SummaryVec
	FileReadErrors     *prometheus.CounterVec
	SQLQueryErrors     *prometheus.CounterVec
	APIValueGauge      *prometheus.GaugeVec
	APIValueHistogram  *prometheus.HistogramVec
	APIValueSummary    *prometheus.SummaryVec
	FileValueGauge     *prometheus.GaugeVec
	SQLValueGauge      *prometheus.GaugeVec
}

func New(cfg *config.Config, logger *slog.Logger) *Exporter {
	disabled := map[string]struct{}{}
	for _, name := range cfg.MetricFilter.Disabled {
		disabled[name] = struct{}{}
	}

	metrics := newExporterMetrics()

	return &Exporter{
		cfg:      cfg,
		logger:   logger,
		disabled: disabled,
		metrics:  metrics,
		api:      NewAPICollector(cfg.APIEndpoints, cfg.Labels, metrics, logger),
		files:    NewFileCollector(cfg.FileMetrics, cfg.Labels, metrics, logger),
		sql:      NewSQLCollector(cfg.SQLMetrics, cfg.Labels, metrics, logger),
	}
}

func (e *Exporter) Register(registry *prometheus.Registry) {
	e.registerIfEnabled(registry, e.metrics.Up)
	e.registerIfEnabled(registry, e.metrics.LastScrape)
	e.registerIfEnabled(registry, e.metrics.ScrapeDuration)
	e.registerIfEnabled(registry, e.metrics.ScrapeErrorsTotal)
	e.registerIfEnabled(registry, e.metrics.APIRequestTotal)
	e.registerIfEnabled(registry, e.metrics.APIRequestDuration)
	e.registerIfEnabled(registry, e.metrics.APIResponseSize)
	e.registerIfEnabled(registry, e.metrics.FileReadErrors)
	e.registerIfEnabled(registry, e.metrics.SQLQueryErrors)
	e.registerIfEnabled(registry, e.metrics.APIValueGauge)
	e.registerIfEnabled(registry, e.metrics.APIValueHistogram)
	e.registerIfEnabled(registry, e.metrics.APIValueSummary)
	e.registerIfEnabled(registry, e.metrics.FileValueGauge)
	e.registerIfEnabled(registry, e.metrics.SQLValueGauge)
}

func (e *Exporter) registerIfEnabled(registry *prometheus.Registry, collector prometheus.Collector) {
	if collector == nil {
		return
	}
	if name := collectorName(collector); name != "" {
		if _, blocked := e.disabled[name]; blocked {
			return
		}
	}
	registry.MustRegister(collector)
}

func collectorName(collector prometheus.Collector) string {
	descriptors := make(chan *prometheus.Desc, 1)
	collector.Describe(descriptors)
	select {
	case desc := <-descriptors:
		if desc == nil {
			return ""
		}
		return parseDescName(desc.String())
	default:
		return ""
	}
}

func parseDescName(desc string) string {
	start := strings.Index(desc, "fqName: \"")
	if start == -1 {
		return ""
	}
	start += len("fqName: \"")
	end := strings.Index(desc[start:], "\"")
	if end == -1 {
		return ""
	}
	return desc[start : start+end]
}

func (e *Exporter) Scrape(ctx context.Context) {
	start := time.Now()
	errCount := 0

	if e.cfg.FeatureFlags.EnableAPI {
		if err := e.api.Collect(ctx); err != nil {
			errCount++
			e.logger.Error("api collection failed", "err", err)
		}
	}
	if e.cfg.FeatureFlags.EnableFiles {
		if err := e.files.Collect(ctx); err != nil {
			errCount++
			e.logger.Error("file collection failed", "err", err)
		}
	}
	if e.cfg.FeatureFlags.EnableSQL {
		if err := e.sql.Collect(ctx); err != nil {
			errCount++
			e.logger.Error("sql collection failed", "err", err)
		}
	}

	e.metrics.LastScrape.SetToCurrentTime()
	e.metrics.ScrapeDuration.Observe(time.Since(start).Seconds())

	if errCount > 0 {
		e.metrics.ScrapeErrorsTotal.Add(float64(errCount))
		e.metrics.Up.Set(0)
	} else {
		e.metrics.Up.Set(1)
	}
}

func newExporterMetrics() *ExporterMetrics {
	return &ExporterMetrics{
		Up: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "custom_exporter_up",
			Help: "Whether the last scrape of collectors was successful.",
		}),
		LastScrape: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "custom_exporter_last_scrape_timestamp",
			Help: "Unix timestamp of the last scrape.",
		}),
		ScrapeDuration: prometheus.NewHistogram(prometheus.HistogramOpts{
			Name:    "custom_exporter_scrape_duration_seconds",
			Help:    "Duration of a full scrape across enabled collectors.",
			Buckets: prometheus.DefBuckets,
		}),
		ScrapeErrorsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "custom_exporter_scrape_errors_total",
			Help: "Total number of scrape errors across collectors.",
		}),
		APIRequestTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "custom_exporter_api_requests_total",
			Help: "Total API requests executed by the exporter.",
		}, []string{"endpoint"}),
		APIRequestDuration: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Name:    "custom_exporter_api_request_duration_seconds",
			Help:    "Duration of API requests.",
			Buckets: prometheus.DefBuckets,
		}, []string{"endpoint"}),
		APIResponseSize: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Name:       "custom_exporter_api_response_size_bytes",
			Help:       "Response size of API requests.",
			Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
		}, []string{"endpoint"}),
		FileReadErrors: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "custom_exporter_file_read_errors_total",
			Help: "Total file read errors while collecting metrics.",
		}, []string{"file"}),
		SQLQueryErrors: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "custom_exporter_sql_query_errors_total",
			Help: "Total SQL query errors while collecting metrics.",
		}, []string{"metric"}),
		APIValueGauge: prometheus.NewGaugeVec(prometheus.GaugeOpts{
			Name: "custom_exporter_api_value",
			Help: "Value extracted from API responses.",
		}, []string{"endpoint", "label"}),
		APIValueHistogram: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Name:    "custom_exporter_api_value_histogram",
			Help:    "Histogram of API values.",
			Buckets: prometheus.DefBuckets,
		}, []string{"endpoint", "label"}),
		APIValueSummary: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Name:       "custom_exporter_api_value_summary",
			Help:       "Summary of API values.",
			Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
		}, []string{"endpoint", "label"}),
		FileValueGauge: prometheus.NewGaugeVec(prometheus.GaugeOpts{
			Name: "custom_exporter_file_value",
			Help: "Values parsed from files.",
		}, []string{"file", "label"}),
		SQLValueGauge: prometheus.NewGaugeVec(prometheus.GaugeOpts{
			Name: "custom_exporter_sql_value",
			Help: "Values returned from SQL queries.",
		}, []string{"metric", "label"}),
	}
}

var errNoData = errors.New("no data collected")

func combineErrors(errs []error) error {
	if len(errs) == 0 {
		return nil
	}
	if len(errs) == 1 {
		return errs[0]
	}
	return errNoData
}
