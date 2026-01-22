# Release Evidence Pack: Kubernetes CI/CD Project

## Summary
This evidence pack documents the current state of deployment and CI evidence collection for `projects/3-kubernetes-cicd`. In this environment, Kubernetes tooling and GitHub CLI access are unavailable, so deployments and CI run capture could not be executed.

## Environment Limitations
### Kubernetes tooling
Attempted to verify `kubectl` availability:

```bash
kubectl version --client
```

Output:

```
bash: command not found: kubectl
```

### CI workflow tooling
Attempted to verify GitHub CLI availability for triggering CI:

```bash
gh --version
```

Output:

```
bash: command not found: gh
```

## Requested Evidence (Pending)
The following items could not be generated in this environment:

- **CI run screenshot** (requires GitHub Actions access).
- **`kubectl get all` output** (requires `kubectl` and cluster credentials).
- **Rollout history** (requires access to the Kubernetes cluster/Argo Rollouts).
- **Cluster resource screenshots** (requires a reachable cluster UI or dashboard).

## Next Steps
Run the following in an environment with Kubernetes access and GitHub credentials:

1. Deploy manifests:
   ```bash
   kubectl apply -k projects/3-kubernetes-cicd/k8s/base
   kubectl rollout status deployment/k8s-cicd-demo
   ```
2. Capture cluster output:
   ```bash
   kubectl get all -n default
   kubectl rollout history deployment/k8s-cicd-demo
   ```
3. Trigger the CI workflow via GitHub Actions and capture logs + screenshots.
4. Save screenshots and outputs in `projects/3-kubernetes-cicd/evidence/`.
