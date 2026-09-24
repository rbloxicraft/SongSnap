"""Diagnostic v2: un thread par device loopback, mesure RMS 10 s."""
import threading
import time
import numpy as np
import pyaudiowpatch as pyaudio

p = pyaudio.PyAudio()
wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
default_out = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
print(f"Sortie par defaut: {default_out['name']}", flush=True)

results = {}
lock = threading.Lock()

def monitor(dev):
    name = dev["name"]
    res = {"rms": None, "bytes": 0, "err": None}
    with lock:
        results[name] = res
    try:
        s = p.open(
            format=pyaudio.paInt16, channels=2, rate=int(dev["defaultSampleRate"]),
            input=True, input_device_index=dev["index"], frames_per_buffer=1024,
        )
    except Exception as e:
        res["err"] = str(e)
        return
    frames = []
    end = time.time() + 10
    while time.time() < end:
        try:
            frames.append(s.read(1024, exception_on_overflow=False))
        except Exception as e:
            res["err"] = str(e)
            break
    s.stop_stream(); s.close()
    raw = b"".join(frames)
    res["bytes"] = len(raw)
    if raw:
        samples = np.frombuffer(raw, dtype=np.int16)
        res["rms"] = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))

threads = []
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("isLoopbackDevice"):
        t = threading.Thread(target=monitor, args=(dev,), daemon=True)
        t.start()
        threads.append(t)
        print(f"  Thread lance: {dev['name']}", flush=True)

print("Mesure 10 s — joue ta musique maintenant !", flush=True)
for t in threads:
    t.join(timeout=15)

print(flush=True)
print("=== Resultats (seuil silence app = 500) ===", flush=True)
for name, res in results.items():
    if res["err"]:
        print(f"  {name}: ERREUR {res['err']}", flush=True)
    elif res["rms"] is None:
        print(f"  {name}: bloque/aucune donnee ({res['bytes']} octets)", flush=True)
    else:
        verdict = "AUDIBLE" if res["rms"] >= 500 else "silence"
        print(f"  {name}: RMS={res['rms']:.0f} ({res['bytes']} octets) -> {verdict}", flush=True)

p.terminate()
