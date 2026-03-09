package collector

import (
	"context"
	"database/sql"
	"fmt"
	"strings"
	"sync"
	"time"

	_ "modernc.org/sqlite"

	"github.com/example/custom-prometheus-exporter/internal/config"
)

type SQLCollector struct {
	queries    []config.SQLMetric
	metrics    *ExporterMetrics
	logger     logger
	pool       map[string]*sql.DB
	mutex      sync.Mutex
	baseLabels map[string]string
}

func NewSQLCollector(queries []config.SQLMetric, baseLabels map[string]string, metrics *ExporterMetrics, log logger) *SQLCollector {
	return &SQLCollector{
		queries:    queries,
		metrics:    metrics,
		logger:     log,
		pool:       map[string]*sql.DB{},
		baseLabels: baseLabels,
	}
}

func (c *SQLCollector) Collect(ctx context.Context) error {
	if len(c.queries) == 0 {
		return nil
	}
	var errs []error
	for _, query := range c.queries {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}
		if err := c.collectQuery(ctx, query); err != nil {
			err = fmt.Errorf("sql metric %q: %w", query.Name, err)
			errs = append(errs, err)
		}
	}
	if len(errs) > 0 {
		return fmt.Errorf("sql collection errors: %d", len(errs))
	}
	return nil
}

func (c *SQLCollector) collectQuery(ctx context.Context, query config.SQLMetric) error {
	if query.Driver == "" || query.DSN == "" || query.Query == "" {
		return fmt.Errorf("missing driver/dsn/query")
	}
	db, err := c.db(query.Driver, query.DSN)
	if err != nil {
		c.metrics.SQLQueryErrors.WithLabelValues(query.Name).Inc()
		return err
	}

	queryCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	row := db.QueryRowContext(queryCtx, query.Query)
	var value float64
	if err := row.Scan(&value); err != nil {
		c.metrics.SQLQueryErrors.WithLabelValues(query.Name).Inc()
		return err
	}

	labelValue := labelString(mergeLabels(c.baseLabels, query.Labels))
	if strings.ToLower(query.MetricType) == "counter" {
		c.metrics.SQLValueGauge.WithLabelValues(query.Name, labelValue).Add(value)
		return nil
	}
	c.metrics.SQLValueGauge.WithLabelValues(query.Name, labelValue).Set(value)
	return nil
}

func (c *SQLCollector) db(driver, dsn string) (*sql.DB, error) {
	key := fmt.Sprintf("%s:%s", driver, dsn)
	c.mutex.Lock()
	defer c.mutex.Unlock()
	if existing, ok := c.pool[key]; ok {
		return existing, nil
	}
	db, err := sql.Open(driver, dsn)
	if err != nil {
		return nil, err
	}
	c.pool[key] = db
	return db, nil
}
