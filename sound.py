import pygame
import numpy as np
import random
import time

# Make sure mixer is initialised
if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

def _tone(freq, dur, vol):
    sr = 44100
    n = int(dur * sr)
    t = np.linspace(0, dur, n, False)
    w = np.sin(2 * np.pi * freq * t)
    fade = min(int(sr * 0.25), n // 2)
    w[:fade]  *= np.linspace(0, 1, fade)
    w[-fade:] *= np.linspace(1, 0, fade)
    w = (w * 32767 * vol).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((w, w)))

reef_notes = [_tone(f, 2.0, 0.13) for f in [523, 659, 784, 880, 698]]
deep_notes = [_tone(f, 3.0, 0.10) for f in [110, 130, 98, 87, 146]]
pulse_note = _tone(55, 0.5, 0.07)

_last_note  = 0.0
_last_pulse = 0.0

def update_sound(depth):
    global _last_note, _last_pulse
    now = time.time()

    # interval gets longer deeper (less frequent notes)
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
