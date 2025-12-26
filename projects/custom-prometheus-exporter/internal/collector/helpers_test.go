package collector

import (
	"testing"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/testutil"
)

func readGauge(t *testing.T, gaugeVec *prometheus.GaugeVec, labels ...string) float64 {
	t.Helper()
	return testutil.ToFloat64(gaugeVec.WithLabelValues(labels...))
}
