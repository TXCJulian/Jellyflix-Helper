# Media Renamer - Erweiterte Version

Ein Docker-basiertes Tool zum automatischen Umbenennen von:
- **TV-Serien-Episoden** basierend auf TMDB-Daten
- **Musik-Dateien (FLAC)** basierend auf Metadaten

## 🎯 Features

### Episode Renamer
- Automatische Umbenennung von TV-Episoden via TMDB API
- Fuzzy-Matching für unscharfe Dateinamen
- Dry-Run Modus zum Testen
- Sequential Assignment für fehlende Episoden
- Mehrsprachig (DE/EN)

### Music Renamer  
- Automatische Umbenennung von FLAC-Dateien basierend auf ID3-Tags
- Format: `{Disc}-{Track} {Title}.flac` (z.B. `01-03 Wonderwall.flac`)
- Automatische Bereinigung von Mojibake und ungültigen Zeichen
- Duplikat-Erkennung und Cleanup
- Dry-Run Modus

## 📁 Ordnerstruktur

Das Projekt erwartet folgende Struktur:

```
/media/
├── TV Shows/
│   ├── Breaking Bad/
│   │   ├── Season 01/
│   │   │   ├── episode1.mkv
│   │   │   └── episode2.mkv
│   │   └── Season 02/
│   └── The Office/
│       └── Season 01/
└── Music/
    ├── The Beatles/
    │   ├── Abbey Road/
    │   │   ├── track1.flac
    │   │   └── track2.flac
    │   └── Revolver/
    └── Pink Floyd/
        └── Dark Side of the Moon/
```

## 🚀 Installation & Start

### Lokale Entwicklung

```bash
# 1. Repository klonen
git clone https://github.com/TXCJulian/Docker-Rename.git
cd Docker-Rename

# 2. Ordnerstruktur erstellen
mkdir -p media/TV\ Shows media/Music

# 3. TMDB API Key setzen (optional als .env)
# Oder direkt in docker-compose.yml eintragen

# 4. Container starten
docker-compose up --build
```

Die Anwendung ist dann verfügbar unter:
- Frontend: http://localhost:3333
- Backend API: http://localhost:3332

### Production Deployment

```bash
# 1. Images bauen und pushen
cd backend
docker build -t bosscock/episode-renamer:backend .
docker push bosscock/episode-renamer:backend

cd ../frontend
docker build -t bosscock/episode-renamer:frontend .
docker push bosscock/episode-renamer:frontend

# 2. Mit deploy.yml starten
docker-compose -f deploy.yml up -d
```

### CasaOS Deployment

1. Netzwerk erstellen (einmalig):
```bash
sudo docker network create renamer-network
```

2. `casaos-deploy.yml` anpassen:
   - `TMDB_API_KEY` eintragen
   - Volume-Pfad auf deinen Media-Ordner setzen

3. In CasaOS importieren und starten

## ⚙️ Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `BASE_PATH` | `/media` | Basis-Pfad für alle Medien |
| `TVSHOW_FOLDER_NAME` | `TV Shows` | Unterordner für TV-Serien |
| `MUSIC_FOLDER_NAME` | `Music` | Unterordner für Musik |
| `TMDB_API_KEY` | - | API-Key von themoviedb.org (für Episode Renamer) |
| `VALID_VIDEO_EXT` | `{'.mp4', '.mkv', '.mov', '.avi'}` | Gültige Video-Extensions |
| `VALID_MUSIC_EXT` | `{'.flac', '.wav', '.mp3'}` | Gültige Musik-Extensions (für Verzeichnis-Scan) |

## 🎨 UI-Übersicht

Das Frontend zeigt zwei Renamer nebeneinander:

```
┌─────────────────────────────────────────────────────────┐
│                    Media Renamer                         │
├──────────────────────────┬──────────────────────────────┤
│   📺 Episode Renamer     │     🎵 Music Renamer        │
│                          │                              │
│  - Serie eingeben        │  - Künstler eingeben        │
│  - Staffel wählen        │  - Album filtern (optional) │
│  - Verzeichnis wählen    │  - Verzeichnis wählen       │
│  - Sprache               │  - Dry-Run                  │
│  - Dry-Run, Threshold    │  - Umbenennen               │
│  - Umbenennen            │                              │
└──────────────────────────┴──────────────────────────────┘
│                    📋 Log-Ausgabe                        │
│  (Gemeinsame Log-Ausgabe für beide Renamer)            │
└─────────────────────────────────────────────────────────┘
```

## 🔧 API-Endpunkte

### Episode Renamer
- `GET /directories?series=...&season=...` - Liste TV-Verzeichnisse
- `POST /directories/refresh` - Cache leeren
- `POST /rename` - Episoden umbenennen

### Music Renamer
- `GET /music/directories?artist=...&album=...` - Liste Musik-Verzeichnisse
- `POST /music/directories/refresh` - Cache leeren
- `POST /music/rename` - FLAC-Dateien umbenennen

## 📝 Änderungen zur Vorgängerversion

1. **Erweiterte Pfadstruktur**: 
   - Von `/tvshows` zu `/media` mit Unterordnern
   - Konfigurierbare Ordnernamen via ENV

2. **Neuer Music Renamer**:
   - Parallel zum Episode Renamer
   - Separates API (`/music/*` Routes)
   - Eigener Directory-Cache

3. **Verbessertes UI**:
   - Zwei-Spalten-Layout (responsive)
   - Gemeinsame Log-Ausgabe über volle Breite
   - Emoji-Icons für bessere Übersicht

4. **Backend-Architektur**:
   - `get_dirs.py`: Separate Funktionen für TV/Music
   - `rename_music.py`: Neue Modul für FLAC-Renaming
   - Caching pro Medientyp

## 🐛 Troubleshooting

### Keine Verzeichnisse werden gefunden
- Prüfe Volume-Mounts in `docker-compose.yml`
- Stelle sicher, dass die Ordnerstruktur stimmt (`/media/TV Shows/` und `/media/Music/`)
- Prüfe Container-Logs: `docker logs episode-renamer_backend`

### Frontend kann Backend nicht erreichen
- Stelle sicher, dass das Netzwerk `renamer-network` existiert
- Prüfe Nginx-Konfiguration in `frontend/nginx-app.conf`
- DevTools → Network → Prüfe `/api/directories` Aufrufe

### FLAC-Dateien werden nicht umbenannt
- Prüfe, ob Metadaten vorhanden sind (Title, Track, Disc)
- Aktiviere Dry-Run, um zu sehen, was passieren würde
- Logs zeigen genau, welche Dateien übersprungen wurden

##  Deployment Details

### Deployment auf CasaOS

1. Stoppen Sie die aktuellen Container:
```bash
sudo docker stop episode-renamer_backend episode-renamer_frontend
sudo docker rm episode-renamer_backend episode-renamer_frontend
```

2. Neue Images bauen und pushen (lokal auf Ihrem Dev-System):
```bash
# Backend
cd backend
docker build -t bosscock/episode-renamer:backend .
docker push bosscock/episode-renamer:backend

# Frontend
cd ../frontend
docker build -t bosscock/episode-renamer:frontend .
docker push bosscock/episode-renamer:frontend
```

3. Verwenden Sie die neue `casaos-deploy.yml` in CasaOS

4. Container starten:
```bash
sudo docker compose -f casaos-deploy.yml up -d
```

### Zugriff

- Frontend: `http://192.168.0.75:3333` (oder aktuelle Host-IP)
- Backend direkt: `http://192.168.0.75:3332` (für API-Tests)

Die Frontend-Anwendung kommuniziert intern über `/api` mit dem Backend, unabhängig von der Host-IP!

## 👤 Autor

TXCJulian
