# IoT Streaming Platform

A real-time IoT data processing pipeline built with Python, Kafka, TimescaleDB, and Kubernetes.

---

## Quick Start (Kubernetes)

Follow these steps to deploy the entire stack on a local **KinD (Kubernetes in Docker)** cluster.

### 1. Cluster Setup
Create the cluster and verify connectivity.
```bash
kind create cluster --name iot-cluster
kubectl cluster-info --context kind-iot-cluster
kubectl get nodes
```

### 2. Base Infrastructure
Apply the namespace, configuration, and data stores (Postgres & Kafka).
```bash
# Apply Namespace & Config
kubectl apply -f infrastructure/k8s/namespace.yaml
kubectl apply -f infrastructure/k8s/base/config.yaml
kubectl apply -f infrastructure/k8s/base/secrets.yaml

# Deploy Data Stores
kubectl apply -f infrastructure/k8s/base/postgres/postgres.yaml
kubectl apply -f infrastructure/k8s/base/kafka/kafka.yaml

# Wait for databases to be ready
kubectl get pods -n iot-platform -w
```

### 3. Build & Load Images
Build application images locally and load them into the KinD nodes.
```bash
# Build
docker build -t iot-worker:latest -f services/worker/Dockerfile .
docker build -t iot-api:latest -f services/api/Dockerfile .
docker build -t iot-simulator:latest -f services/simulator/Dockerfile .

# Load into Kind
kind load docker-image iot-worker:latest --name iot-cluster
kind load docker-image iot-api:latest --name iot-cluster
kind load docker-image iot-simulator:latest --name iot-cluster
```

### 4. Database Migration
Run the one-off migration job to set up tables.
```bash
kubectl apply -f infrastructure/k8s/services/worker/migrate-job.yaml

# Check migration logs
kubectl logs job/db-migrate -n iot-platform
```

### 5. Deploy Application Services
Start the Worker, Simulator, and API.
```bash
kubectl apply -f infrastructure/k8s/services/worker/worker.yaml
kubectl apply -f infrastructure/k8s/services/simulator/simulator.yaml
kubectl apply -f infrastructure/k8s/services/api/api.yaml
```

### 6. Networking & Ingress
Install the NGINX Ingress Controller and apply the routing rules.
```bash
# Install Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=600s

# Apply our Ingress rules
kubectl apply -f infrastructure/k8s/ingress.yaml
```

### 7. Access & Verify
Forward the ingress port to access the API docs.
```bash
# Port forward Ingress
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80

# Open and check:
# http://localhost:8080/docs
```

---

## Cleanup
To remove everything and stop the cluster.
```bash
# Delete all resources in the namespace
kubectl delete namespace iot-platform

# Delete the entire Kind cluster
kind delete cluster --name iot-cluster
```

---

## Local Development (Docker Compose)
For running without Kubernetes during development:
```bash
make build
make up
make setup
make test-all
```