import pygame
import random
import math

class WorldObject:
    def __init__(self, x, y, obj_type):
        self.x = x
        self.y = y
        self.type = obj_type

def generate_world():
    objects = []
    rng = random.Random(42)  # fixed seed so world is consistent

    # ── The Reef (0–600) ──────────────────────────────────────────────────────
    for _ in range(50):
        x = rng.randint(50, 750)
        y = rng.randint(380, 590)
        objects.append(WorldObject(x, y, "coral"))
    for _ in range(8):
        x = rng.randint(50, 750)
        y = rng.randint(350, 590)
        objects.append(WorldObject(x, y, "coral_fan"))
    # Sandy floor detail
    for _ in range(20):
        x = rng.randint(30, 770)
        y = rng.randint(560, 600)
        objects.append(WorldObject(x, y, "sand_ripple"))

    # ── The Drop-Off (600–1500) ───────────────────────────────────────────────
    for _ in range(20):
        x = rng.randint(50, 750)
        y = rng.randint(700, 1400)
        objects.append(WorldObject(x, y, "rock"))
    objects.append(WorldObject(350, 1100, "shipwreck"))
    objects.append(WorldObject(560, 950, "shipwreck_debris"))
    for _ in range(12):
        x = rng.randint(100, 700)
        y = rng.randint(750, 1450)
        objects.append(WorldObject(x, y, "net"))
    for _ in range(6):
        x = rng.randint(100, 700)
        y = rng.randint(800, 1400)
        objects.append(WorldObject(x, y, "trash"))

    # ── The Trench (1500–2500) ────────────────────────────────────────────────
    for _ in range(15):
        x = rng.randint(50, 750)
        y = rng.randint(1600, 2450)
        objects.append(WorldObject(x, y, "deep_rock"))
    for _ in range(8):
        x = rng.randint(100, 700)
        y = rng.randint(1800, 2800)
        objects.append(WorldObject(x, y, "creature"))
    for _ in range(5):
        x = rng.randint(50, 750)
        y = rng.randint(1600, 2400)
        objects.append(WorldObject(x, y, "vent"))

    # ── The Unknown (2500–5000) ───────────────────────────────────────────────
    for _ in range(30):
        x = rng.randint(50, 750)
        y = rng.randint(2600, 4900)
        objects.append(WorldObject(x, y, "unknown_rock"))
    for _ in range(15):
        x = rng.randint(50, 750)
        y = rng.randint(2700, 4800)
        objects.append(WorldObject(x, y, "unknown_creature"))
    for _ in range(8):
        x = rng.randint(100, 700)
        y = rng.randint(2800, 4500)
        objects.append(WorldObject(x, y, "signal"))
    # Abyss floor structures
    for _ in range(6):
        x = rng.randint(50, 750)
        y = rng.randint(4600, 4900)
        objects.append(WorldObject(x, y, "abyss_pillar"))

    return objects


def draw_world(screen, objects, camera_y, depth_ratio):
    t = pygame.time.get_ticks()

    for obj in objects:
        screen_y = int(obj.y - camera_y)
        if screen_y < -80 or screen_y > 720:
            continue

        if obj.type == "coral":
            b = max(0, min(255, int(255 * (1 - depth_ratio * 3))))
            pygame.draw.polygon(screen, (255, b, 80), [
                (obj.x, screen_y),
                (obj.x - 12, screen_y + 30),
                (obj.x + 12, screen_y + 30)
            ])
            pygame.draw.polygon(screen, (80, 255, b), [
                (obj.x + 15, screen_y + 5),
                (obj.x + 5,  screen_y + 30),
                (obj.x + 25, screen_y + 30)
            ])
            # Small branch
            pygame.draw.line(screen, (255, max(0, b - 40), 60),
                             (obj.x + 5, screen_y + 10),
                             (obj.x + 16, screen_y), 2)

        elif obj.type == "coral_fan":
            b = max(0, min(255, int(220 * (1 - depth_ratio * 3))))
            for i in range(7):
                angle = math.radians(-60 + i * 20)
                ex = int(obj.x + 28 * math.sin(angle))
                ey = int(screen_y - 28 * math.cos(angle))
                pygame.draw.line(screen, (b, 80, 200), (obj.x, screen_y), (ex, ey), 2)
            pygame.draw.circle(screen, (b, 60, 180), (obj.x, screen_y), 4)

        elif obj.type == "sand_ripple":
            pygame.draw.arc(screen, (180, 160, 100),
                            (obj.x - 15, screen_y - 3, 30, 6), 0, math.pi, 1)

        elif obj.type == "rock":
            pygame.draw.ellipse(screen, (75, 80, 90),
                                (obj.x - 22, screen_y - 11, 44, 22))
            pygame.draw.ellipse(screen, (60, 65, 75),
                                (obj.x - 10, screen_y - 6, 18, 10))

        elif obj.type == "shipwreck":
            pygame.draw.rect(screen, (55, 45, 35),
                             (obj.x - 65, screen_y - 22, 130, 44))
            pygame.draw.polygon(screen, (45, 35, 25), [
                (obj.x - 65, screen_y - 22),
                (obj.x - 85, screen_y + 22),
                (obj.x - 65, screen_y + 22),
            ])
            pygame.draw.line(screen, (40, 30, 20),
                             (obj.x - 15, screen_y - 22),
                             (obj.x + 25, screen_y - 75), 5)
            pygame.draw.line(screen, (40, 30, 20),
                             (obj.x + 25, screen_y - 75),
                             (obj.x + 50, screen_y - 60), 2)
            pygame.draw.circle(screen, (25, 25, 35), (obj.x - 25, screen_y), 9)
            pygame.draw.circle(screen, (15, 15, 25), (obj.x - 25, screen_y), 6)
            pygame.draw.circle(screen, (25, 25, 35), (obj.x + 20, screen_y + 5), 7)
            # Algae on hull
            for i in range(4):
                gx = obj.x - 50 + i * 30
                pygame.draw.line(screen, (40, 100, 50),
                                 (gx, screen_y - 22),
                                 (gx + 5, screen_y - 35), 2)

        elif obj.type == "shipwreck_debris":
            pygame.draw.rect(screen, (50, 40, 30),
                             (obj.x - 30, screen_y - 10, 60, 20))
            pygame.draw.line(screen, (40, 30, 20),
                             (obj.x - 30, screen_y - 10),
                             (obj.x + 20, screen_y + 10), 2)

        elif obj.type == "net":
            col = (90, 110, 90)
            for i in range(5):
                pygame.draw.line(screen, col,
                                 (obj.x + i * 9, screen_y),
                                 (obj.x + i * 9, screen_y + 45), 1)
            for i in range(6):
                pygame.draw.line(screen, col,
                                 (obj.x, screen_y + i * 9),
                                 (obj.x + 36, screen_y + i * 9), 1)

        elif obj.type == "trash":
            r = pygame.Rect(obj.x - 5, screen_y - 8, 10, 16)
            pygame.draw.rect(screen, (80, 110, 80), r, border_radius=2)
            pygame.draw.rect(screen, (60, 90, 60), r, 1, border_radius=2)

        elif obj.type == "deep_rock":
            pygame.draw.ellipse(screen, (28, 28, 38),
                                (obj.x - 28, screen_y - 14, 56, 28))
            pygame.draw.ellipse(screen, (20, 20, 30),
                                (obj.x - 14, screen_y - 8, 24, 14))

        elif obj.type == "creature":
            glow = abs(int(t / 10) % 100 - 50)
            g = max(0, min(255, glow + 50))
            b2 = max(0, min(255, glow + 80))
            pygame.draw.circle(screen, (0, g, b2), (obj.x, screen_y), 11)
            pygame.draw.circle(screen, (200, 255, 255), (obj.x - 3, screen_y - 3), 2)
            pygame.draw.circle(screen, (200, 255, 255), (obj.x + 3, screen_y - 3), 2)
            # Tentacle wisps
            for i in range(3):
                angle = math.radians(200 + i * 40 + math.sin(t * 0.003 + i) * 15)
                ex = int(obj.x + 14 * math.cos(angle))
                ey = int(screen_y + 14 * math.sin(angle))
                pygame.draw.line(screen, (0, g // 2, b2 // 2), (obj.x, screen_y), (ex, ey), 1)

        elif obj.type == "vent":
            pygame.draw.ellipse(screen, (40, 35, 30),
                                (obj.x - 10, screen_y - 5, 20, 10))
            # Particle stream
            for i in range(4):
                vy = (t // 20 + i * 8) % 40
                vx = int(math.sin(t * 0.01 + i) * 4)
                va = max(0, 180 - vy * 4)
                vs = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(vs, (180, 140, 80, va), (3, 3), 3)
                screen.blit(vs, (obj.x + vx - 3, screen_y - vy - 3))

        elif obj.type == "unknown_rock":
            # Jagged, alien-looking
            dr = max(0, int(40 - depth_ratio * 20))
            col = (dr, dr + 5, dr + 15)
            pts = []
            for i in range(6):
                angle = math.radians(i * 60 + math.sin(obj.x + obj.y) * 20)
                r2 = 18 + int(math.sin(obj.x * 0.1 + i) * 8)
                pts.append((int(obj.x + r2 * math.cos(angle)),
                             int(screen_y + r2 * 0.5 * math.sin(angle))))
            if len(pts) >= 3:
                pygame.draw.polygon(screen, col, pts)
            pygame.draw.polygon(screen, (max(0, col[0] - 10),) * 3, pts, 1)

        elif obj.type == "unknown_creature":
            # Barely visible, pulsing
            glow2 = int(15 + 10 * math.sin(t * 0.002 + obj.x))
            s = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, glow2, glow2 + 10, 80), (15, 15), 12)
            pygame.draw.circle(s, (glow2, glow2 * 2, glow2 * 3, 40), (15, 15), 8)
            screen.blit(s, (obj.x - 15, screen_y - 15))

        elif obj.type == "signal":
            # Pulsing ring — something is broadcasting
            pulse = (t // 8 + int(obj.x)) % 60
            for ring in range(3):
                rr = pulse + ring * 20
                if rr > 60:
                    continue
                ra = max(0, int(100 - rr * 1.6))
                rs = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(rs, (0, 180, 120, ra), (rr + 2, rr + 2), rr, 1)
                screen.blit(rs, (obj.x - rr - 2, screen_y - rr - 2))
            pygame.draw.circle(screen, (0, 160, 100), (obj.x, screen_y), 4)

        elif obj.type == "abyss_pillar":
            # Towering dark columns
            ph = 120
            pygame.draw.rect(screen, (15, 15, 25),
                             (obj.x - 12, screen_y - ph, 24, ph))
            pygame.draw.rect(screen, (10, 10, 20),
                             (obj.x - 16, screen_y - 10, 32, 14))
            # Faint glow at top
            gs2 = pygame.Surface((40, 40), pygame.SRCALPHA)
            gv = int(20 + 10 * math.sin(t * 0.003 + obj.x))
            pygame.draw.circle(gs2, (0, gv, gv + 20, 60), (20, 20), 18)
            screen.blit(gs2, (obj.x - 20, screen_y - ph - 20))
