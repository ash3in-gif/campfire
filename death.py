import pygame
import sys
import numpy as np
import math
import random
import io
import wave
import struct

def _make_sound(freq, duration, volume):
    import tempfile, os
    sr = 44100
    n = int(duration * sr)
    t = np.linspace(0, duration, n, False)
    wave_data = (np.sin(2 * np.pi * freq * t) * 0.5 +
                 np.sin(2 * np.pi * freq * 1.5 * t) * 0.3 +
                 np.sin(2 * np.pi * freq * 0.5 * t) * 0.2)
    wave_data *= 0.7 + 0.3 * np.sin(2 * np.pi * 5 * t)
    fade = min(int(sr * 0.2), n // 2)
    wave_data[:fade]  *= np.linspace(0, 1, fade)
    wave_data[-fade:] *= np.linspace(1, 0, fade)
    wave_data = np.clip(wave_data * 32767 * volume, -32767, 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()
    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(wave_data.tobytes())
    snd = pygame.mixer.Sound(tmp_path)
    os.unlink(tmp_path)
    return snd

def run_death_screen(screen, clock):
    font_big   = pygame.font.SysFont(None, 80)
    font_med   = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)

    pygame.mixer.stop()

    notes = [
        _make_sound(110, 2.0, 0.5),
        _make_sound(98,  2.5, 0.4),
        _make_sound(82,  3.0, 0.45),
        _make_sound(73,  2.0, 0.4),
    ]

    blood = []
    for _ in range(60):
        angle = random.uniform(0, 6.28)
        spd   = random.uniform(1, 5)
        blood.append({
            'x': 400.0, 'y': 300.0,
            'vx': spd * math.cos(angle),
            'vy': spd * math.sin(angle),
            'r': random.randint(8, 18),
            'alpha': 255.0,
        })

    t             = 0
    note_idx      = 0
    last_note     = -999
    note_interval = 90

    notes[0].play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pygame.mixer.stop()
                    return

        t += 1

        if t - last_note > note_interval:
            note_idx = (note_idx + 1) % len(notes)
            notes[note_idx].play()
            last_note     = t
            note_interval = 80 + note_idx * 20

        bg_r = min(40, t // 3)
        screen.fill((bg_r, 0, 0))

        for drop in blood:
            drop['x']    += drop['vx']
            drop['y']    += drop['vy']
            drop['vy']   += 0.1
            drop['vx']   *= 0.98
            drop['alpha'] = max(80, drop['alpha'] - 0.3)
            r = max(3, drop['r'] - t // 120)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 0, 0, int(drop['alpha'])), (r, r), r)
            screen.blit(s, (int(drop['x']) - r, int(drop['y']) - r))

        fx, fy = 400, 300
        pygame.draw.ellipse(screen, (180, 120, 20), (fx-30, fy-10, 60, 20))
        pygame.draw.polygon(screen, (160, 100, 10), [
            (fx-30, fy+5), (fx-48, fy+18), (fx-48, fy-4)])
        pygame.draw.polygon(screen, (160, 100, 10), [
            (fx-10, fy-10), (fx+5, fy-10), (fx, fy-22)])
        ex, ey = fx+18, fy-3
        pygame.draw.line(screen, (30, 30, 30), (ex-4, ey-4), (ex+4, ey+4), 2)
        pygame.draw.line(screen, (30, 30, 30), (ex+4, ey-4), (ex-4, ey+4), 2)

        wobble = int(math.sin(t * 0.05) * 2)
        kx, ky = fx+5, fy-50+wobble
        pygame.draw.rect(screen, (80, 50, 20),   (kx-5, ky-20, 10, 20))
        pygame.draw.rect(screen, (60, 35, 10),   (kx-7, ky-22, 14, 5))
        pygame.draw.polygon(screen, (200, 200, 210), [
            (kx-3, ky), (kx+3, ky), (kx+1, ky+40), (kx-1, ky+40)])
        pygame.draw.line(screen, (240, 240, 255), (kx+1, ky+2), (kx+1, ky+35), 1)
        pygame.draw.polygon(screen, (160, 0, 0), [
            (kx-3, ky+20), (kx+3, ky+20), (kx+2, ky+38), (kx-2, ky+38)])

        alpha = min(255, t * 4)
        ts = font_big.render("YOU DIED", True, (220, 30, 30))
        ts.set_alpha(alpha)
        screen.blit(ts, ts.get_rect(center=(400, 160)))

        sub = font_med.render("The fisherman was waiting.", True, (180, 100, 100))
        sub.set_alpha(min(255, max(0, (t-30)*4)))
        screen.blit(sub, sub.get_rect(center=(400, 460)))

        if t > 80 and (t // 40) % 2 == 0:
            prompt = font_small.render("Press SPACE to try again", True, (140, 60, 60))
            screen.blit(prompt, prompt.get_rect(center=(400, 530)))

        pygame.display.flip()
        clock.tick(60)