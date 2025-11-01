#!/usr/bin/env python3
import os
import re
import sys
import unicodedata
from mutagen.flac import FLAC
import filecmp
from typing import Optional, Any

DISALLOWED_RE = re.compile(r'[\x00-\x1F<>:"/\\|?*]')  # entferne komplett (nicht ersetzen)

def try_decode_bytes(b: bytes) -> str:
    """Versuche mehrere Decodings in Reihenfolge, return str."""
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    # letzte Notlösung: decode lossily
    return b.decode("utf-8", errors="replace")

def fix_mojibake_if_needed(s: str) -> str:
    """
    Heuristik: wenn typische Mojibake-Sequenzen vorkommen (z.B. 'Ã' gefolgt von anderen Zeichen),
    versuche Re-encoding über cp1252->utf-8 oder latin-1->utf-8.
    """
    # Only attempt repair when there are signs of mojibake or replacement chars.
    # If the string already looks fine (no suspicious sequences), leave it alone
    # to avoid turning correct Unicode into mojibake.
    suspicious = any(x in s for x in ("�", "Ã", "Â"))
    if not suspicious:
        return s

    # We'll try several sensible re-encodings and pick the candidate with the
    # fewest replacement characters ("�"). Prefer only candidates that reduce
    # the number of replacement characters — do NOT accept changed strings
    # that keep the same count (that caused regressions earlier).
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
            # Only accept candidates that reduce replacement char count
            if cand_repl < best_repl:
                best = cand
                best_repl = cand_repl
        except Exception:
            # ignore and continue with other candidates
            pass

    return best

def sanitize_tag_value(value) -> str:
    """
    Nimmt eine Tag-Value (bytes oder str oder anderes) und gibt sauberen str zurück.
    Entfernt unerwünschte Zeichen komplett.
    """
    if value is None:
        return ""

    # mutagen liefert meistens str, manchmal aber bytes in Sonderfällen.
    if isinstance(value, bytes):
        s = try_decode_bytes(value)
    else:
        s = str(value)

    # Falls möglicherweise falsch decodiert (Mojibake), versuchen zu korrigieren
    s = fix_mojibake_if_needed(s)

    # Unicode normalisieren (NFC)
    s = unicodedata.normalize("NFC", s)

    # Entferne Steuerzeichen & die in DISALLOWED_RE (komplett entfernen, nicht ersetzen)
    s = DISALLOWED_RE.sub("", s)

    # Strips am Anfang/Ende
    s = s.strip()

    return s

def get_first_tag_value(audio: FLAC, tag_name: str) -> Optional[str]:
    """Versucht das Tag zu lesen; gibt ersten Wert als sauberen str oder None.

    Unwraps lists/tuples, decodes bytes and returns a str or None so the return
    type is always Optional[str]. Fehlerhafte Werte werden zu None.
    """
    try:
        vals: Any = audio.get(tag_name)
    except Exception:
        return None

    if vals is None:
        return None

    # If it's a list/tuple, take the first element (if present)
    if isinstance(vals, (list, tuple)):
        if not vals:
            return None
        vals = vals[0]

    # If bytes, try to decode robustly
    if isinstance(vals, (bytes, bytearray)):
        try:
            return try_decode_bytes(bytes(vals))
        except Exception:
            return None

    # Finally coerce other types to str
    try:
        return str(vals)
    except Exception:
        return None

def rename_flac_files(folder: str, debug: bool = False, dry_run: bool = False):
    """
    Benennt FLAC-Dateien basierend auf Metadaten um.
    
    Args:
        folder: Pfad zum Album-Ordner
        debug: Aktiviert erweiterte Debug-Ausgaben
        dry_run: Wenn True, werden keine Änderungen vorgenommen
    
    Returns:
        Tuple[List[str], Optional[str]]: (logs, error)
    """
    logs = []
    
    # debug: pre-scan to show how many .flac files exist
    if debug:
        all_files = os.listdir(folder)
        flac_files = [f for f in all_files if f.lower().endswith('.flac')]
        logs.append(f"[DEBUG] Found {len(flac_files)} .flac files in {folder}")
        if flac_files:
            sample = flac_files[:10]
            logs.append(f"[DEBUG] Sample files: {sample}")

    for filename in os.listdir(folder):
        if not filename.lower().endswith(".flac"):
            continue

        filepath = os.path.join(folder, filename)
        try:
            audio = FLAC(filepath)
        except Exception as e:
            logs.append(f"[ERROR] Lesen fehlgeschlagen: {filename}: {e}")
            continue

        if debug:
            logs.append(f"[DEBUG] Found file: {filename}")

        raw_title = get_first_tag_value(audio, "title")
        raw_track = get_first_tag_value(audio, "tracknumber") or get_first_tag_value(audio, "track")
        raw_disk = get_first_tag_value(audio, "discnumber") or get_first_tag_value(audio, "disc")

        if debug:
            print(f"[DEBUG] Raw tags for {filename}: title={raw_title!r}, track={raw_track!r}, disc={raw_disk!r}")

        if not raw_title or not raw_track or not raw_disk:
            print(f"[SKIP] Fehlende Metadaten: {filename}")
            continue

        title = sanitize_tag_value(raw_title)
        track_s = sanitize_tag_value(raw_track)
        disk_s = sanitize_tag_value(raw_disk)

        if debug:
            print(f"[DEBUG] Sanitized for {filename}: title={title!r}, track={track_s!r}, disc={disk_s!r}")

        # Disknummer: nimm die erste Ziffer aus dem Roh-Tag (z.B. "1/2" -> 1).
        # Hinweis: in sanitize werden Zeichen wie '/' entfernt, daher müssen
        # wir raw_disk verwenden, um die ursprüngliche Trennung zu erkennen.
        disk_num = 0
        try:
            if raw_disk:
                m = re.search(r"\d", str(raw_disk))
                disk_num = int(m.group(0)) if m else 0
        except Exception:
            disk_num = 0

        # Tracknummer: nur die erste Zahl extrahieren
        m2 = re.match(r"\s*(\d+)", track_s)
        try:
            track_num = int(m2.group(1)) if m2 else 0
        except Exception:
            track_num = 0

        # Wenn Titel leer nach Bereinigung -> skip
        if not title:
            print(f"[SKIP] Titel leer nach Bereinigung: {filename}")
            continue

        new_name_base = f"{disk_num:02d}-{track_num:02d} {title}.flac"
        # Sorgfältig: entferne führende/trailing Whitespace nochmal
        new_name_base = new_name_base.strip()

        new_path = os.path.join(folder, new_name_base)

        # Falls Zielname bereits existiert, füge (1),(2),... an
        if os.path.exists(new_path):
            base, ext = os.path.splitext(new_name_base)
            i = 1
            while True:
                candidate = f"{base} ({i}){ext}"
                candidate_path = os.path.join(folder, candidate)
                if not os.path.exists(candidate_path):
                    new_path = candidate_path
                    break
                i += 1

        try:
            if debug:
                # show repr and codepoints for non-ascii chars to debug encoding issues
                print(f"[DEBUG] Renaming to (repr): {repr(new_name_base)}")
                cps = [f"U+{ord(c):04X}" for c in new_name_base if ord(c) > 127]
                if cps:
                    print(f"[DEBUG] Non-ASCII codepoints in new name: {cps}")

            os.rename(filepath, new_path)

            if debug:
                # show what the filesystem reports after rename
                try:
                    actual = next((f for f in os.listdir(folder) if os.path.basename(new_path) in f or f == os.path.basename(new_path)), None)
                    print(f"[DEBUG] After rename, filesystem shows: {repr(actual)}")
                except Exception:
                    pass

            print(f"[OK] {filename} -> {os.path.basename(new_path)}")
        except Exception as e:
            print(f"[ERROR] Umbenennen {filename} -> {os.path.basename(new_path)} fehlgeschlagen: {e}")

def cleanup_windows_suffixes(folder: str, debug: bool = False):
    """Remove Windows '(n)' suffixes when unnecessary.

    For files named like 'Name (1).ext' this function will try to rename them to
    'Name.ext' if that name does not exist. If 'Name.ext' exists and the two
    files are identical (by content), the suffixed file is removed. If the
    target exists but differs, the suffixed file is left in place.
    """
    suffix_re = re.compile(r'^(?P<base>.+) \((?P<num>\d+)\)(?P<ext>\.[^.]+)$')

    for entry in os.listdir(folder):
        m = suffix_re.match(entry)
        if not m:
            continue

        base = m.group('base')
        ext = m.group('ext')
        suffixed_path = os.path.join(folder, entry)
        candidate_name = f"{base}{ext}"
        candidate_path = os.path.join(folder, candidate_name)

        try:
            if not os.path.exists(candidate_path):
                # safe to rename
                if debug:
                    print(f"[CLEAN] Renaming {entry} -> {candidate_name}")
                os.rename(suffixed_path, candidate_path)
            else:
                # candidate exists: if identical content, remove the duplicate
                try:
                    same = filecmp.cmp(suffixed_path, candidate_path, shallow=False)
                except Exception:
                    same = False

                if same:
                    if debug:
                        print(f"[DUP] {entry} is duplicate of {candidate_name}; removing {entry}")
                    os.remove(suffixed_path)
                else:
                    if debug:
                        print(f"[SKIP] {entry} differs from {candidate_name}; leaving as-is")
        except Exception as e:
            print(f"[ERROR] Cleanup failed for {entry}: {e}")
def main():
    # Folder via CLI-Argument optional übergeben, ansonsten Standardpfad
    folder = r"D:\Audio\Bravo Hits 81"
    debug = False
    if len(sys.argv) > 1:
        # allow: script.py [folder] [--debug]
        # parse simple flags
        for arg in sys.argv[1:]:
            if arg in ("--debug", "-d"):
                debug = True
            else:
                folder = arg

    if not os.path.isdir(folder):
        print(f"[ERROR] Ordner nicht gefunden: {folder}")
        return

    # run with debug flag if requested
    if debug:
        print(f"[DEBUG] Running in debug mode on folder: {folder}")

    rename_flac_files(folder, debug=debug)
    # After renaming based on tags, remove Windows-added " (n)" suffixes when safe
    try:
        cleanup_windows_suffixes(folder, debug=debug)
    except Exception as e:
        print(f"[ERROR] Cleanup pass failed: {e}")

if __name__ == "__main__":
    main()
