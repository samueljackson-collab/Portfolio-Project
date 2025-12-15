# Secret Management

This directory does not include actual Kubernetes secrets in version control for security reasons.

## Creating Secrets

### Option 1: Using the helper script (Recommended for local development)

1. Set environment variables with your actual values:
```bash
export API_KEY="your-actual-api-key"
export DATABASE_URL="postgresql://app_user:secure-password@postgres:5432/pocdb"
export REDIS_URL="redis://redis:6379/0"
export POSTGRES_USER="app_user"
export POSTGRES_PASSWORD="secure-password"
```

2. Run the helper script:
```bash
chmod +x k8s/setup-k8s-auth.sh
./k8s/setup-k8s-auth.sh
```

### Option 2: Using kubectl directly

```bash
kubectl create namespace poc-api

kubectl create secret generic poc-api-secrets \
  --namespace=poc-api \
  --from-literal=API_KEY="your-api-key" \
  --from-literal=DATABASE_URL="postgresql://app_user:password@postgres:5432/pocdb" \
  --from-literal=REDIS_URL="redis://redis:6379/0"

kubectl create secret generic postgres-credentials \
  --namespace=poc-api \
  --from-literal=POSTGRES_USER="app_user" \
  --from-literal=POSTGRES_PASSWORD="your-password"
```

### Option 3: Using a secret management tool (Recommended for production)

For production environments, use proper secret management tools:

- **Sealed Secrets**: Encrypt secrets that can be safely stored in Git
  ```bash
  kubeseal --format=yaml < secret.yaml > sealed-secret.yaml
  ```

- **External Secrets Operator**: Sync secrets from external secret managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, etc.)
  ```yaml
  apiVersion: external-secrets.io/v1beta1
  kind: ExternalSecret
  metadata:
    name: poc-api-secrets
  spec:
    secretStoreRef:
      name: aws-secrets-manager
      kind: SecretStore
    target:
      name: poc-api-secrets
    data:
    - secretKey: API_KEY
      remoteRef:
        key: poc/api-key
  ```

- **HashiCorp Vault**: Use Vault Agent Injector or CSI driver
- **SOPS**: Encrypt YAML files with various key providers

## Template File

See `secret.yaml.example` for the structure of required secrets.
