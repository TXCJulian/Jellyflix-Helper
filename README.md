# Docker-Rename

## Project overview

This project consists of a backend (FastAPI, Python) and a frontend (Vue 3, Vite, Nginx). Both run in separate containers and communicate over a shared Docker network.

## Prerequisites

- Docker & Docker Compose

## Build & run locally (Docker Compose)

1. Adjust environment variables in `docker-compose.yml` and `frontend/.env` if needed (e.g., TMDB_API_KEY, media paths).
2. Build and start the containers:

```powershell
docker compose up --build
```

The backend will be available at http://localhost:3332 and the frontend at http://localhost:3333.

## Architecture & communication

### Overview

The project uses an Nginx reverse proxy inside the frontend container to transparently forward backend API requests. The browser talks to a single port (3333), and Nginx routes requests internally to the backend.

### Request flow

```
Browser                    Frontend container               Backend container
  |                             (Nginx)                          (FastAPI)
  |                               |                                  |
  |--[1] GET :3333/directories--->|                                  |
  |    (HTTP Request)             |                                  |
  |                               |--[2] proxy_pass----------------->|
  |                               |    http://renamer-backend:3332   |
  |                               |    (Docker network)              |
  |                               |                                  |
  |                               |<---[3] JSON response-------------|
  |<--[4] JSON response-----------|                                  |
```

Step by step:

1. Browser → Frontend (port 3333)  
   The browser loads the Vue app from `http://your-server:3333` and makes API calls like:
   ```javascript
   fetch('/directories/tvshows')  // same-origin request
   ```

2. Nginx proxy routing  
   `nginx-app.conf` defines the proxy rules:
   ```nginx
   location /directories/ {
       proxy_pass http://renamer-backend:3332/directories/;
   }
   location /rename/ {
       proxy_pass http://renamer-backend:3332/rename/;
   }
   ```

3. Docker network (`renamer-network`)  
   Nginx can resolve `renamer-backend` via the service name (Docker network DNS).  
   The backend container listens internally on port 3332.

4. Response back to the browser  
   FastAPI responds → Nginx forwards it → the browser receives JSON.

### Benefits of this architecture

✅ No CORS issues: from the browser’s perspective, all requests are same-origin  
✅ Single entry point: only port 3333 needs to be exposed  
✅ Backend can stay private: port 3332 doesn’t have to be published  
✅ Simple SSL termination: HTTPS only at Nginx  
✅ Standard production pattern: API gateway in front of microservices

### Good to know

- The browser doesn’t talk to the backend directly — only to port 3333.
- `renamer-backend` is only resolvable within the Docker network.
- The frontend `.env` is empty (`VITE_API_BASE_URL=""`), so the app uses `window.location.origin` as the base URL.

> Note:
> If you change service names (e.g., `helper-backend`) in your compose/deploy files, update them in the Nginx configuration (`frontend/nginx-app.conf`) as well. Otherwise, the frontend won’t reach the backend service (see the `proxy_pass` lines in the Nginx config).

## Deployment

Use `deploy.yml` as a template for server deployment. Adjust volumes and environment variables for your environment.

## Push images to Docker Hub

The compose/deploy files expect the images:

- `bosscock/jellyflix-helper:backend`
- `bosscock/jellyflix-helper:frontend`

If your Docker Hub username isn’t `bosscock`, replace it in the commands below and in `deploy.yml`/`docker-compose.yml` accordingly.

### 1) Log in to Docker Hub

```powershell
docker login
```

### 2) Build and tag images locally

Backend (FastAPI):

```powershell
docker build -t bosscock/jellyflix-helper:backend ./backend
```

Frontend (Vue + Nginx):

```powershell
docker build -t bosscock/jellyflix-helper:frontend ./frontend
```

Optional: add version tags as well (recommended for reproducible deployments):

```powershell
$version = "v1.0.0"
docker tag bosscock/jellyflix-helper:backend  bosscock/jellyflix-helper:backend-$version
docker tag bosscock/jellyflix-helper:frontend bosscock/jellyflix-helper:frontend-$version
```

### 3) Push images

```powershell
docker push bosscock/jellyflix-helper:backend
docker push bosscock/jellyflix-helper:frontend

# optionally push the version tags as well
docker push bosscock/jellyflix-helper:backend-$version
docker push bosscock/jellyflix-helper:frontend-$version
```

### Optional: Build and push multi-arch (amd64 + arm64)

For servers on different architectures (x86_64 and ARM, e.g., Raspberry Pi):

```powershell
# one-time: create a builder
docker buildx create --name multi --use ; docker buildx inspect --bootstrap

# backend multi-arch
docker buildx build --platform linux/amd64,linux/arm64 `
   -t bosscock/jellyflix-helper:backend `
    ./backend `
    --push

# frontend multi-arch
docker buildx build --platform linux/amd64,linux/arm64 `
   -t bosscock/jellyflix-helper:frontend `
    ./frontend `
    --push
```

### 4) Use the deploy file

After pushing, the target server can pull and start the images, e.g., using the provided `deploy.yml`:

```powershell
docker compose -f deploy.yml pull
docker compose -f deploy.yml up -d
```

Note: If you want to use a custom network (e.g., `renamer-network`), add a `networks` section to `deploy.yml` and attach both services to it. In that case, the frontend reaches the backend at `http://renamer-backend:3332`.

## Important files

- `docker-compose.yml`: Local setup, build contexts, network
- `deploy.yml`: Example for deployment using pushed images
- `frontend/.env`: API base URL (empty = same-origin via Nginx proxy)
- `frontend/nginx-app.conf`: Key piece — Nginx reverse proxy configuration for API routes
- `backend/Dockerfile`: Python 3.12 (LTS), FastAPI/Uvicorn
- `frontend/Dockerfile`: Node 20 (LTS), multi-stage build with Nginx runtime

## Notes

- Media directories must be mounted into the backend as a volume at `/media`.
- Backend environment variables are set in `docker-compose.yml`.
- Important: Use stable LTS versions (Python 3.11/3.12, Node 20/22). Newer versions like Python 3.13 or Node 25 may cause subtle runtime issues.