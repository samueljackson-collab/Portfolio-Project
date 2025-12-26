package collector

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/example/custom-prometheus-exporter/internal/config"
)

type APICollector struct {
	endpoints  []config.APIEndpoint
	metrics    *ExporterMetrics
	client     *http.Client
	logger     logger
	baseLabels map[string]string
}

type logger interface {
	Error(msg string, args ...any)
	Warn(msg string, args ...any)
	Info(msg string, args ...any)
}

func NewAPICollector(endpoints []config.APIEndpoint, baseLabels map[string]string, metrics *ExporterMetrics, log logger) *APICollector {
	return &APICollector{
		endpoints:  endpoints,
		metrics:    metrics,
		client:     &http.Client{Timeout: 10 * time.Second},
		logger:     log,
		baseLabels: baseLabels,
	}
}

func (c *APICollector) Collect(ctx context.Context) error {
	if len(c.endpoints) == 0 {
		return nil
	}
	var errs []error
	for _, endpoint := range c.endpoints {
		if endpoint.URL == "" {
			err := fmt.Errorf("api endpoint %q missing url", endpoint.Name)
			errs = append(errs, err)
			continue
		}
		if err := c.collectEndpoint(ctx, endpoint); err != nil {
			err = fmt.Errorf("api endpoint %q: %w", endpoint.Name, err)
			errs = append(errs, err)
		}
	}
	if len(errs) > 0 {
		return errors.New("api collection errors")
	}
	return nil
}

func (c *APICollector) collectEndpoint(ctx context.Context, endpoint config.APIEndpoint) error {
	method := strings.ToUpper(endpoint.Method)
	if method == "" {
		method = http.MethodGet
	}
	client := c.client
	if endpoint.Timeout > 0 {
		client = &http.Client{Timeout: endpoint.Timeout}
	}

	req, err := http.NewRequestWithContext(ctx, method, endpoint.URL, nil)
	if err != nil {
		return err
	}
	for key, value := range endpoint.Headers {
		req.Header.Set(key, value)
	}

	start := time.Now()
	resp, err := client.Do(req)
	c.metrics.APIRequestTotal.WithLabelValues(endpoint.Name).Inc()
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	c.metrics.APIRequestDuration.WithLabelValues(endpoint.Name).Observe(time.Since(start).Seconds())

	payload, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	c.metrics.APIResponseSize.WithLabelValues(endpoint.Name).Observe(float64(len(payload)))

	if resp.StatusCode >= http.StatusBadRequest {
		return fmt.Errorf("unexpected status %d", resp.StatusCode)
	}

	value, err := extractValue(payload, endpoint.ValuePath)
	if err != nil {
		return err
	}

	labelValue := labelString(mergeLabels(c.baseLabels, endpoint.Labels))
	switch strings.ToLower(endpoint.MetricType) {
	case "counter":
		c.metrics.APIValueGauge.WithLabelValues(endpoint.Name, labelValue).Add(value)
	case "histogram":
		c.metrics.APIValueHistogram.WithLabelValues(endpoint.Name, labelValue).Observe(value)
	case "summary":
		c.metrics.APIValueSummary.WithLabelValues(endpoint.Name, labelValue).Observe(value)
	default:
		c.metrics.APIValueGauge.WithLabelValues(endpoint.Name, labelValue).Set(value)
	}
	return nil
}

func extractValue(payload []byte, path string) (float64, error) {
	var body any
	if err := json.Unmarshal(payload, &body); err != nil {
		return 0, err
	}
	if path == "" {
		path = "value"
	}

	current := body
	for _, part := range strings.Split(path, ".") {
		switch typed := current.(type) {
		case map[string]any:
			current = typed[part]
		case []any:
			index := -1
			if part == "0" {
				index = 0
			}
			if index >= 0 && index < len(typed) {
				current = typed[index]
			} else {
				return 0, fmt.Errorf("invalid array index path %q", part)
			}
		default:
			return 0, fmt.Errorf("invalid path segment %q", part)
		}
	}

	switch value := current.(type) {
	case float64:
		return value, nil
	case int:
		return float64(value), nil
	case int64:
		return float64(value), nil
	case string:
		return parseStringValue(value)
	default:
		return 0, fmt.Errorf("unsupported value type %T", current)
	}
}

func parseStringValue(value string) (float64, error) {
	trimmed := strings.TrimSpace(value)
	parsed, err := strconv.ParseFloat(trimmed, 64)
	if err != nil {
		return 0, fmt.Errorf("parse value %q: %w", value, err)
	}
	return parsed, nil
}
