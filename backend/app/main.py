from fastapi import FastAPI, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from rename_tmdb import rename_episodes
from rename_music import rename_music_files
from get_dirs import (
    _get_all_dirs_cached,
    _get_tvshow_dirs_cached,
    _get_music_dirs_cached,
    BASE_PATH,
    TVSHOW_FOLDER_NAME,
    MUSIC_FOLDER_NAME
)

load_dotenv("dependencies/.env")

# Aus .env: gültige Video-Extensions
VALID_VIDEO_EXT = set(eval(os.getenv("VALID_VIDEO_EXT", "{'.mp4', '.mkv', '.mov', '.avi'}")))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DirChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            _get_all_dirs_cached.cache_clear()
            _get_tvshow_dirs_cached.cache_clear()
            _get_music_dirs_cached.cache_clear()

    def on_deleted(self, event):
        if event.is_directory:
            _get_all_dirs_cached.cache_clear()
            _get_tvshow_dirs_cached.cache_clear()
            _get_music_dirs_cached.cache_clear()

    def on_moved(self, event):
        if event.is_directory:
            _get_all_dirs_cached.cache_clear()
            _get_tvshow_dirs_cached.cache_clear()
            _get_music_dirs_cached.cache_clear()


@app.on_event("startup")
def start_fs_watcher():
    handler = DirChangeHandler()
    observer = Observer()
    observer.schedule(handler, BASE_PATH, recursive=True)
    observer.start()
    app.state.fs_observer = observer


@app.on_event("shutdown")
def stop_fs_watcher():
    observer = app.state.fs_observer
    observer.stop()
    observer.join()


@app.get("/directories")
def list_directories(
    series: str | None = Query(None, description="Optionaler Serienfilter"),
    season: int | None = Query(None, description="Optionale Staffelnummer")
):
    all_dirs = _get_tvshow_dirs_cached()

    # nach Serie filtern
    filtered = all_dirs
    if series:
        series_lc = series.lower()
        filtered = [d for d in filtered if series_lc in d.lower()]

    # nach Staffel filtern
    if season is not None:
        season_str = f"{season:02d}"
        pattern = f"/season {season_str}"
        filtered = [
            d for d in filtered
            if d.lower().endswith(pattern)
        ]

    return {"directories": filtered}


@app.post("/directories/refresh")
def refresh_directories():
    _get_all_dirs_cached.cache_clear()
    _get_tvshow_dirs_cached.cache_clear()
    return {"status": "ok"}


# ============= MUSIC ROUTES =============

@app.get("/music/directories")
def list_music_directories(
    artist: str | None = Query(None, description="Optionaler Künstlerfilter"),
    album: str | None = Query(None, description="Optionales Album-Filter")
):
    """Liste alle Musik-Alben-Verzeichnisse."""
    all_dirs = _get_music_dirs_cached()

    # nach Künstler filtern
    filtered = all_dirs
    if artist:
        artist_lc = artist.lower()
        filtered = [d for d in filtered if artist_lc in d.lower()]

    # nach Album filtern (optional)
    if album:
        album_lc = album.lower()
        filtered = [d for d in filtered if album_lc in d.lower()]

    return {"directories": filtered}


@app.post("/music/directories/refresh")
def refresh_music_directories():
    """Leert den Cache für Musik-Verzeichnisse."""
    _get_music_dirs_cached.cache_clear()
    return {"status": "ok"}


@app.post("/music/rename")
async def rename_music(
    artist: str = Form(...),
    directory: str = Form(...),
    dry_run: bool = Form(...)
):
    """Benennt FLAC-Dateien in einem Album-Ordner um."""
    path = os.path.join(BASE_PATH, MUSIC_FOLDER_NAME, directory)
    
    if not os.path.isdir(path):
        return {
            "success": False,
            "error": "Ordner nicht gefunden",
            "log": [],
            "directories": _get_music_dirs_cached()
        }

    logs, error = rename_music_files(
        folder=path,
        dry_run=dry_run
    )

    return {
        "success": error is None,
        "error": error,
        "log": logs,
        "directories": _get_music_dirs_cached()
    }


@app.post("/rename")
async def rename(
    series: str = Form(...),
    season: int = Form(...),
    directory: str = Form(...),
    dry_run: bool = Form(...),
    assign_seq: bool = Form(...),
    threshold: float = Form(...),
    lang: str = Form(...)
):
    path = os.path.join(BASE_PATH, TVSHOW_FOLDER_NAME, directory)
    if not os.path.isdir(path):
        return {
            "success": False,
            "error": "Ordner nicht gefunden",
            "log": [],
            "directories": _get_tvshow_dirs_cached()
        }

    logs, error = rename_episodes(
        series=series,
        season=season,
        directory=path,
        lang=lang,
        dry_run=dry_run,
        threshold=threshold,
        assign_seq=assign_seq
    )

    return {
        "success": error is None,
        "error": error,
        "log": logs,
        "directories": _get_tvshow_dirs_cached()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=3332)