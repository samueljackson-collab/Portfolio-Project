# P12 Airflow DAG Demo

Run a minimal Airflow-inspired ETL flow (extract → transform → load) to verify the pipeline steps complete in order.

## Run locally
```bash
python app.py
cat artifacts/airflow_dag_run.log
```

## Build and run with Docker
```bash
docker build -t p12-data-pipeline .
docker run --rm p12-data-pipeline
```

## Run in Kubernetes
Push the image to your registry, set `image:` in `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/airflow_dag_run.log` lists each DAG task execution and completion status.
