import os
import re
import unicodedata
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.aiff import AIFF
from mutagen.asf import ASF
from mutagen.musepack import Musepack
import filecmp
from dotenv import load_dotenv
from typing import Optional, Any, Tuple

load_dotenv("dependencies/.env")

VALID_MUSIC_EXT = set(eval(os.getenv("VALID_MUSIC_EXT", "{}"))) or {'.flac', '.wav', '.mp3'}

DISALLOWED_RE = re.compile(r'[\x00-\x1F<>:"/\\|?*]')

def try_decode_bytes(b: bytes) -> str:
    """Versuche mehrere Decodings in Reihenfolge, return str."""
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", errors="replace")

def fix_mojibake_if_needed(s: str) -> str:
    suspicious = any(x in s for x in ("�", "Ã", "Â"))
    if not suspicious:
        return s

    best = s
    best_repl = s.count("�")

    candidates = [
        ("cp1252", "utf-8"),
        ("latin-1", "utf-8"),
        ("utf-8", "cp1252"),
    ]

    for enc_from, enc_to in candidates:
        try:
            cand = s.encode(enc_from, errors="replace").decode(enc_to, errors="replace")
            cand_repl = cand.count("�")
            if cand_repl < best_repl:
                best = cand
                best_repl = cand_repl
        except Exception:
            pass

    return best

def sanitize_tag_value(value) -> str:
    if value is None:
        return ""

    if isinstance(value, bytes):
        s = try_decode_bytes(value)
    else:
        s = str(value)

    s = fix_mojibake_if_needed(s)
    s = unicodedata.normalize("NFC", s)
    s = DISALLOWED_RE.sub("", s)
    s = s.strip()

    return s

def get_first_tag_value(audio: FLAC, tag_name: str) -> Optional[str]:
    try:
        vals: Any = audio.get(tag_name)
    except Exception:
        return None

    if vals is None:
        return None

    if isinstance(vals, (list, tuple)):
        if not vals:
            return None
        vals = vals[0]

    if isinstance(vals, (bytes, bytearray)):
        try:
            return try_decode_bytes(bytes(vals))
        except Exception:
            return None

    try:
        return str(vals)
    except Exception:
        return None

def has_valid_music_files(folder: str) -> bool:
    for _, _, files in os.walk(folder):
        for f in files:
            if any(f.lower().endswith(ext.lower()) for ext in VALID_MUSIC_EXT):
                return True
    return False

def load_audio_file(filepath: str) -> Optional[Any]:
    _, ext = os.path.splitext(filepath)
    ext_lower = ext.lower()
    
    try:
        if ext_lower == '.flac':
            return FLAC(filepath)
        elif ext_lower == '.wav':
            return WAVE(filepath)
        elif ext_lower == '.mp3':
            return MP3(filepath)
        elif ext_lower == '.ogg':
            return OggVorbis(filepath)
        elif ext_lower == '.opus':
            return OggOpus(filepath)
        elif ext_lower in ('.aiff', '.aif'):
            return AIFF(filepath)
        elif ext_lower in ('.wma', '.asf'):
            return ASF(filepath)
        elif ext_lower in ('.mpc', '.mp+', '.mpp'):
            return Musepack(filepath)
        else:
            return None
    except Exception:
        return None

def rename_music(
    directory: str,
    dry_run: bool = False
) -> Tuple[list[str], Optional[str]]:

    logs: list[str] = []
    error: Optional[str] = None

    if not os.path.isdir(directory):
        error = f"Ordner nicht gefunden: {directory}"
        return logs, error

    if not has_valid_music_files(directory):
        error = f"Keine gültigen Musikdateien gefunden (Extensions: {VALID_MUSIC_EXT})"
        return logs, error

    renamed_count = 0
    skipped_count = 0

    for filename in os.listdir(directory):
        if not any(filename.lower().endswith(ext.lower()) for ext in VALID_MUSIC_EXT):
            continue

        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            continue

        audio = load_audio_file(filepath)
        if audio is None:
            # still skip silently (only OK/RENAME should be logged)
            skipped_count += 1
            continue

        raw_title = get_first_tag_value(audio, "title")
        raw_track = get_first_tag_value(audio, "tracknumber") or get_first_tag_value(audio, "track")
        raw_disk = get_first_tag_value(audio, "discnumber") or get_first_tag_value(audio, "disc")

        if not raw_title or not raw_track or not raw_disk:
            skipped_count += 1
            continue

        title = sanitize_tag_value(raw_title)
        track_s = sanitize_tag_value(raw_track)
        disk_s = sanitize_tag_value(raw_disk)

        disk_num = 0
        try:
            if raw_disk:
                m = re.search(r"\d", str(raw_disk))
                disk_num = int(m.group(0)) if m else 0
        except Exception:
            disk_num = 0

        m2 = re.match(r"\s*(\d+)", track_s)
        try:
            track_num = int(m2.group(1)) if m2 else 0
        except Exception:
            track_num = 0

        if not title:
            skipped_count += 1
            continue

        _, ext = os.path.splitext(filename)
        new_name_base = f"{disk_num:02d}-{track_num:02d} {title}{ext}"
        new_name_base = new_name_base.strip()
        new_path = os.path.join(directory, new_name_base)

        if os.path.abspath(filepath) == os.path.abspath(new_path):
            logs.append(f"[  OK  ]\t'{filename}' bereits korrekt")
            continue

        if os.path.exists(new_path):
            base, file_ext = os.path.splitext(new_name_base)
            i = 1
            while True:
                candidate = f"{base} ({i}){file_ext}"
                candidate_path = os.path.join(directory, candidate)
                if not os.path.exists(candidate_path):
                    new_path = candidate_path
                    break
                i += 1

        try:
            if not dry_run:
                os.rename(filepath, new_path)
                # Delete associated .txt or .lrc lyric files
                base_name = os.path.splitext(filepath)[0]
                for lyric_ext in ['.txt', '.lrc']:
                    old_lyric = base_name + lyric_ext
                    if os.path.exists(old_lyric):
                        try:
                            os.remove(old_lyric)
                        except Exception as e:
                            logs.append(f"\t[!] {lyric_ext} löschen fehlgeschlagen: {e}")
            logs.append(f"[RENAME]\t'{filename}' -> {os.path.basename(new_path)}")
            renamed_count += 1
        except Exception:
            skipped_count += 1

    return logs, None
