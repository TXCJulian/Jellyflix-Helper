import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv("dependencies/.env")

BASE_PATH = os.getenv("BASE_PATH")
VALID_EXT = set(eval(os.getenv("VALID_EXT", "{}")))

def has_valid_files(path: str) -> bool:
    for _, _, files in os.walk(path):
        for f in files:
            if any(f.lower().endswith(ext.lower()) for ext in VALID_EXT):
                return True
    return False

def get_dirs(base: str) -> list[str]:
    directories = []
    for root, dirs, _ in os.walk(base):
        dirs[:] = [
            d for d in dirs
            if not d.endswith(".trickplay") and ".trickplay" not in root
        ]
        for d in dirs:
            full_path = os.path.join(root, d)
            if has_valid_files(full_path):
                rel_path = os.path.relpath(full_path, base)
                directories.append(rel_path.replace("\\", "/"))
    return sorted(directories)

@lru_cache(maxsize=1)
def _get_all_dirs_cached() -> list[str]:
    return get_dirs(BASE_PATH)