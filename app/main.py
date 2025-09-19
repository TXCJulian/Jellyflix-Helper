from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn
import os

from rename_tmdb import rename_episodes

load_dotenv("dependencies/.env")

BASE_PATH = os.getenv("BASE_PATH")
VALID_EXT = set(eval(os.getenv("VALID_EXT", "{}")))

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def has_valid_files(path):
    for _, _, files in os.walk(path):
        for f in files:
            if any(f.lower().endswith(ext.lower()) for ext in VALID_EXT):
                return True
    return False


def get_dirs(base):
    directories = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not d.endswith(".trickplay") and ".trickplay" not in root]
        for d in dirs:
            full_path = os.path.join(root, d)
            if has_valid_files(full_path):
                rel_path = os.path.relpath(full_path, base)
                directories.append(rel_path.replace("\\", "/"))
    return sorted(directories)


@app.get("/")
def index(request: Request):
    dirs = get_dirs(BASE_PATH)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "directories": dirs,
        "log": "",
        "error": None
    })


@app.post("/")
def rename(
    request: Request,
    series: str = Form(...),
    season: int = Form(...),
    directory: str = Form(...),
    dry_run: bool = Form(False),
    assign_seq: bool = Form(False),
    threshold: float = Form(0.6),
    lang: str = Form("de")
):
    path = os.path.join(BASE_PATH, directory)
    if not os.path.isdir(path):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "directories": get_dirs(BASE_PATH),
            "log": "",
            "error": "Ordner nicht gefunden"
        })

    logs, error = rename_episodes(
        series=series,
        season=season,
        directory=path,
        lang=lang,
        dry_run=dry_run,
        threshold=threshold,
        assign_seq=assign_seq
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "directories": get_dirs(BASE_PATH),
        "log": "\n".join(logs),
        "error": error
    })


if __name__ == "__main__":
    uvicorn.run("main:app", port=3333)