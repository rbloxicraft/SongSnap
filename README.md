# ShazamPC 🎵

**Real-time song recognition from your PC's system audio — powered by Shazam fingerprinting.**

ShazamPC listens to whatever is playing on your computer (YouTube, Spotify, games, anime streams — anything) and automatically identifies the song, displaying the title and artist in a clean web UI in real time.

> **Live Demo →** [wjddusrb03.github.io/ShazamPC](https://wjddusrb03.github.io/ShazamPC) *(static preview, no backend required)*

---

## How It Works

ShazamPC does **not** use lyrics or AI guessing. It uses the same technique as the Shazam app:

1. **Loopback audio capture** — Records your PC's output audio directly using Windows WASAPI loopback (the same stream that goes to your speakers/headphones), so no microphone is needed.
2. **Audio fingerprinting** — Every 5 seconds, a short audio sample is converted into a spectrogram. The loudest frequency peaks are extracted to form a unique "fingerprint" — like a sonic barcode.
3. **Shazam matching** — The fingerprint is sent to Shazam's recognition engine, which compares it against a database of 70+ million songs and returns the match in under a second.
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
Shazam Recognition Engine
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
- **Album art** — fetches high-quality cover images from Shazam
- **One-click launch** — double-click `start.bat` and the browser opens automatically
- **In-browser stop button** — no need to touch the terminal to shut down

---

## Requirements

- **OS:** Windows 10 / 11 (WASAPI loopback is Windows-only)
- **Python:** 3.10 or newer
- **Network:** Internet connection (for Shazam lookups)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ShazamPC.git
cd ShazamPC
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
| Doujin / self-released tracks | May not be in Shazam's database |
| NicoNico-only uploads | Unlikely to match |

If a song isn't recognized, ShazamPC simply waits and tries the next 5-second window — it never crashes or freezes.

---

## Project Structure

```
ShazamPC/
├── app.py            # FastAPI server + audio capture + Shazam recognition
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
| Song recognition | [ShazamAPI](https://github.com/dotX12/ShazamAPI) (unofficial) |
| Audio processing | [NumPy](https://numpy.org/) |

---

## Disclaimer

ShazamAPI is an **unofficial, reverse-engineered** interface to Shazam's recognition service. This project is for personal, non-commercial use only. All song metadata and recognition results are provided by Shazam.

---

## License

MIT License — free to use, modify, and share.
