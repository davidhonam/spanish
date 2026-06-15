# Intermediate Spanish SRS

A spaced-repetition study app for **7000 intermediate/advanced Spanish sentences**, each with
native audio. English → Spanish production flashcards. Self-contained single page — no build
step to *run*, no server, no account.

Part of a family of SRS apps (see also [Mandarin](../mandarin) and [French](../french)).
Sentences, translations, and audio extracted from the *"Spanish 7000
Intermediate/Advanced Sentences w/ Audio"* Anki deck.

## Features

- **Spaced repetition (SM-2 variant)** — Anki-style Again / Hard / Good / Easy grading,
  daily new-card cap, day streaks.
- **Native audio** — a recording for every sentence, played automatically when a card
  appears (toggle in Settings) and replayable with `▶` / the `R` key, at adjustable speed.
  Falls back to the browser's Spanish voice if a clip is missing.
- **Browse / Search / Cram** — search across Spanish and English; filter by status; drill a
  filtered set without affecting scheduling.
- **Stats** — retention, reviews/day, due forecast, collection maturity, leeches.
- **Mobile-first PWA** — responsive, installable to the home screen, full offline support
  (app shell + audio cached via service worker).
- **Persistent progress** — auto-saved to the browser; export/import as JSON.

## Card format

By default each card tests **production**: the English sentence is shown; you recall the
Spanish, then reveal it — the Spanish sentence is displayed and read aloud (autoplay,
toggleable). A **Production mode** toggle in Settings flips this to **recognition** (see and
hear the Spanish, recall the English). This is a sentence deck — there is no per-word
vocabulary, part of speech, or definition; the sentence itself is the unit of study.

## Run it

Serve locally for full features (service worker / offline audio):

```bash
cd spanish
python3 -m http.server     # then open http://localhost:8000
```

The card data is embedded inline, so `index.html` also works from `file://`, though the
service worker (offline install) only activates over `http(s)`.

## Data & audio

- **7627 sentences**, ordered by the deck's original audio sequence.
- **`cards.json`** — one entry per sentence: `{ id, es, en }`.
- **`audio/`** — `s_<id>.mp3` per sentence, ~122 MB total, reused directly from the source
  deck.

## Rebuilding from the Anki deck

The data and audio are generated from the `.apkg` (an Anki package = a zip of a SQLite DB
plus numbered media files):

```bash
# 1. unzip the .apkg somewhere, e.g. /tmp/es
unzip "Spanish_7000_IntermediateAdvanced_Sentences_w_Audio.apkg" -d /tmp/es

# 2. extract cards.json + copy/rename audio into audio/
python3 build/extract.py /tmp/es

# 3. embed cards.json into index.html
python3 build/make_index.py
```

`build/extract.py` reads the notes, strips the leading bullet and normalizes whitespace,
orders sentences by the audio filename sequence, and copies each `[sound:…]` clip to
`audio/s_<id>.mp3`. The source deck's empty `frequency ranks` / `eng_audio` fields are
ignored.

When you change the app, edit **`index.template.html`** and re-run `make_index.py` — do not
edit `index.html` by hand (it's generated and contains the embedded data).
