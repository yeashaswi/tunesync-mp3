import re

def clean_title(title: str) -> str:
    """
    Cleans up YouTube / YouTube Music video titles into clean, concise song titles
    ready for MP3 players and file systems.
    """
    if not title:
        return "Unknown Track"

    t = title

    # 1. Remove leading track numbering (e.g. '001 - ', '01. ', '1 - ')
    t = re.sub(r'^\d+[\s\.\-_]+', '', t)

    # 2. Normalize full-width and exotic punctuation
    t = (t.replace('＂', "'")
          .replace('“', "'")
          .replace('”', "'")
          .replace('`', "'")
          .replace('’', "'")
          .replace('：', ' - ')
          .replace('｜', ' - ')
          .replace('|', ' - '))

    # 3. Strip common YouTube promotional clutter and bracketed video tags
    junk_patterns = [
        r'\[\s*(?:official\s*(?:music\s*)?video|official\s*audio|visualizer|lyric\s*video|lyrics?|audio|hd|4k|1080p|remastered|hq|video|og)\s*\]',
        r'\(\s*(?:official\s*(?:music\s*)?video|official\s*audio|visualizer|lyric\s*video|lyrics?|audio|hd|4k|1080p|remastered|hq|full\s*audio|video\s*song)\s*\)',
        r'(?i)\b(?:official\s*(?:music\s*)?video|official\s*audio|visualizer|lyric\s*video)\b',
        r'Prod\.\s*@?[\w\d_]+',
    ]
    for p in junk_patterns:
        t = re.sub(p, '', t, flags=re.IGNORECASE)

    # 4. Filter repetitive promotional trailing parts if split by dashes
    parts = [p.strip() for p in t.split(' - ') if p.strip()]
    if len(parts) > 2:
        # Check if latter parts are studio labels / promo
        filtered = []
        for i, part in enumerate(parts):
            if i > 0 and re.search(r'(?i)\b(t-series|sony\s*music|zee\s*music|aditya\s*music|movie\s*makers?|official|extended|full\s*version)\b', part):
                continue
            filtered.append(part)
        t = ' - '.join(filtered) if filtered else parts[0]
    elif len(parts) == 2:
        # e.g., "The Rare Occasions - Notion" -> keep as is
        t = ' - '.join(parts)
    elif parts:
        t = parts[0]

    # 5. Sanitize illegal filesystem characters for FAT32 / exFAT / Windows / macOS / Linux
    t = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '', t)

    # 6. Normalize multiple spaces and hyphens
    t = re.sub(r'\s*-\s*-\s*', ' - ', t)
    t = re.sub(r'\s+', ' ', t).strip(' -._')

    return t or "Track"

def sanitize_filename(name: str, max_length: int = 120) -> str:
    """
    Ensures filename is strictly safe for FAT32, exFAT, and all mobile/desktop filesystems.
    """
    clean = clean_title(name)
    # Truncate length if unusually long
    if len(clean) > max_length:
        clean = clean[:max_length].rstrip(' -._')
    return clean
