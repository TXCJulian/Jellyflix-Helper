# Jellyflix Helper

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)

**Ein automatisches Umbenennungstool für TV-Serien und Musik-Dateien mit einer benutzerfreundlichen Web-Oberfläche.**  
*An automatic renaming tool for TV shows and music files with a user-friendly web interface.*

## 📋 Inhaltsverzeichnis / Table of Contents

- [Überblick / Overview](#-überblick--overview)
- [Features](#-features)
- [Architektur / Architecture](#-architektur--architecture)
- [Voraussetzungen / Prerequisites](#-voraussetzungen--prerequisites)
- [Installation](#-installation)
- [Konfiguration / Configuration](#-konfiguration--configuration)
- [API-Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Entwicklung / Development](#-entwicklung--development)
- [Fehlerbehebung / Troubleshooting](#-fehlerbehebung--troubleshooting)

## 📖 Überblick / Overview

**Deutsch:**  
Jellyflix Helper ist ein dockerisiertes Tool, das TV-Serien-Episoden und Musik-Dateien automatisch nach einem standardisierten Schema umbenennt. Es nutzt die TMDB-API für TV-Serien-Metadaten und Mutagen für Musik-Tags. Die Anwendung besteht aus einem FastAPI-Backend (Python) und einem Vue 3-Frontend (Vite, Nginx), die über ein Docker-Netzwerk kommunizieren.

**English:**  
Jellyflix Helper is a dockerized tool that automatically renames TV show episodes and music files according to a standardized schema. It uses the TMDB API for TV series metadata and Mutagen for music tags. The application consists of a FastAPI backend (Python) and a Vue 3 frontend (Vite, Nginx), which communicate over a Docker network.

## ✨ Features

### TV-Serien / TV Shows
- 🔍 **Automatische Seriensuche** über TMDB-API (mehrsprachig)
- 📺 **Episoden-Umbenennung** nach dem Schema: `S01E01 - Episodentitel.ext`
- 🎯 **Intelligentes Matching** von Dateinamen zu TMDB-Episoden
- 🌐 **Mehrsprachige Unterstützung** (Deutsch, Englisch, Französisch, etc.)
- 📁 **Batch-Verarbeitung** ganzer Staffeln auf einmal
- ✅ **Vorschau** vor der Umbenennung

### Musik / Music
- 🎵 **Metadata-basierte Umbenennung** aus ID3-Tags, FLAC-Tags, etc.
- 🎼 **Unterstützte Formate**: FLAC, WAV, MP3, OGG Vorbis, OGG Opus, AIFF, ASF, Musepack
- 🔤 **Umlaute-Normalisierung** für Kompatibilität
- 📋 **Schema**: `Tracknr - Künstler - Titel.ext`
- 🎹 **Künstler- und Album-Filter** in der Benutzeroberfläche

### Allgemein / General
- 🖥️ **Moderne Web-Oberfläche** mit Vue 3
- 🐳 **Vollständig dockerisiert** mit Docker Compose
- 🔄 **Echtzeit-Updates** der Verzeichnisliste
- 🚀 **Reverse Proxy** mit Nginx (keine CORS-Probleme)
- 📊 **File System Monitoring** mit Watchdog

## 🏗️ Architektur / Architecture

### Technologie-Stack / Technology Stack

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
- Bridge Network für Service-Kommunikation

## 🔧 Voraussetzungen / Prerequisites

- **Docker** (Version 20.10 oder höher / 20.10 or higher)
- **Docker Compose** (Version 2.0 oder höher / 2.0 or higher)
- **TMDB API Key** ([kostenlos erhältlich / free at](https://www.themoviedb.org/settings/api))
- **Medien-Verzeichnis** mit entsprechenden Berechtigungen

## 🚀 Installation

### Schritt 1: Repository klonen / Clone Repository

```bash
git clone https://github.com/TXCJulian/Jellyflix-Helper.git
cd Jellyflix-Helper
```

### Schritt 2: TMDB API Key besorgen / Get TMDB API Key

1. Registriere dich auf [themoviedb.org](https://www.themoviedb.org/)
2. Gehe zu Einstellungen → API
3. Beantrage einen API Key (kostenlos)
4. Kopiere deinen API Key

### Schritt 3: Konfiguration anpassen / Adjust Configuration

Bearbeite die `docker-compose.yml` und passe folgende Werte an:

```yaml
environment:
  - TMDB_API_KEY=DEIN_TMDB_API_KEY_HIER  # Dein API Key
volumes:
  - /pfad/zu/deinen/medien:/media:rw  # Dein Medien-Pfad
```

### Schritt 4: Container starten / Start Containers

```powershell
docker compose up --build
```

### Schritt 5: Anwendung öffnen / Open Application

- **Frontend**: http://localhost:3333
- **Backend API**: http://localhost:3332
- **API Dokumentation**: http://localhost:3332/docs

## ⚙️ Konfiguration / Configuration

### Backend-Umgebungsvariablen / Backend Environment Variables

| Variable | Beschreibung | Standard | Beispiel |
|----------|--------------|----------|----------|
| `BASE_PATH` | Basis-Pfad zu den Medien im Container | `/media` | `/media` |
| `TVSHOW_FOLDER_NAME` | Name des TV-Serien-Ordners | `TV Shows` | `TV Shows` |
| `MUSIC_FOLDER_NAME` | Name des Musik-Ordners | `Music` | `Music` |
| `TMDB_API_KEY` | TMDB API Schlüssel (erforderlich) | - | `abc123...` |
| `VALID_VIDEO_EXT` | Gültige Video-Dateierweiterungen | `{'.mp4', '.mkv', '.mov', '.avi'}` | - |
| `VALID_MUSIC_EXT` | Gültige Musik-Dateierweiterungen | `{'.flac', '.wav', '.mp3'}` | - |

### Verzeichnisstruktur / Directory Structure

Die Anwendung erwartet folgende Struktur in deinem Medien-Verzeichnis:

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

## 📡 API-Endpoints

### TV-Serien / TV Shows

#### `GET /directories/tvshows`
Liste alle TV-Serien-Verzeichnisse auf / List all TV show directories

**Query Parameter:**
- `series` (optional): Filter nach Serienname
- `season` (optional): Filter nach Staffelnummer

**Beispiel / Example:**
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
Benenne Episoden in einem Verzeichnis um / Rename episodes in a directory

**Form Data:**
- `directory`: Pfad zum Staffel-Verzeichnis
- `series`: Serienname
- `season`: Staffelnummer (1-99)
- `language`: Sprache für TMDB (de-DE, en-US, etc.)
- `preview` (optional): "true" für Vorschau ohne Umbenennung

**Beispiel / Example:**
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

### Musik / Music

#### `GET /directories/music`
Liste alle Musik-Verzeichnisse auf / List all music directories

**Query Parameter:**
- `artist` (optional): Filter nach Künstler
- `album` (optional): Filter nach Album

**Beispiel / Example:**
```bash
curl "http://localhost:3332/directories/music?artist=Pink%20Floyd"
```

#### `POST /rename/music`
Benenne Musik-Dateien um / Rename music files

**Form Data:**
- `directory`: Pfad zum Album-Verzeichnis
- `preview` (optional): "true" für Vorschau ohne Umbenennung

**Beispiel / Example:**
```bash
curl -X POST "http://localhost:3332/rename/music" \
  -F "directory=/media/Music/Pink Floyd/The Wall" \
  -F "preview=false"
```

## 🏗️ Architektur / Architecture

### Überblick / Overview

Das Projekt nutzt einen Nginx Reverse Proxy im Frontend-Container, um Backend-API-Anfragen transparent weiterzuleiten. Der Browser kommuniziert nur mit einem Port (3333), und Nginx routet die Anfragen intern zum Backend.

### Request Flow / Anfrage-Ablauf

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

**Schritt für Schritt / Step by Step:**

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

### Wichtige Hinweise / Important Notes

- Der Browser kommuniziert nicht direkt mit dem Backend — nur mit Port 3333
- `helper-backend` ist nur innerhalb des Docker-Netzwerks auflösbar
- Die Frontend `.env` ist leer (`VITE_API_BASE_URL=""`), die App nutzt `window.location.origin` als Basis-URL

> **⚠️ Achtung / Warning:**  
> Wenn du Service-Namen in `docker-compose.yml` oder `deploy.yml` änderst (z.B. `helper-backend` → `my-backend`), musst du diese auch in der Nginx-Konfiguration (`frontend/nginx-app.conf`) in den `proxy_pass`-Zeilen anpassen!

### Wichtige Dateien / Important Files

| Datei / File | Beschreibung / Description |
|--------------|---------------------------|
| `docker-compose.yml` | Lokales Setup, Build-Kontexte, Netzwerk |
| `deploy.yml` | Deployment-Vorlage mit vorgebauten Images |
| `frontend/nginx-app.conf` | Nginx Reverse Proxy Konfiguration (API-Routing) |
| `frontend/.env` | API Base URL (leer = same-origin via Nginx) |
| `backend/Dockerfile` | Python 3.12 Multi-Stage Build |
| `frontend/Dockerfile` | Node 20 Multi-Stage Build mit Nginx Runtime |
| `backend/requirements.txt` | Python-Dependencies |
| `frontend/package.json` | Node-Dependencies |

## 🚢 Deployment

### Lokale Entwicklung / Local Development

Für lokale Entwicklung mit Hot-Reload:

```powershell
# Backend (mit Auto-Reload)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 3332

# Frontend (Dev-Server)
cd frontend
npm install
npm run dev
```

### Produktion mit Docker Compose / Production with Docker Compose

Verwende `deploy.yml` als Vorlage für Server-Deployment:

```powershell
# Images von Docker Hub pullen
docker compose -f deploy.yml pull

# Container starten
docker compose -f deploy.yml up -d

# Logs ansehen
docker compose -f deploy.yml logs -f

# Container stoppen
docker compose -f deploy.yml down
```

**Wichtig:** Passe in `deploy.yml` die Volumes und Umgebungsvariablen an deine Umgebung an!

## 🐳 Docker Images auf Docker Hub veröffentlichen / Push Images to Docker Hub

Die compose/deploy files erwarten folgende Images:

- `bosscock/jellyflix-helper:backend`
- `bosscock/jellyflix-helper:frontend`

**Wenn dein Docker Hub Username nicht `bosscock` ist**, ersetze ihn in den Befehlen unten und in `deploy.yml`/`docker-compose.yml`.

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

**Hinweis:** Wenn du ein eigenes Netzwerk verwenden möchtest (z.B. `helper-network`), füge einen `networks`-Abschnitt zu `deploy.yml` hinzu und verbinde beide Services damit. Das Frontend erreicht das Backend dann unter `http://helper-backend:3332`.

## 💻 Entwicklung / Development

### Projekt-Struktur / Project Structure

```
Jellyflix-Helper/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Hauptanwendung + API-Routen
│   │   ├── rename_episodes.py # TV-Serien Umbenennung
│   │   ├── rename_music.py    # Musik Umbenennung
│   │   └── get_dirs.py        # Verzeichnis-Scanning
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 3 Frontend
│   ├── src/
│   │   ├── App.vue            # Hauptkomponente
│   │   └── main.js
│   ├── nginx-app.conf         # Nginx Reverse Proxy Config
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Lokales Development
├── deploy.yml                  # Production Deployment
└── README.md
```

### Code-Qualität / Code Quality

**Backend:**
```powershell
# Formatierung mit black
pip install black
black backend/app/

# Linting mit ruff
pip install ruff
ruff check backend/app/
```

**Frontend:**
```powershell
# Formatierung mit prettier
cd frontend
npm run format
```

### Testing

```powershell
# Backend Tests (wenn implementiert)
cd backend
pytest

# Frontend Tests (wenn implementiert)
cd frontend
npm run test
```

## 🐛 Fehlerbehebung / Troubleshooting

### Problem: Backend kann nicht gestartet werden

**Symptom:** Container startet, stoppt aber sofort wieder

**Lösung:**
```powershell
# Logs ansehen
docker compose logs helper-backend

# Häufige Ursachen:
# 1. Fehlender TMDB_API_KEY
# 2. Ungültiger Medien-Pfad im Volume
# 3. Fehlende Berechtigungen für /media
```

### Problem: Frontend kann Backend nicht erreichen

**Symptom:** API-Aufrufe schlagen fehl mit 502 Bad Gateway

**Lösung:**
1. Prüfe, ob beide Container im gleichen Netzwerk sind:
```powershell
docker network inspect helper-network
```

2. Prüfe Service-Namen in `nginx-app.conf`:
```nginx
proxy_pass http://helper-backend:3332;  # Muss mit docker-compose.yml übereinstimmen
```

3. Prüfe Backend-Logs:
```powershell
docker compose logs helper-backend
```

### Problem: TMDB API Fehler

**Symptom:** "Serie nicht gefunden" oder API-Fehler

**Lösung:**
1. Prüfe API Key:
```powershell
docker compose exec helper-backend env | grep TMDB_API_KEY
```

2. Teste API Key manuell:
```bash
curl "https://api.themoviedb.org/3/search/tv?api_key=DEIN_KEY&query=Breaking+Bad"
```

3. Prüfe API-Limits (TMDB hat Rate-Limits)

### Problem: Berechtigungen / Permissions

**Symptom:** Dateien können nicht umbenannt werden

**Lösung:**
```powershell
# Auf dem Host: Prüfe Berechtigungen
icacls "D:\Pfad\zu\Medien"

# Im Container: Prüfe Berechtigungen
docker compose exec helper-backend ls -la /media

# Lösung: Gib dem Container Schreibrechte
# Option 1: Ändere Host-Berechtigungen
# Option 2: Nutze Docker user-Mapping
```

### Problem: Port bereits belegt

**Symptom:** "port is already allocated"

**Lösung:**
```powershell
# Prüfe welcher Prozess den Port nutzt
netstat -ano | findstr :3333
netstat -ano | findstr :3332

# Ändere Ports in docker-compose.yml
ports:
  - "8080:3000"  # Statt 3333:3000
```

### Problem: Umlaute werden falsch dargestellt

**Symptom:** Dateinamen mit ä, ö, ü sind falsch

**Lösung:**
- Musik: Prüfe, ob die Audio-Tags UTF-8 kodiert sind
- TV-Shows: Prüfe TMDB-Spracheinstellung (`language` Parameter)
- Der Code normalisiert Umlaute automatisch (ä→ae, ö→oe, ü→ue)

## 📝 Changelog

### Version 1.0.0 (aktuell)
- ✅ Initiales Release
- ✅ TV-Serien Umbenennung via TMDB
- ✅ Musik Umbenennung via Metadata
- ✅ Vue 3 Web-Interface
- ✅ Docker Compose Setup
- ✅ Nginx Reverse Proxy
- ✅ Mehrsprachige Unterstützung

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Forke das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 🙏 Danksagungen / Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) für die kostenlose API
- [FastAPI](https://fastapi.tiangolo.com/) für das exzellente Python-Framework
- [Vue.js](https://vuejs.org/) für das reaktive Frontend-Framework
- [Mutagen](https://mutagen.readthedocs.io/) für Audio-Metadata-Handling

## 📧 Support

Bei Fragen oder Problemen:
- Öffne ein [Issue](https://github.com/TXCJulian/Jellyflix-Helper/issues)
- Kontaktiere den Maintainer

---

**Made for Jellyfin and Plex users**
