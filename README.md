# SongSnap 🎵

**Real-time song recognition from your PC's system audio — using audio fingerprinting technology.**

SongSnap listens to whatever is playing on your computer (YouTube, Spotify, games, anime streams — anything) and automatically identifies the song, displaying the title and artist in a clean web UI in real time.

> **Live Demo →** [wjddusrb03.github.io/SongSnap](https://wjddusrb03.github.io/SongSnap) *(static preview, no backend required)*

---

## How It Works

SongSnap does **not** use lyrics or AI guessing. It uses audio fingerprinting — the same technique used by popular song recognition apps:

1. **Loopback audio capture** — Records your PC's output audio directly using Windows WASAPI loopback (the same stream that goes to your speakers/headphones), so no microphone is needed.
2. **Audio fingerprinting** — Every 5 seconds, a short audio sample is converted into a spectrogram. The loudest frequency peaks are extracted to form a unique "fingerprint" — like a sonic barcode.
3. **Song matching** — The fingerprint is sent to a recognition engine that compares it against a database of 70+ million songs and returns the match in under a second.
4. **Live web UI** — Results are pushed instantly to your browser via WebSocket, showing the cover art, title, and artist.

```
PC Audio Output
     │
     ▼
WASAPI Loopback (no mic needed)
     │
     ▼ every 5 seconds
Audio Fingerprint (frequency peaks)
     │
     ▼
Song Recognition Engine
     │
     ▼
WebSocket → Browser UI
```

---

## Features

- **No microphone required** — captures audio directly from the system output
- **Automatic detection** — continuously listens; no button to press
- **Duplicate filtering** — same song won't appear twice in a row
- **Silence detection** — skips processing when no audio is playing
- **Recognition history** — shows the last 50 songs recognized in the session
- **Album art** — fetches high-quality cover images automatically
- **One-click launch** — double-click `start.bat` and the browser opens automatically
- **In-browser stop button** — no need to touch the terminal to shut down

---

## Requirements

- **OS:** Windows 10 / 11 (WASAPI loopback is Windows-only)
- **Python:** 3.10 or newer
- **Network:** Internet connection (for song lookups)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/wjddusrb03/SongSnap.git
cd SongSnap
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

> If you get a `pyaudiowpatch` build error, install the Microsoft C++ Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## Usage

**Double-click `start.bat`**

That's it. The server starts and your browser opens automatically at `http://localhost:8000`.

To stop the server, click the **"Stop Server"** button on the web page.

---

## What It Can and Cannot Recognize

| Content | Result |
|---|---|
| Mainstream music (any language) | Works well |
| Anime OP/ED | Works well |
| Vocaloid (popular tracks) | Usually works |
| Instrumentals | Works (fingerprinting doesn't need lyrics) |
| Cover songs / fan arrangements | May not match (different audio fingerprint) |
| Doujin / self-released tracks | May not be in the database |
| NicoNico-only uploads | Unlikely to match |

If a song isn't recognized, SongSnap simply waits and tries the next 5-second window — it never crashes or freezes.

---

## Project Structure

```
SongSnap/
├── app.py            # FastAPI server + audio capture + song recognition
├── start.bat         # Windows launcher (starts server, opens browser)
├── requirements.txt  # Python dependencies
└── docs/
    └── index.html    # GitHub Pages static demo
```

---

## Tech Stack

| Component | Library |
|---|---|
| Web server | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Real-time push | WebSocket (built into FastAPI) |
| Audio capture | [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) (WASAPI loopback) |
| Song recognition | [ShazamAPI](https://github.com/Numenorean/ShazamAPI) (sync fork — the original `dotX12/ShazamAPI` was renamed to [ShazamIO](https://github.com/shazamio/ShazamIO) and the old PyPI package was removed; see [Maintenance Update](#-maintenance-update---2026-09-24)) |
| Audio processing | [NumPy](https://numpy.org/) |

---

## 🔧 Maintenance Update — 2026-09-24

**Status: fully working on Python 3.14 / Windows 11.** Recognition verified end-to-end (tested with a Voicemeeter virtual audio setup). This section documents everything that was fixed after a fresh clone stopped working.

### Symptom

After a fresh install, the server starts and the UI loads, but **no song is ever recognized**. On Python ≥ 3.13 the install itself (`pip install -r requirements.txt`) fails before that.

### Root causes — three stacked breakages

**1. `ShazamAPI==0.6.1` no longer exists anywhere.**
The upstream project [`dotX12/ShazamAPI`](https://github.com/shazamio/ShazamIO) was renamed to **shazamio/ShazamIO** and rewritten as an async library (new package name `shazamio`). The old `ShazamAPI` package was removed from PyPI — only a 2017-era `0.0.2` remains up there. The pinned `ShazamAPI==0.6.1` in `requirements.txt` is uninstallable for everyone.

**2. The drop-in replacement fork has a different API — and the failure was silent.**
The fix is the sync fork [Numenorean/ShazamAPI](https://github.com/Numenorean/ShazamAPI) (same recognition algorithm, modernized interface). But its entry point is:

```python
Shazam(lang="en", region="US", timezone="Europe/Paris").recognize_song(wav_bytes)
```

…not the old `Shazam(wav_bytes).recognizeSong()`. `app.py` kept calling the old API, so **every recognition attempt raised `AttributeError`**, which was swallowed by the bare `except` in `recognize_from_wav_bytes` — and because stdout is block-buffered when redirected, nothing showed in the console. The app looked healthy and just never recognized anything.

**3. Python 3.13 / 3.14 compatibility.**

| Dependency | Problem | Fix |
|---|---|---|
| `pyaudiowpatch==0.2.12.6` | no cp314 wheel on PyPI | bump to `0.2.12.8` |
| `numpy==2.2.4` | no cp314 wheel | resolves to `1.26.4` (builds from source, works) via the fork's constraint |
| `pydub` (ShazamAPI dependency) | imports stdlib `audioop`, **removed in Python 3.13** | add `audioop-lts` |
| plain `uvicorn` | no WebSocket support → UI loops on *"Unsupported upgrade request"* | add `websockets` |

### Changes, file by file

| File | Change |
|---|---|
| `app.py` | Recognition call migrated to the fork's API: `Shazam(lang="en", region="US", timezone="Europe/Paris")` + `recognize_song(wav_bytes)` (same response JSON — `matches` / `track` parsing unchanged) |
| `app.py` | Server binds `127.0.0.1` instead of `0.0.0.0` — localhost-only by default (revert if you want LAN access) |
| `start.bat` | Launches via the project venv (`.venv\Scripts\python.exe`) instead of the global interpreter, so the one-click launcher works after a venv install |
| `requirements.txt` | New working pins (see table above) |
| `diag_audio.py` | **New.** Diagnostic: measures RMS level on **every** WASAPI loopback device simultaneously (one thread per device) while music plays — tells you whether audio capture works and on which device |
| `diag_shazam.py` | **New.** Diagnostic: captures 8 s from the default output's loopback and sends it straight to the Shazam endpoint — isolates the recognition step from the app |

### Verified install procedure (Windows 11, Python 3.14)

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
start.bat        # server on http://localhost:8000, browser opens automatically
```

Server log after the fix (run with `python -u app.py` for unbuffered output):

```
Default output: Voicemeeter Input (VB-Audio Voicemeeter VAIO)
Loopback device: Voicemeeter Input (VB-Audio Voicemeeter VAIO) [Loopback]
Config: 2ch, 48000Hz
>> [23:14:01] DNCE - Cake By The Ocean
```

### Debugging notes (Voicemeeter & other virtual audio setups)

- The app follows the **default output device** and picks the loopback whose name starts with it. With Voicemeeter as default output, it listens to the **VAIO input loopback** — i.e. what applications play *into* Voicemeeter — verified working.
- If nothing is recognized, run `diag_audio.py` while music plays:
  - RMS ≥ 500 (the app's silence threshold) on your device → capture is fine, problem is downstream → run `diag_shazam.py`.
  - RMS ≈ 0 everywhere → your player is outputting to a different device than the system default.
- Known WASAPI quirk: reading from a loopback device that receives **no audio blocks indefinitely** — that's normal driver behavior, not a bug (which is also why `diag_audio.py` uses one thread per device).

---

## Disclaimer

This project uses [ShazamAPI](https://github.com/dotX12/ShazamAPI), an **unofficial, third-party, reverse-engineered** library not affiliated with or endorsed by Shazam Entertainment Ltd. or Apple Inc.

SongSnap is an independent open-source project for **personal, non-commercial use only**. All song metadata and recognition results are provided by third-party services.

---

## License

MIT License — free to use, modify, and share.
