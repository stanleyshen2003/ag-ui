# Deployment Plan: ops/ for AG-UI (Frontend + Backend)

## Overview

Add an `ops/` folder with Kubernetes manifests to deploy the Docker images built and pushed by the existing GitHub Actions workflows. Images are stored in Harbor at `$HARBOR_URL/agent/frontend` and `$HARBOR_URL/agent/backend` (tags: `latest`, git SHA). Ingress controller is already installed; frontend will be exposed via Ingress with hostname **research.stanley.winlab.tw**.

---

## Folder Structure

```
ops/
├── DEPLOYMENT_PLAN.md     # This plan (optional to keep after implementation)
├── frontend/
│   ├── deployment.yaml   # Deployment + optional ConfigMap for env
│   ├── service.yaml      # ClusterIP Service (port 3000)
│   └── ingress.yaml      # Ingress with host: research.stanley.winlab.tw
└── backend/
    ├── deployment.yaml   # Deployment + env from Secret/ConfigMap
    └── service.yaml      # ClusterIP Service (port 8000)
```

- **Frontend**: Deployment → Service → Ingress (public).
- **Backend**: Deployment → Service (internal only; frontend calls it via K8s Service DNS).

---

## 1. Backend (ops/backend/)

| File | Purpose |
|------|--------|
| **deployment.yaml** | Deployment for `agent/backend` image. No imagePullSecrets (Harbor is public). Env: `GOOGLE_API_KEY` (and optional `SEMANTIC_SCHOLAR_API_KEY`, `MLFLOW_TRACKING_URI`) from a Secret. Replicas: 1 (or more). Port 8000. Liveness/readiness: `GET /health`. |
| **service.yaml** | ClusterIP Service exposing port 8000. No Ingress — frontend (in-cluster, same namespace) calls it at `http://backend:8000/`. |

**Image**: Assume `harbor.stanley.winlab.tw/agent/backend:latest` (or parameterized via kustomize/env). Replace with your actual Harbor host if different.

**Secrets**: Backend needs at least `GOOGLE_API_KEY`. Plan assumes a Secret `backend-secret` (or similar) exists; we can document creating it (e.g. `kubectl create secret generic backend-secret --from-literal=GOOGLE_API_KEY=...`) and reference it in the Deployment.

---

## 2. Frontend (ops/frontend/)

| File | Purpose |
|------|--------|
| **deployment.yaml** | Deployment for `agent/frontend` image. Env: `NEXT_PUBLIC_AG_UI_URL=http://backend:8000/` (backend Service in same namespace) so the Next.js app talks to the backend. Port 3000. Optional liveness/readiness on `/` or a health path. |
| **service.yaml** | ClusterIP Service exposing port 3000 (Next.js default in container). |
| **ingress.yaml** | Ingress with `spec.ingressClassName` set to your controller (e.g. `nginx`), single rule: host **research.stanley.winlab.tw**, path `/` or no path, backend `service: frontend`, port 3000. TLS optional (can add later with a cert-manager or static Secret). |

**Image**: Assume `harbor.stanley.winlab.tw/agent/frontend:latest`. No imagePullSecrets (Harbor is public).

**Backend URL**: In-cluster, same namespace — use `http://backend:8000/` (short Service DNS name).

---

## 3. Assumptions and Conventions

- **In-cluster, same namespace**: Frontend and backend run in the same cluster and same namespace. Frontend reaches backend at `http://backend:8000/`. No imagePullSecrets (Harbor is public).
- **Namespace**: Use a single namespace (e.g. `default` or `ag-ui`) for all resources; optionally set `metadata.namespace` in manifests or via kustomization.
- **Ingress class**: One of `nginx`, `traefik`, or your controller’s class. Set in `ingress.yaml`; adjust `ingressClassName` to match your cluster.
- **Harbor**: Public registry — no imagePullSecrets. Image names and tag (`latest` or SHA) match what the CI pushes.
- **TLS**: Plan keeps Ingress HTTP only; add a `tls` section and certificate later if needed.

---

## 4. Implementation Order

1. Create **ops/backend/**  
   - **service.yaml** (ClusterIP, port 8000).  
   - **deployment.yaml** (image, port 8000, env from Secret, health checks).
2. Create **ops/frontend/**  
   - **service.yaml** (ClusterIP, port 3000).  
   - **deployment.yaml** (image, port 3000, `NEXT_PUBLIC_AG_UI_URL=http://backend:8000/`).  
   - **ingress.yaml** (host: research.stanley.winlab.tw, backend service frontend:3000).
3. (Optional) Add a short **ops/README.md** with:  
   - How to create `backend-secret` (e.g. `GOOGLE_API_KEY`).  
   - Example `kubectl apply -f ops/backend`, `kubectl apply -f ops/frontend`, and note to apply backend before frontend.

---

## 5. Summary

| Component | Image | Service | Ingress |
|-----------|--------|---------|---------|
| Backend | Harbor `agent/backend:latest` | ClusterIP :8000 | No |
| Frontend | Harbor `agent/frontend:latest` | ClusterIP :3000 | Yes — host **research.stanley.winlab.tw** |

After implementation, you’ll have two folders under `ops/` (frontend and backend) with YAML that deploy the wrapped Docker images and expose the frontend via your existing ingress controller at **research.stanley.winlab.tw**.
