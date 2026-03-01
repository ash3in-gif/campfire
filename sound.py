import pygame
import numpy as np
import random
import time
import io
import wave

def _make_sound(freq, duration, volume):
    sr = 44100
    n = int(duration * sr)
    t = np.linspace(0, duration, n, False)
    w = np.sin(2 * np.pi * freq * t)
    fade = min(int(sr * 0.25), n // 2)
    w[:fade]  *= np.linspace(0, 1, fade)
    w[-fade:] *= np.linspace(1, 0, fade)
    w = np.clip(w * 32767 * volume, -32767, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(w.tobytes())
    buf.seek(0)
    return pygame.mixer.Sound(buf)

reef_notes = [_make_sound(f, 2.0, 0.13) for f in [523, 659, 784, 880, 698]]
deep_notes = [_make_sound(f, 3.0, 0.10) for f in [110, 130, 98, 87, 146]]
pulse_note = _make_sound(55, 0.5, 0.07)

_last_note  = 0.0
_last_pulse = 0.0

def update_sound(depth):
    global _last_note, _last_pulse
    now = time.time()
    interval = 1.5 + depth * 5.0
    if now - _last_note > interval:
        if depth < 0.4:
            n = random.choice(reef_notes)
            n.set_volume(max(0.01, 0.13 * (1.0 - depth / 0.4)))
        else:
            n = random.choice(deep_notes)
            n.set_volume(max(0.01, 0.08 * min(1.0, depth)))
        n.play()
        _last_note = now
    if depth > 0.65:
        pulse_interval = max(0.4, 2.5 - depth * 2.0)
        if now - _last_pulse > pulse_interval:
            pulse_note.set_volume(min(0.15, depth * 0.12))
            pulse_note.play()
            _last_pulse = now