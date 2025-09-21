from fastapi import FastAPI, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from functools import lru_cache
import os
import re

from rename_tmdb import rename_episodes

load_dotenv("dependencies/.env")

BASE_PATH = os.getenv("BASE_PATH")
VALID_EXT = set(eval(os.getenv("VALID_EXT", "{}")))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def has_valid_files(path: str) -> bool:
    for _, _, files in os.walk(path):
        for f in files:
            if any(f.lower().endswith(ext.lower()) for ext in VALID_EXT):
                return True
    return False

def get_dirs(base: str) -> list[str]:
    directories = []
    for root, dirs, _ in os.walk(base):
        dirs[:] = [d for d in dirs if not d.endswith(".trickplay") and ".trickplay" not in root]
        for d in dirs:
            full_path = os.path.join(root, d)
            if has_valid_files(full_path):
                rel_path = os.path.relpath(full_path, base)
                directories.append(rel_path.replace("\\", "/"))
    return sorted(directories)

@lru_cache(maxsize=1)
def _get_all_dirs_cached() -> list[str]:
    return get_dirs(BASE_PATH)

@app.get("/directories")
def list_directories(
    series: str | None = Query(None, description="Optionaler Serienfilter"),
    season: int | None = Query(None, description="Optionale Staffelnummer")
):
    all_dirs = _get_all_dirs_cached()

    filtered = all_dirs
    if series:
        series_lc = series.lower()
        filtered = [d for d in filtered if series_lc in d.lower()]

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
    return {"status": "ok"}

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
    path = os.path.join(BASE_PATH, directory)
    if not os.path.isdir(path):
        return {
            "success": False,
            "error": "Ordner nicht gefunden",
            "log": [],
            "directories": get_dirs(BASE_PATH)
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
        "directories": get_dirs(BASE_PATH)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=3333)