package collector

import (
	"context"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/example/custom-prometheus-exporter/internal/config"
)

func TestAPICollector(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write([]byte(`{"data":{"value":42}}`))
	}))
	defer server.Close()

	metrics := newExporterMetrics()
	collector := NewAPICollector([]config.APIEndpoint{
		{
			Name:       "test",
			URL:        server.URL,
			Method:     "GET",
			ValuePath:  "data.value",
			MetricType: "gauge",
		},
	}, nil, metrics, slog.New(slog.NewTextHandler(io.Discard, nil)))

	if err := collector.Collect(context.Background()); err != nil {
		t.Fatalf("collect failed: %v", err)
	}

	value := readGauge(t, metrics.APIValueGauge, "test", "")
	if value != 42 {
		t.Fatalf("expected value 42, got %f", value)
	}
}
