package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/segmentio/kafka-go"
)

type roamingEvent struct {
    EventID   string `json:"event_id"`
    IMSI      string `json:"imsi"`
    CellID    string `json:"cell_id"`
    Country   string `json:"country"`
    Event     string `json:"event"`
    Timestamp int64  `json:"timestamp"`
}

var processed = 0

func metricsHandler(w http.ResponseWriter, _ *http.Request) {
    fmt.Fprintf(w, "roaming_events_processed_total %d\n", processed)
}

func main() {
    bootstrap := getenv("BOOTSTRAP_SERVERS", "kafka:9092")
    topic := "roaming.events"

    go func() {
        http.HandleFunc("/metrics", metricsHandler)
        log.Fatal(http.ListenAndServe(":9102", nil))
    }()

    r := kafka.NewReader(kafka.ReaderConfig{
        Brokers: []string{bootstrap},
        Topic:   topic,
        GroupID: "roaming-consumer",
    })
    ctx := context.Background()
    for {
        m, err := r.FetchMessage(ctx)
        if err != nil {
            log.Printf("fetch error: %v", err)
            time.Sleep(time.Second)
            continue
        }
        var ev roamingEvent
        if err := json.Unmarshal(m.Value, &ev); err != nil {
            log.Printf("decode error: %v", err)
        } else {
            processed++
            log.Printf("event %s from %s", ev.EventID, ev.Country)
        }
        _ = r.CommitMessages(ctx, m)
    }
}

func getenv(key, def string) string {
    if val := os.Getenv(key); val != "" {
        return val
    }
    return def
}
