package collector

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/example/custom-prometheus-exporter/internal/config"
)

type FileCollector struct {
	files      []config.FileMetric
	metrics    *ExporterMetrics
	logger     logger
	baseLabels map[string]string
}

func NewFileCollector(files []config.FileMetric, baseLabels map[string]string, metrics *ExporterMetrics, log logger) *FileCollector {
	return &FileCollector{
		files:      files,
		metrics:    metrics,
		logger:     log,
		baseLabels: baseLabels,
	}
}

func (c *FileCollector) Collect(ctx context.Context) error {
	if len(c.files) == 0 {
		return nil
	}
	var errs []error
	for _, fileMetric := range c.files {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}
		if err := c.collectFile(fileMetric); err != nil {
			err = fmt.Errorf("file %s: %w", fileMetric.Path, err)
			errs = append(errs, err)
		}
	}
	if len(errs) > 0 {
		return fmt.Errorf("file collection errors: %d", len(errs))
	}
	return nil
}

func (c *FileCollector) collectFile(fileMetric config.FileMetric) error {
	payload, err := os.ReadFile(fileMetric.Path)
	if err != nil {
		c.metrics.FileReadErrors.WithLabelValues(fileMetric.Path).Inc()
		return err
	}
	value := string(payload)
	if fileMetric.TrimSpace {
		value = strings.TrimSpace(value)
	}
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		c.metrics.FileReadErrors.WithLabelValues(fileMetric.Path).Inc()
		return err
	}
	labelValue := labelString(mergeLabels(c.baseLabels, fileMetric.Labels))
	switch strings.ToLower(fileMetric.MetricType) {
	case "counter":
		c.metrics.FileValueGauge.WithLabelValues(fileMetric.Name, labelValue).Add(parsed)
	default:
		c.metrics.FileValueGauge.WithLabelValues(fileMetric.Name, labelValue).Set(parsed)
	}
	return nil
}
