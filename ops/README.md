# Ops: Deploy AG-UI (Frontend + Backend)

Kubernetes manifests to deploy the Docker images built and pushed by the GitHub Actions workflows. Frontend is exposed via Ingress at **research.stanley.winlab.tw**; backend is in-cluster only (same namespace).

## Prerequisites

- Ingress controller installed (manifests use `ingressClassName: nginx`; change in `frontend/ingress.yaml` if needed).
- Harbor is public; no imagePullSecrets required.
- Frontend and backend run in the **same namespace**.

## Create backend secret

Backend needs at least `GOOGLE_API_KEY`. Create a Secret in the same namespace where you will deploy:

```bash
kubectl create secret generic backend-secret \
  --from-literal=GOOGLE_API_KEY=<your-google-api-key>
```

Optional keys (for higher rate limits / MLflow):

```bash
kubectl create secret generic backend-secret \
  --from-literal=GOOGLE_API_KEY=<key> \
  --from-literal=SEMANTIC_SCHOLAR_API_KEY=<key> \
  --from-literal=MLFLOW_TRACKING_URI=<uri> \
  --dry-run=client -o yaml | kubectl apply -f -
```

Or patch an existing secret to add keys.

## Deploy

Apply **backend first** (frontend depends on the backend Service), then frontend:

```bash
# Backend (Deployment + Service)
kubectl apply -f ops/backend/

# Frontend (Deployment + Service + Ingress)
kubectl apply -f ops/frontend/
```

## Image and registry

- **Backend**: `harbor.stanley.winlab.tw/agent/backend:latest`
- **Frontend**: `harbor.stanley.winlab.tw/agent/frontend:latest`

If your Harbor host or project differs, edit the `image` field in `backend/deployment.yaml` and `frontend/deployment.yaml`.

## Ingress

- **Host**: research.stanley.winlab.tw
- **Ingress class**: nginx (change `spec.ingressClassName` in `frontend/ingress.yaml` to match your cluster).
- TLS is not configured; add a `tls` section and certificate if needed.
