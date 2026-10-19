# DevOps Learning Path

One tiny Flask app (`app/`) with Redis, taken through the full DevOps lifecycle. Do the stages in order; each adds one skill.

| Stage | Topic | Folder | Goal |
|---|---|---|---|
| 1 | Git + local dev + tests | `app/` | Run the app, run `pytest`, use feature branches and PRs |
| 2 | Containers | `app/Dockerfile`, `docker-compose.yml` | Build an image, run app + Redis with Compose |
| 3 | CI/CD | `.github/workflows/ci.yml` | Auto-test on every push, build and push image to GHCR |
| 4 | Infrastructure as Code | `terraform/` | `plan` / `apply` / `destroy`, understand state |
| 5 | Orchestration | `k8s/` | Deployments, Services, probes, rolling updates, autoscaling |
| 6 | Monitoring & alerting | `monitoring/` | Prometheus metrics, Grafana dashboards, alert rules |
| 7 | Configuration management | `ansible/` | Deploy to a real server idempotently |
| 8 | GitOps (advanced) | `gitops/` | Argo CD syncs the cluster from Git |

## Tools to install
Git, Python 3.12, Docker Desktop, then later: Terraform, kind + kubectl, and WSL (for Ansible).

## Stage walkthrough

### 1. Basics
```powershell
cd app
python -m venv .venv; .venv\Scripts\activate
pip install -r requirements.txt
pytest
python app.py          # http://localhost:5000, /health, /metrics
```
Then `git init`, commit, make a branch, break a test, and see it fail.

### 2. Docker
```powershell
docker compose up --build
curl http://localhost:5000      # hits counter increments (stored in Redis)
```
Experiments: `docker compose down` then `up` (does the counter survive? why?), `docker compose logs web`, `docker exec -it <container> sh`.

### 3. CI/CD
Push this folder to a new GitHub repo. Watch the Actions tab. Break a test in a PR and see the merge get blocked. Add branch protection requiring the `test` job.

### 4. Terraform
```powershell
docker build -t devops-app:local ./app
cd terraform
terraform init; terraform plan; terraform apply
terraform destroy
```
Experiments: change `app_port` and re-plan; delete a container manually and see Terraform detect drift.

### 5. Kubernetes
```powershell
kind create cluster
docker build -t devops-app:local ./app
kind load docker-image devops-app:local
kubectl apply -f k8s/
kubectl get pods -w
kubectl port-forward svc/web 8080:80
```
Experiments: `kubectl delete pod` (self-heals), `kubectl scale deploy web --replicas=5`, change `APP_VERSION` in the ConfigMap and `kubectl rollout restart deploy/web`, break the image name and `kubectl rollout undo`.

### 6. Monitoring
Run the root compose, then `cd monitoring; docker compose up`. Generate load (`for ($i=0;$i -lt 500;$i++){curl -s localhost:5000 >$null}`), graph `rate(app_requests_total[1m])`, stop the web container and watch `WebDown` fire at http://localhost:9090/alerts.

### 7. Ansible
Needs an Ubuntu VM and Linux/WSL. Edit `inventory.ini` and the image in `playbook.yml`, run it twice and note that the second run changes nothing (idempotency).

### 8. GitOps
Install Argo CD in your kind cluster, apply `gitops/argocd-app.yaml`. Change replicas in Git, push, and watch Argo reconcile. Manually `kubectl scale` and watch it self-heal back.

## Next steps (ideas once you finish)
- Add image vulnerability scanning (Trivy) and secret scanning to CI
- Helm chart or Kustomize overlays for dev/staging/prod
- Move Terraform to a real cloud (AWS free tier: VPC + EC2 or EKS) with remote state
- Blue/green or canary deploys (Argo Rollouts)
- Centralized logging (Loki) and tracing (OpenTelemetry + Tempo)
- Secrets management (Vault or Sealed Secrets)
