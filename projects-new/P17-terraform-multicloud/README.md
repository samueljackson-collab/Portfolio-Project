# P17 Terraform Multi-Cloud Demo

Mocks a Terraform plan/apply across AWS and Azure resources to demonstrate workflow orchestration.

## Run locally
```bash
python app.py
cat artifacts/terraform_plan.json
```

## Build and run with Docker
```bash
docker build -t p17-terraform-multicloud .
docker run --rm p17-terraform-multicloud
```

## Run in Kubernetes
Push the image, set `image:` in `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/terraform_plan.json` contains the mock plan and apply summary with the resource count.
