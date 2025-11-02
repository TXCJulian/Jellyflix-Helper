# Jellyflix Helper

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)

*An automatic renaming tool for TV shows and music files with a user-friendly web interface.*

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Overview

Jellyflix Helper is a dockerized tool that automatically renames TV show episodes and music files according to a standardized schema. It uses the TMDB API for TV series metadata and Mutagen for music tags. The application consists of a FastAPI backend (Python) and a Vue 3 frontend (Vite, Nginx), which communicate over a Docker network.

## Features

### TV Shows
- 🔍 **Automatic series search** via TMDB API (multi-language)
- 📺 **Episode renaming** according to the schema: `S01E01 - Episode title.ext`
- 🎯 **Intelligent matching** of filenames to TMDB episodes
- 🌐 **Multi-language support** (German, English, French, etc.)
- 📁 **Batch processing** of entire seasons at once
- ✅ **Preview** before renaming

### Music
- 🎵 **Metadata-based renaming** from ID3 tags, FLAC tags, etc.
- 🎼 **Supported formats**: FLAC, WAV, MP3, OGG Vorbis, OGG Opus, AIFF, ASF, Musepack
- 🔤 **Umlaut normalization** for compatibility
- 📋 **Schema**: `Tracknr - Artist - Title.ext`
- 🎹 **Artist and album filters** in the user interface

### General
- 🖥️ **Modern web interface** with Vue 3
- 🐳 **Fully dockerized** with Docker Compose
- 🔄 **Real-time updates** of directory list
- 🚀 **Reverse proxy** with Nginx (no CORS issues)
- 📊 **File system monitoring** with Watchdog

## Architecture

### Technology Stack

**Backend:**
- Python 3.12 (LTS)
- FastAPI + Uvicorn
- TMDB API (The Movie Database)
- Mutagen (Audio-Metadata-Handling)
- Watchdog (Filesystem-Monitoring)
- python-dotenv

**Frontend:**
- Vue 3 (Composition API)
- Vite (Build-Tool)
- Nginx (Reverse Proxy + Static File Serving)
- Node 20 LTS

**Infrastructure:**
- Docker + Docker Compose
- Multi-stage Docker Builds
- Bridge Network for service communication

## Prerequisites

- **Docker** (Version 20.10 or higher)
- **Docker Compose** (Version 2.0 or higher)
- **TMDB API Key** ([free at](https://www.themoviedb.org/settings/api))
- **Media directory** with appropriate permissions

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/TXCJulian/Jellyflix-Helper.git
cd Jellyflix-Helper
```

### Step 2: Get TMDB API Key

1. Register on [themoviedb.org](https://www.themoviedb.org/)
2. Go to Settings → API
3. Request an API Key (free)
4. Copy your API Key

### Step 3: Adjust Configuration

Edit the `docker-compose.yml` and adjust the following values:

```yaml
environment:
  - TMDB_API_KEY=YOUR_TMDB_API_KEY_HERE  # Your API Key
volumes:
  - /path/to/your/media:/media:rw  # Your media path
```

### Step 4: Start Containers

```powershell
docker compose up --build
```

### Step 5: Open Application

- **Frontend**: http://localhost:3333
- **Backend API**: http://localhost:3332
- **API Documentation**: http://localhost:3332/docs

## Configuration

### Backend Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `BASE_PATH` | Base path to media in container | `/media` | `/media` |
| `TVSHOW_FOLDER_NAME` | Name of TV shows folder | `TV Shows` | `TV Shows` |
| `MUSIC_FOLDER_NAME` | Name of music folder | `Music` | `Music` |
| `TMDB_API_KEY` | TMDB API key (required) | - | `abc123...` |
| `VALID_VIDEO_EXT` | Valid video file extensions | `{'.mp4', '.mkv', '.mov', '.avi'}` | - |
| `VALID_MUSIC_EXT` | Valid music file extensions | `{'.flac', '.wav', '.mp3'}` | - |

### Directory Structure

The application expects the following structure in your media directory:

```
/media/
├── TV Shows/
│   ├── Breaking Bad/
│   │   ├── Season 01/
│   │   │   ├── episode1.mkv
│   │   │   ├── episode2.mkv
│   │   │   └── ...
│   │   └── Season 02/
│   │       └── ...
│   └── ...
└── Music/
    ├── Artist Name/
    │   ├── Album Name/
    │   │   ├── 01-track.flac
    │   │   ├── 02-track.flac
    │   │   └── ...
    │   └── ...
    └── ...
```

## API Endpoints

### TV Shows

#### `GET /directories/tvshows`
List all TV show directories

**Query Parameters:**
- `series` (optional): Filter by series name
- `season` (optional): Filter by season number

**Example:**
```bash
curl "http://localhost:3332/directories/tvshows?series=Breaking%20Bad&season=1"
```

**Response:**
```json
{
  "directories": [
    "/media/TV Shows/Breaking Bad/Season 01"
  ]
}
```

#### `POST /rename/episodes`
Rename episodes in a directory

**Form Data:**
- `directory`: Path to season directory
- `series`: Series name
- `season`: Season number (1-99)
- `language`: Language for TMDB (de-DE, en-US, etc.)
- `preview` (optional): "true" for preview without renaming

**Example:**
```bash
curl -X POST "http://localhost:3332/rename/episodes" \
  -F "directory=/media/TV Shows/Breaking Bad/Season 01" \
  -F "series=Breaking Bad" \
  -F "season=1" \
  -F "language=de-DE" \
  -F "preview=false"
```

**Response:**
```json
{
  "renamed": [
    {
      "old": "ep1.mkv",
      "new": "S01E01 - Pilot.mkv"
    }
  ]
}
```

### Music

#### `GET /directories/music`
List all music directories

**Query Parameters:**
- `artist` (optional): Filter by artist
- `album` (optional): Filter by album

**Example:**
```bash
curl "http://localhost:3332/directories/music?artist=Pink%20Floyd"
```

#### `POST /rename/music`
Rename music files

**Form Data:**
- `directory`: Path to album directory
- `preview` (optional): "true" for preview without renaming

**Example:**
```bash
curl -X POST "http://localhost:3332/rename/music" \
  -F "directory=/media/Music/Pink Floyd/The Wall" \
  -F "preview=false"
```

## Architecture

### Overview

The project uses an Nginx reverse proxy in the frontend container to transparently forward backend API requests. The browser communicates only with one port (3333), and Nginx routes the requests internally to the backend.

### Request Flow

```
Browser                    Frontend Container               Backend Container
  |                             (Nginx)                          (FastAPI)
  |                               |                                  |
  |--[1] GET :3333/directories--->|                                  |
  |    (HTTP Request)             |                                  |
  |                               |--[2] proxy_pass----------------->|
  |                               |    http://helper-backend:3332    |
  |                               |    (Docker network)              |
  |                               |                                  |
  |                               |<---[3] JSON response-------------|
  |<--[4] JSON response-----------|                                  |
```

**Step by Step:**

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

✅ No CORS issues: from the browser's perspective, all requests are same-origin  
✅ Single entry point: only port 3333 needs to be exposed  
✅ Backend can stay private: port 3332 doesn't have to be published  
✅ Simple SSL termination: HTTPS only at Nginx  
✅ Standard production pattern: API gateway in front of microservices

### Important Notes

- The browser does not communicate directly with the backend — only with port 3333
- `helper-backend` is only resolvable within the Docker network
- The frontend `.env` is empty (`VITE_API_BASE_URL=""`), the app uses `window.location.origin` as the base URL

> **⚠️ Warning:**  
> If you change service names in `docker-compose.yml` or `deploy.yml` (e.g., `helper-backend` → `my-backend`), you must also adjust them in the Nginx configuration (`frontend/nginx-app.conf`) in the `proxy_pass` lines!

### Important Files

| File | Description |
|------|-------------|
| `docker-compose.yml` | Local setup, build contexts, network |
| `deploy.yml` | Deployment template with pre-built images |
| `frontend/nginx-app.conf` | Nginx reverse proxy configuration (API routing) |
| `frontend/.env` | API base URL (empty = same-origin via Nginx) |
| `backend/Dockerfile` | Python 3.12 multi-stage build |
| `frontend/Dockerfile` | Node 20 multi-stage build with Nginx runtime |
| `backend/requirements.txt` | Python dependencies |
| `frontend/package.json` | Node dependencies |

## Deployment

### Local Development

For local development with hot-reload:

```powershell
# Backend (with auto-reload)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 3332

# Frontend (dev server)
cd frontend
npm install
npm run dev
```

### Production with Docker Compose

Use `deploy.yml` as a template for server deployment:

```powershell
# Pull images from Docker Hub
docker compose -f deploy.yml pull

# Start containers
docker compose -f deploy.yml up -d

# View logs
docker compose -f deploy.yml logs -f

# Stop containers
docker compose -f deploy.yml down
```

**Important:** Adjust the volumes and environment variables in `deploy.yml` to your environment!

## Push Images to Docker Hub

The compose/deploy files expect the following images:

- `bosscock/jellyflix-helper:backend`
- `bosscock/jellyflix-helper:frontend`

**If you want to push the Images to your own Docker-Repository**, replace `bosscock` it in the commands below and in `deploy.yml`/`docker-compose.yml`.

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

**Note:** If you want to use your own network (e.g., `helper-network`), add a `networks` section to `deploy.yml` and connect both services to it. The frontend will then reach the backend at `http://helper-backend:3332`.

## Development

### Project Structure

```
Jellyflix-Helper/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Main application + API routes
│   │   ├── rename_episodes.py # TV show renaming
│   │   ├── rename_music.py    # Music renaming
│   │   └── get_dirs.py        # Directory scanning
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 3 Frontend
│   ├── src/
│   │   ├── App.vue            # Main component
│   │   └── main.js
│   ├── nginx-app.conf         # Nginx reverse proxy config
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Local development
├── deploy.yml                  # Production deployment
└── README.md
```

### Code Quality

**Backend:**
```powershell
# Formatting with black
pip install black
black backend/app/

# Linting with ruff
pip install ruff
ruff check backend/app/
```

**Frontend:**
```powershell
# Formatting with prettier
cd frontend
npm run format
```

### Testing

```powershell
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm run test
```

## Troubleshooting

### Problem: Backend cannot be started

**Symptom:** Container starts, but stops immediately

**Solution:**
```powershell
# View logs
docker compose logs helper-backend

# Common causes:
# 1. Missing TMDB_API_KEY
# 2. Invalid media path in volume
# 3. Missing permissions for /media
```

### Problem: Frontend cannot reach backend

**Symptom:** API calls fail with 502 Bad Gateway

**Solution:**
1. Check if both containers are in the same network:
```powershell
docker network inspect helper-network
```

2. Check service names in `nginx-app.conf`:
```nginx
proxy_pass http://helper-backend:3332;  # Must match docker-compose.yml
```

3. Check backend logs:
```powershell
docker compose logs helper-backend
```

### Problem: TMDB API error

**Symptom:** "Series not found" or API error

**Solution:**
1. Check API key:
```powershell
docker compose exec helper-backend env | grep TMDB_API_KEY
```

2. Test API key manually:
```bash
curl "https://api.themoviedb.org/3/search/tv?api_key=YOUR_KEY&query=Breaking+Bad"
```

3. Check API limits (TMDB has rate limits)

### Problem: Permissions

**Symptom:** Files cannot be renamed

**Solution:**
```powershell
# On the host: Check permissions
icacls "D:\Path\to\Media"

# In container: Check permissions
docker compose exec helper-backend ls -la /media

# Solution: Give the container write rights
# Option 1: Change host permissions
# Option 2: Use Docker user mapping
```

### Problem: Port already in use

**Symptom:** "port is already allocated"

**Solution:**
```powershell
# Check which process uses the port
netstat -ano | findstr :3333
netstat -ano | findstr :3332

# Change ports in docker-compose.yml
ports:
  - "8080:3000"  # Instead of 3333:3000
```

### Problem: Umlauts are displayed incorrectly

**Symptom:** Filenames with ä, ö, ü are wrong

**Solution:**
- Music: Check if audio tags are UTF-8 encoded
- TV Shows: Check TMDB language setting (`language` parameter)
- The code normalizes umlauts automatically (ä→ae, ö→oe, ü→ue)

## Changelog

### Version 1.0.0 (current)
- ✅ Initial release
- ✅ TV show renaming via TMDB
- ✅ Music renaming via metadata
- ✅ Vue 3 web interface
- ✅ Docker Compose setup
- ✅ Nginx reverse proxy
- ✅ Multi-language support

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for the free API
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python framework
- [Vue.js](https://vuejs.org/) for the reactive frontend framework
- [Mutagen](https://mutagen.readthedocs.io/) for audio metadata handling

## Support

For questions or issues:
- Open an [issue](https://github.com/TXCJulian/Jellyflix-Helper/issues)
- Contact the maintainer

---

**Made for Jellyfin and Plex users**
