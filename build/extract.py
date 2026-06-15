#!/usr/bin/env python3
"""
Extract the "Spanish 7000 Intermediate/Advanced Sentences" Anki deck (.apkg)
into the Spanish SRS app's cards.json + audio/ folder.

Source layout (an unzipped .apkg):
  <APKG_DIR>/collection.anki2   - SQLite DB with the notes
  <APKG_DIR>/media              - JSON map {"<num>": "<filename.mp3>", ...}
  <APKG_DIR>/<num>              - the actual media files (numbered)

Note fields: audio, sentence, english translation, frequency ranks, eng_audio
(the last two are empty throughout this deck).

Output:
  cards.json        - [{ id, es, en }], ordered by the deck's audio sequence
  audio/s_<id>.mp3  - sentence audio
"""
import sqlite3, json, os, re, html, shutil, sys

APKG_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/es_inspect"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_OUT = os.path.join(ROOT, "audio")

F_AUDIO, F_SENT, F_ENG = 0, 1, 2


def clean(s):
    if not s:
        return ""
    s = re.sub(r"(?i)<\s*(br|/p|/div)\s*/?>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.lstrip("•·*-").strip()           # strip the leading bullet
    s = s.replace(" ", " ").replace("​", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def sound_ref(field):
    m = re.search(r"\[sound:([^\]]+)\]", field or "")
    return m.group(1) if m else None


def seq_num(filename):
    m = re.search(r"(\d+)\.mp3$", filename or "")
    return int(m.group(1)) if m else 10**9


def main():
    db = os.path.join(APKG_DIR, "collection.anki2")
    if os.path.exists(os.path.join(APKG_DIR, "collection.anki21")):
        db = os.path.join(APKG_DIR, "collection.anki21")
    media = json.load(open(os.path.join(APKG_DIR, "media")))
    name_to_num = {v: k for k, v in media.items()}

    con = sqlite3.connect(db)
    rows = con.execute("SELECT flds FROM notes").fetchall()
    con.close()

    notes = []
    for (flds,) in rows:
        f = flds.split("\x1f")
        if len(f) < 3:
            continue
        es = clean(f[F_SENT])
        en = clean(f[F_ENG])
        if not es or not en:
            continue
        ref = sound_ref(f[F_AUDIO])
        notes.append({"es": es, "en": en, "audio": ref, "seq": seq_num(ref or "")})

    notes.sort(key=lambda n: n["seq"])

    os.makedirs(AUDIO_OUT, exist_ok=True)
    cards, copied, missing = [], 0, []
    for new_id, n in enumerate(notes):
        cards.append({"id": new_id, "es": n["es"], "en": n["en"]})
        ref = n["audio"]
        if not ref:
            missing.append("(no ref)")
            continue
        num = name_to_num.get(ref)
        src = os.path.join(APKG_DIR, num) if num is not None else None
        if src and os.path.exists(src):
            shutil.copyfile(src, os.path.join(AUDIO_OUT, f"s_{new_id}.mp3"))
            copied += 1
        else:
            missing.append(ref)

    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as fp:
        json.dump(cards, fp, ensure_ascii=False, separators=(",", ":"))

    print(f"cards: {len(cards)}")
    print(f"audio copied: {copied}")
    print(f"missing media: {len(missing)}", missing[:5])
    size = os.path.getsize(os.path.join(ROOT, "cards.json"))
    print(f"cards.json: {size//1024} KB")


if __name__ == "__main__":
    main()
