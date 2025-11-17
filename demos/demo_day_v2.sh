#!/usr/bin/env bash
set -euo pipefail

echo "== 1. Start Observability (P25)"
make -C projects/P25-observability up

echo "== 2. Start RAG (P09) and warm"
make -C projects/P09-rag-chatbot ingest || true
( cd projects/P09-rag-chatbot && uvicorn app:app --port 8010 --reload ) &
RAG_PID=$!
sleep 3
for i in {1..40}; do curl -s "http://localhost:8010/q?text=aws%20vpc" >/dev/null || true; done

echo "== 3. Capture evidence (requires GRAFANA_* and JAEGER_BASE env)"
mkdir -p projects/P25-observability/docs/evidence projects/P09-rag-chatbot/docs/evidence
if [[ -n "${GRAFANA_URL:-}" && -n "${GRAFANA_TOKEN:-}" ]]; then
  bash scripts/capture_grafana_by_title.sh "Demo App" "Latency (p95)" now-15m now projects/P25-observability/docs/evidence/Latency_p95.png || true
else
  echo "Skip Grafana snapshot (missing env)"
fi
python scripts/jaeger_recent_trace.py --service rag-chatbot --lookback 30m --export projects/P09-rag-chatbot/docs/evidence/trace.png || true

echo "Open Grafana:  ${GRAFANA_URL:-http://localhost:3000}"
echo "Open Jaeger:   ${JAEGER_BASE:-http://localhost:16686}"
echo "Stop RAG api:  kill $RAG_PID"
