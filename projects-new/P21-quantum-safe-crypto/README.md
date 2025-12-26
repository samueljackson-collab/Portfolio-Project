# P21 Quantum-Safe Cryptography Demo

Generates a mock Kyber-style keypair to illustrate post-quantum readiness.

## Run locally
```bash
python app.py
cat artifacts/kyber_key_material.json
```

## Build and run with Docker
```bash
docker build -t p21-quantum-safe-crypto .
docker run --rm p21-quantum-safe-crypto
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/kyber_key_material.json` includes the generated public/private key placeholders and algorithm tag.
