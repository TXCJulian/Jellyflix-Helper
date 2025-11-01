import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv("dependencies/.env")

BASE_PATH = os.getenv("BASE_PATH", "/media")
TVSHOW_FOLDER_NAME = os.getenv("TVSHOW_FOLDER_NAME", "TV Shows")
MUSIC_FOLDER_NAME = os.getenv("MUSIC_FOLDER_NAME", "Music")
# Aus .env laden: gültige Video- und Musik-Dateiendungen
# Hinweis: ENV-Werte sind in Python-Set-Syntax anzugeben, z. B. "{'.mp4', '.mkv'}"
VALID_VIDEO_EXT = set(eval(os.getenv("VALID_VIDEO_EXT", "{'.mp4', '.mkv', '.mov', '.avi'}")))
VALID_MUSIC_EXT = set(eval(os.getenv("VALID_MUSIC_EXT", "{'.flac', '.wav', '.mp3'}")))

def has_valid_files(path: str, extensions: set[str]) -> bool:
    """Prüft ob Ordner Dateien mit gültigen Extensions enthält."""
    for _, _, files in os.walk(path):
        for f in files:
            if any(f.lower().endswith(ext.lower()) for ext in extensions):
                return True
    return False

def get_dirs(base: str, extensions: set[str], exclude_patterns: list[str] | None = None) -> list[str]:
    """
    Scannt einen Basis-Ordner nach Unterordnern mit gültigen Dateien.
    
    Args:
        base: Basis-Pfad zum Scannen
        extensions: Set von gültigen Dateiendungen
        exclude_patterns: Liste von Mustern, die ausgeschlossen werden sollen
    
    Returns:
        Sortierte Liste von relativen Pfaden
    """
    if not os.path.isdir(base):
        return []
    
    if exclude_patterns is None:
        exclude_patterns = [".trickplay"]
    
    directories = []
    for root, dirs, _ in os.walk(base):
        # Exclude-Filter anwenden
        dirs[:] = [
            d for d in dirs
            if not any(pattern in d or pattern in root for pattern in exclude_patterns)
        ]
        
        for d in dirs:
            full_path = os.path.join(root, d)
            if has_valid_files(full_path, extensions):
                rel_path = os.path.relpath(full_path, base)
                directories.append(rel_path.replace("\\", "/"))
    
    return sorted(directories)

# TV Shows Directory Cache
@lru_cache(maxsize=1)
def _get_tvshow_dirs_cached() -> list[str]:
    """Gibt alle TV Show Verzeichnisse zurück."""
    tvshow_path = os.path.join(BASE_PATH, TVSHOW_FOLDER_NAME)
    return get_dirs(tvshow_path, VALID_VIDEO_EXT, exclude_patterns=[".trickplay"])

# Music Directory Cache
@lru_cache(maxsize=1)
def _get_music_dirs_cached() -> list[str]:
    """Gibt alle Musik-Alben-Verzeichnisse zurück."""
    music_path = os.path.join(BASE_PATH, MUSIC_FOLDER_NAME)
    return get_dirs(music_path, VALID_MUSIC_EXT)

# Backward compatibility
@lru_cache(maxsize=1)
def _get_all_dirs_cached() -> list[str]:
    """Legacy: Gibt TV Show Verzeichnisse zurück (für Kompatibilität)."""
    return _get_tvshow_dirs_cached()