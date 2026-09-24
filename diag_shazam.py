"""Diagnostic: capture 8 s du loopback Voicemeeter -> requete Shazam directe."""
import io
import wave
import pyaudiowpatch as pyaudio
from ShazamAPI import Shazam

p = pyaudio.PyAudio()
wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
default_out = p.get_device_info_by_index(wasapi["defaultOutputDevice"])

loopback = None
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("isLoopbackDevice") and dev["name"].startswith(default_out["name"]):
        loopback = dev
        break

print(f"Device: {loopback['name']}", flush=True)
ch, rate = 2, int(loopback["defaultSampleRate"])
s = p.open(format=pyaudio.paInt16, channels=ch, rate=rate, input=True,
           input_device_index=loopback["index"], frames_per_buffer=1024)

print("Capture 8 s...", flush=True)
frames = []
while sum(len(f) for f in frames) < ch * 2 * rate * 8:
    frames.append(s.read(1024, exception_on_overflow=False))
s.stop_stream(); s.close(); p.terminate()

wav_buf = io.BytesIO()
with wave.open(wav_buf, "wb") as wf:
    wf.setnchannels(ch)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
wav_bytes = wav_buf.getvalue()
print(f"Echantillon: {len(wav_bytes)} octets WAV", flush=True)

print("Requete Shazam (API fork)...", flush=True)
try:
    shazam = Shazam(lang="en", region="US", timezone="Europe/Paris")
    for offset, result in shazam.recognize_song(wav_bytes):
        print(f"offset={offset}", flush=True)
        print(f"matches: {len(result.get('matches', []))}", flush=True)
        if result.get("matches"):
            track = result["track"]
            print(f"==> {track.get('subtitle')} - {track.get('title')}", flush=True)
        else:
            print(f"cles: {list(result.keys())}", flush=True)
            print(str(result)[:400], flush=True)
        break
except Exception as e:
    print(f"ERREUR Shazam: {type(e).__name__}: {e}", flush=True)
