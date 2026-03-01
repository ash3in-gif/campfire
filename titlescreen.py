import pygame
import sys
import math
import numpy as np
import random

# ── Music generation ──────────────────────────────────────────────────────────

def make_menu_note(freq, duration, volume=0.12, wave_type="sine"):
    import tempfile, os, wave as wavemod
    sr = 44100
    n = int(duration * sr)
    t = np.linspace(0, duration, n, False)
    if wave_type == "sine":
        w = np.sin(2 * np.pi * freq * t)
    else:
        w = (np.sin(2 * np.pi * freq * t) * 0.6 +
             np.sin(2 * np.pi * freq * 2 * t) * 0.3 +
             np.sin(2 * np.pi * freq * 0.5 * t) * 0.1)
    fade = min(int(sr * 0.25), n // 2)
    w[:fade]  *= np.linspace(0, 1, fade)
    w[-fade:] *= np.linspace(1, 0, fade)
    w = np.clip(w * 32767 * volume, -32767, 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()
    with wavemod.open(tmp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(w.tobytes())
    snd = pygame.mixer.Sound(tmp_path)
    os.unlink(tmp_path)
    return snd

# Gentle lullaby-style melody for the menu
MELODY = [
    (523, 1.2), (659, 0.8), (784, 1.4), (659, 0.8),
    (523, 1.0), (440, 1.2), (392, 1.6), (440, 0.8),
    (523, 1.2), (587, 0.8), (659, 1.2), (784, 1.6),
    (659, 0.8), (587, 0.8), (523, 2.0),
]
BASS = [
    (130, 2.0), (164, 2.0), (196, 2.0), (174, 2.0),
    (130, 2.0), (110, 2.0), (98,  2.0), (110, 2.0),
]

melody_notes = None
bass_notes   = None

def _init_music():
    global melody_notes, bass_notes
    if melody_notes is None:
        melody_notes = [make_menu_note(f, d, 0.13) for f, d in MELODY]
        bass_notes   = [make_menu_note(f, d, 0.07, "rich") for f, d in BASS]

# ── Shared drawing helpers ─────────────────────────────────────────────────────

def draw_underwater_bg(screen, t, surface_alpha=1.0):
    screen.fill((0, 25, 60))
    # Caustic light blobs
    for i in range(6):
        bx = int(200 + 250 * math.sin(t * 0.007 + i * 1.1))
        by = int(200 + 150 * math.cos(t * 0.005 + i * 0.9))
        s = pygame.Surface((180, 180), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 60, 120, 18), (90, 90), 90)
        screen.blit(s, (bx - 90, by - 90))
    # Light rays
    for i in range(5):
        rx = (i * 190 + t // 4) % 900 - 50
        rs = pygame.Surface((22, 600), pygame.SRCALPHA)
        rs.fill((80, 160, 255, 14))
        screen.blit(rs, (rx, 0))
    # Bubbles
    for i in range(20):
        bx = (i * 173 + t // 6) % 800
        by = 600 - ((i * 97 + t // 2) % 650)
        pygame.draw.circle(screen, (100, 180, 255), (bx, by), 2)
        s2 = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(s2, (200, 230, 255, 40), (4, 4), 4)
        screen.blit(s2, (bx - 4, by - 4))

def draw_button(screen, rect, text, font, hovered, active_color=(0, 140, 180)):
    x, y, w, h = rect
    # Shadow
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 60), (3, 3, w, h), border_radius=12)
    screen.blit(sh, (x, y))
    # Button body
    col = (active_color[0] + 30, active_color[1] + 30, active_color[2] + 30) if hovered else active_color
    pygame.draw.rect(screen, col, rect, border_radius=12)
    # Border
    border_col = (180, 230, 255) if hovered else (100, 180, 220)
    pygame.draw.rect(screen, border_col, rect, 2, border_radius=12)
    # Text
    ts = font.render(text, True, (230, 245, 255))
    tr = ts.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(ts, tr)

# ── Music player state ─────────────────────────────────────────────────────────

class MusicPlayer:
    def __init__(self):
        self.melody_idx = 0
        self.bass_idx = 0
        self.melody_timer = 0
        self.bass_timer = 0
        self.enabled = True

    def update(self):
        _init_music()
        if not self.enabled:
            return
        self.melody_timer -= 1
        self.bass_timer -= 1
        if self.melody_timer <= 0:
            note, dur = MELODY[self.melody_idx % len(MELODY)]
            melody_notes[self.melody_idx % len(melody_notes)].play()
            self.melody_timer = int(dur * 60)
            self.melody_idx += 1
        if self.bass_timer <= 0:
            note, dur = BASS[self.bass_idx % len(BASS)]
            bass_notes[self.bass_idx % len(bass_notes)].play()
            self.bass_timer = int(dur * 60)
            self.bass_idx += 1

music_player = MusicPlayer()

# ── Settings state ─────────────────────────────────────────────────────────────

settings = {
    "music": True,
    "sfx": True,
    "show_depth": True,
    "show_zone": True,
}

# ── Pages ──────────────────────────────────────────────────────────────────────

def run_how_to_play(screen, clock):
    font_title = pygame.font.SysFont(None, 54)
    font_head  = pygame.font.SysFont(None, 34)
    font_body  = pygame.font.SysFont(None, 26)
    font_btn   = pygame.font.SysFont(None, 30)
    t = 0
    back_rect = (30, 530, 160, 44)

    sections = [
        ("  Controls", [
            "Arrow Keys  -  Swim in any direction",
            "The deeper you go, the slower you move",
        ]),
        ("  Your Goal", [
            "Explore the ocean from the bright reef down",
            "to the darkest trench - then return.",
            "What you learn changes everything.",
        ]),
        ("!  Warnings", [
            "Do NOT swim above the surface.",
            "First offence: warning.  Second: last chance.",
            "Third time: you become dinner.",
        ]),
        ("  NPCs", [
            "Swim close to coloured fish to hear them speak.",
            "Their words mean more the deeper you've been.",
        ]),
    ]

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(back_rect).collidepoint(mx, my):
                    return

        t += 1
        music_player.update()
        draw_underwater_bg(screen, t)

        # Title
        title = font_title.render("How to Play", True, (180, 230, 255))
        tr = title.get_rect(center=(400, 55))
        screen.blit(title, tr)
        pygame.draw.line(screen, (0, 140, 200), (80, 80), (720, 80), 1)

        # Sections
        sy = 100
        for heading, lines in sections:
            hs = font_head.render(heading, True, (100, 200, 240))
            screen.blit(hs, (80, sy))
            sy += 36
            for line in lines:
                ls = font_body.render(line, True, (180, 215, 235))
                screen.blit(ls, (100, sy))
                sy += 26
            sy += 10

        # Back button
        hovered = pygame.Rect(back_rect).collidepoint(mx, my)
        draw_button(screen, back_rect, "<  Back", font_btn, hovered)

        pygame.display.flip()
        clock.tick(60)


def run_settings(screen, clock):
    font_title = pygame.font.SysFont(None, 54)
    font_item  = pygame.font.SysFont(None, 32)
    font_btn   = pygame.font.SysFont(None, 30)
    t = 0
    back_rect = (30, 530, 160, 44)

    toggle_rects = {
        "music":      (500, 140, 110, 38),
        "sfx":        (500, 200, 110, 38),
        "show_depth": (500, 260, 110, 38),
        "show_zone":  (500, 320, 110, 38),
    }
    labels = {
        "music":      "Menu Music",
        "sfx":        "Sound Effects",
        "show_depth": "Show Depth Meter",
        "show_zone":  "Show Zone Name",
    }

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(back_rect).collidepoint(mx, my):
                    return
                for key, rect in toggle_rects.items():
                    if pygame.Rect(rect).collidepoint(mx, my):
                        settings[key] = not settings[key]
                        if key == "music":
                            music_player.enabled = settings["music"]

        t += 1
        music_player.update()
        draw_underwater_bg(screen, t)

        # Title
        title = font_title.render("Settings", True, (180, 230, 255))
        tr = title.get_rect(center=(400, 55))
        screen.blit(title, tr)
        pygame.draw.line(screen, (0, 140, 200), (80, 80), (720, 80), 1)

        # Toggles
        for key, rect in toggle_rects.items():
            # Label
            ls = font_item.render(labels[key], True, (180, 215, 235))
            screen.blit(ls, (80, rect[1] + 8))
            # Toggle button
            on = settings[key]
            col = (0, 160, 80) if on else (120, 40, 40)
            hovered = pygame.Rect(rect).collidepoint(mx, my)
            if hovered:
                col = (col[0] + 20, col[1] + 20, col[2] + 20)
            pygame.draw.rect(screen, col, rect, border_radius=10)
            pygame.draw.rect(screen, (180, 230, 255), rect, 2, border_radius=10)
            label = "ON" if on else "OFF"
            ts = font_item.render(label, True, (230, 245, 255))
            tr2 = ts.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
            screen.blit(ts, tr2)

        # Note about settings applying in-game
        note = font_btn.render("Changes apply immediately in game.", True, (100, 160, 180))
        screen.blit(note, (80, 400))

        # Back button
        hovered_back = pygame.Rect(back_rect).collidepoint(mx, my)
        draw_button(screen, back_rect, "<  Back", font_btn, hovered_back)

        pygame.display.flip()
        clock.tick(60)


def run_title_screen(screen, clock):
    _init_music()
    font_title  = pygame.font.SysFont(None, 82)
    font_sub    = pygame.font.SysFont(None, 34)
    font_btn    = pygame.font.SysFont(None, 32)
    font_tiny   = pygame.font.SysFont(None, 22)

    t = 0

    # Button layout
    btn_w, btn_h = 240, 50
    btn_cx = 400
    buttons = [
        (">   Play",         (btn_cx - btn_w // 2, 290, btn_w, btn_h), "play"),
        ("   Map Select",  (btn_cx - btn_w // 2, 348, btn_w, btn_h), "mapselect"),
        ("?  How to Play",  (btn_cx - btn_w // 2, 406, btn_w, btn_h), "htp"),
        ("*   Settings",    (btn_cx - btn_w // 2, 464, btn_w, btn_h), "settings"),
        ("X   Quit",         (btn_cx - btn_w // 2, 522, btn_w, btn_h), "quit"),
    ]

    # Decorative fish swimming across title screen
    deco_fish = [
        {"x": random.randint(-100, 900), "y": random.randint(80, 280),
         "speed": random.uniform(0.4, 1.1), "col": random.choice([
             (255, 200, 80), (100, 220, 255), (180, 255, 120), (255, 140, 100)
         ])}
        for _ in range(5)
    ]

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect, action in buttons:
                    if pygame.Rect(rect).collidepoint(mx, my):
                        if action == "play":
                            return "play"
                        elif action == "mapselect":
                            return "mapselect" 
                        elif action == "htp":
                            run_how_to_play(screen, clock)
                        elif action == "settings":
                            run_settings(screen, clock)
                        elif action == "quit":
                            pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "play" 

        t += 1
        music_player.update()
        draw_underwater_bg(screen, t)

        # Animated title with wave offset
        title_str = "Below the Blue"
        wave_chars = []
        for i, ch in enumerate(title_str):
            off = int(math.sin(t * 0.04 + i * 0.4) * 5)
            cs = font_title.render(ch, True, (
                max(0, min(255, 160 + int(20 * math.sin(t * 0.02 + i)))),
                max(0, min(255, 210 + int(15 * math.sin(t * 0.015 + i)))),
                255
            ))
            wave_chars.append((cs, off))

        # Centre the whole title
        total_w = sum(c.get_width() for c, _ in wave_chars)
        tx = 400 - total_w // 2
        for cs, off in wave_chars:
            screen.blit(cs, (tx, 130 + off))
            tx += cs.get_width()

        # Subtitle
        sub = font_sub.render("Dive deeper. Learn the truth.", True, (120, 190, 230))
        sub_r = sub.get_rect(center=(400, 230))
        screen.blit(sub, sub_r)

        # Decorative swimming fish
        for df in deco_fish:
            df["x"] += df["speed"]
            if df["x"] > 900:
                df["x"] = -60
            fx = int(df["x"])
            fy = df["y"]
            pygame.draw.ellipse(screen, df["col"], (fx - 14, fy - 8, 28, 16))
            pygame.draw.polygon(screen, df["col"], [
                (fx - 14, fy),
                (fx - 26, fy - 7),
                (fx - 26, fy + 7),
            ])
            pygame.draw.circle(screen, (20, 20, 30), (fx + 10, fy - 2), 3)
            pygame.draw.circle(screen, (255, 255, 255), (fx + 11, fy - 3), 1)

        # Separator line
        pygame.draw.line(screen, (0, 100, 160), (120, 300), (680, 300), 1)

        # Buttons
        for label, rect, action in buttons:
            hovered = pygame.Rect(rect).collidepoint(mx, my)
            if action == "quit":
                draw_button(screen, rect, label, font_btn, hovered, (100, 30, 30))
            else:
                draw_button(screen, rect, label, font_btn, hovered)

        # Version tag
        ver = font_tiny.render("v0.1 - Below the Blue", True, (60, 100, 130))
        screen.blit(ver, (10, 578))

        pygame.display.flip()
        clock.tick(60)