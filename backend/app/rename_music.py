#!/usr/bin/env python3
"""
FLAC Music Renamer - API Integration Version
Benennt FLAC-Dateien basierend auf Metadaten um.
"""
import os
import re
import unicodedata
from mutagen.flac import FLAC
import filecmp
from typing import Optional, Tuple, List

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
    """Heuristik: wenn typische Mojibake-Sequenzen vorkommen, Re-encoding versuchen."""
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
    """Nimmt Tag-Value und gibt sauberen str zurück."""
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
    """Liest Tag und gibt ersten Wert als str oder None zurück."""
    try:
        vals = audio.get(tag_name)
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

def rename_music_files(
    folder: str,
    dry_run: bool = False
) -> Tuple[List[str], Optional[str]]:
    """
    Benennt FLAC-Dateien basierend auf Metadaten um.
    
    Args:
        folder: Pfad zum Album-Ordner
        dry_run: Wenn True, werden keine Änderungen vorgenommen
    
    Returns:
        Tuple[List[str], Optional[str]]: (logs, error_message)
    """
    logs = []
    
    if not os.path.isdir(folder):
        return logs, f"Ordner nicht gefunden: {folder}"
    
    try:
        all_files = os.listdir(folder)
        flac_files = [f for f in all_files if f.lower().endswith('.flac')]
        
        if not flac_files:
            return [f"Keine FLAC-Dateien in {folder} gefunden"], None
        
        logs.append(f"Gefundene FLAC-Dateien: {len(flac_files)}")
        
        renamed_count = 0
        skipped_count = 0
        
        for filename in flac_files:
            filepath = os.path.join(folder, filename)
            
            try:
                audio = FLAC(filepath)
            except Exception as e:
                logs.append(f"❌ Lesen fehlgeschlagen: {filename}: {e}")
                skipped_count += 1
                continue

            raw_title = get_first_tag_value(audio, "title")
            raw_track = get_first_tag_value(audio, "tracknumber") or get_first_tag_value(audio, "track")
            raw_disk = get_first_tag_value(audio, "discnumber") or get_first_tag_value(audio, "disc")

            if not raw_title or not raw_track or not raw_disk:
                logs.append(f"⚠️ Fehlende Metadaten: {filename}")
                skipped_count += 1
                continue

            title = sanitize_tag_value(raw_title)
            track_s = sanitize_tag_value(raw_track)
            disk_s = sanitize_tag_value(raw_disk)

            # Disknummer extrahieren
            disk_num = 0
            try:
                if raw_disk:
                    m = re.search(r"\d", str(raw_disk))
                    disk_num = int(m.group(0)) if m else 0
            except Exception:
                disk_num = 0

            # Tracknummer extrahieren
            m2 = re.match(r"\s*(\d+)", track_s)
            try:
                track_num = int(m2.group(1)) if m2 else 0
            except Exception:
                track_num = 0

            if not title:
                logs.append(f"⚠️ Titel leer nach Bereinigung: {filename}")
                skipped_count += 1
                continue

            new_name_base = f"{disk_num:02d}-{track_num:02d} {title}.flac"
            new_name_base = new_name_base.strip()
            new_path = os.path.join(folder, new_name_base)

            # Falls Zielname existiert, Suffix hinzufügen
            if os.path.exists(new_path) and new_path != filepath:
                base, ext = os.path.splitext(new_name_base)
                i = 1
                while True:
                    candidate = f"{base} ({i}){ext}"
                    candidate_path = os.path.join(folder, candidate)
                    if not os.path.exists(candidate_path):
                        new_path = candidate_path
                        new_name_base = candidate
                        break
                    i += 1

            # Umbenennen oder Dry-Run-Log
            if filepath == new_path:
                logs.append(f"⏭️ Bereits korrekt: {filename}")
                continue
            
            if dry_run:
                logs.append(f"[DRY-RUN] {filename} → {new_name_base}")
                renamed_count += 1
            else:
                try:
                    os.rename(filepath, new_path)
                    logs.append(f"✅ {filename} → {new_name_base}")
                    renamed_count += 1
                except Exception as e:
                    logs.append(f"❌ Fehler beim Umbenennen {filename}: {e}")
                    skipped_count += 1

        # Cleanup Windows-Suffixe (nur wenn nicht dry-run)
        if not dry_run:
            cleanup_logs = cleanup_windows_suffixes(folder)
            logs.extend(cleanup_logs)

        # Zusammenfassung
        logs.append("")
        logs.append(f"📊 Zusammenfassung: {renamed_count} umbenannt, {skipped_count} übersprungen")
        
        return logs, None
        
    except Exception as e:
        return logs, f"Fehler beim Verarbeiten: {str(e)}"

def cleanup_windows_suffixes(folder: str) -> List[str]:
    """Entfernt unnötige Windows '(n)' Suffixe."""
    logs = []
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
                os.rename(suffixed_path, candidate_path)
                logs.append(f"🧹 Suffix entfernt: {entry} → {candidate_name}")
            else:
                try:
                    same = filecmp.cmp(suffixed_path, candidate_path, shallow=False)
                except Exception:
                    same = False

                if same:
                    os.remove(suffixed_path)
                    logs.append(f"🗑️ Duplikat entfernt: {entry}")
        except Exception as e:
            logs.append(f"⚠️ Cleanup-Fehler für {entry}: {e}")
    
    return logs
