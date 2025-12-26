# P11 API Gateway + Lambda Demo

This lightweight example simulates an API Gateway request invoking a Lambda handler and returning a JSON payload.

## Run locally
```bash
python app.py
cat artifacts/api_gateway_flow.json
```

## Build and run with Docker
```bash
docker build -t p11-api-gateway .
docker run --rm p11-api-gateway
```

## Run in Kubernetes
After pushing your image to a registry, update `image:` in `k8s-demo.yaml` and apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/api_gateway_flow.json` captures the gateway response body including the Lambda audit trail.
