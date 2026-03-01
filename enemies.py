import pygame
import math
import random


class PatrolFish:
    """Map 2 — guards a zone, chases if you get too close"""
    def __init__(self, x, y, patrol_range=120):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.patrol_range = patrol_range
        self.speed = 1.2
        self.direction = 1
        self.alert = False
        self.alert_timer = 0
        self.caught = False
        self.size = 18

    def update(self, fish_x, fish_y, camera_y):
        screen_y = self.y - camera_y
        fish_screen_y = fish_y

        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_screen_y - screen_y) ** 2)

        if dist < 150:
            self.alert = True
            self.alert_timer = 60
            # Chase
            dx = fish_x - self.x
            dy = fish_screen_y - screen_y
            length = math.sqrt(dx ** 2 + dy ** 2) or 1
            self.x += dx / length * 2.2
            self.y += dy / length * 2.2 * 0.3  # world coords
        else:
            if self.alert_timer > 0:
                self.alert_timer -= 1
            else:
                self.alert = False
            # Patrol
            self.x += self.speed * self.direction
            if abs(self.x - self.start_x) > self.patrol_range:
                self.direction *= -1

        if dist < 22:
            self.caught = True

    def draw(self, screen, camera_y):
        sy = int(self.y - camera_y)
        if sy < -40 or sy > 680:
            return

        col = (220, 60, 60) if self.alert else (180, 80, 80)
        facing_left = self.direction < 0

        # Body
        pygame.draw.ellipse(screen, col, (int(self.x) - 16, sy - 9, 32, 18))
        # Tail
        if not facing_left:
            pygame.draw.polygon(screen, col, [
                (int(self.x) - 16, sy),
                (int(self.x) - 28, sy - 8),
                (int(self.x) - 28, sy + 8),
            ])
        else:
            pygame.draw.polygon(screen, col, [
                (int(self.x) + 16, sy),
                (int(self.x) + 28, sy - 8),
                (int(self.x) + 28, sy + 8),
            ])
        # Eye
        ex = int(self.x) + (10 if not facing_left else -10)
        pygame.draw.circle(screen, (255, 255, 0), (ex, sy - 2), 4)
        pygame.draw.circle(screen, (0, 0, 0), (ex, sy - 2), 2)

        # Alert ring
        if self.alert:
            t = pygame.time.get_ticks()
            pulse = int(40 + 30 * math.sin(t * 0.01))
            s = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 100, 0, pulse), (30, 30), 28, 2)
            screen.blit(s, (int(self.x) - 30, sy - 30))


class BlindHunter:
    """Map 3 -- fast dark hunter fish that tracks sound (fish speed)"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = 0.2
        self.alert = False
        self.caught = False
        self.hearing_range = 200
        self.direction = 1

    def update(self, fish_x, fish_y, camera_y, fish_speed):
        screen_y = self.y - camera_y
        fish_screen_y = fish_y
        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_screen_y - screen_y) ** 2)
        noise_range = self.hearing_range * max(0.3, fish_speed / 2.5)
        if dist < noise_range:
            self.alert = True
            dx = fish_x - self.x
            dy = fish_screen_y - screen_y
            length = math.sqrt(dx ** 2 + dy ** 2) or 1
            chase_speed = 2.2 + fish_speed * 0.4
            self.vx = dx / length * chase_speed
            self.vy = dy / length * chase_speed * 0.5
            self.direction = 1 if dx > 0 else -1
        else:
            self.alert = False
            self.vx += random.uniform(-0.15, 0.15)
            self.vy += random.uniform(-0.06, 0.06)
            self.vx = max(-0.8, min(0.8, self.vx))
            self.vy = max(-0.4, min(0.4, self.vy))
            if abs(self.vx) > 0.1:
                self.direction = 1 if self.vx > 0 else -1
        self.x += self.vx
        self.y += self.vy
        self.x = max(30, min(770, self.x))
        if dist < 28:
            self.caught = True

    def draw(self, screen, camera_y):
        sy = int(self.y - camera_y)
        if sy < -40 or sy > 680:
            return
        t = pygame.time.get_ticks()
        ix = int(self.x)
        col = (160, 40, 40) if self.alert else (100, 30, 30)
        # Body - bigger than patrol fish
        pygame.draw.ellipse(screen, col, (ix - 22, sy - 12, 44, 24))
        # Tail
        if self.direction > 0:
            pygame.draw.polygon(screen, col, [(ix-22, sy), (ix-38, sy-10), (ix-38, sy+10)])
        else:
            pygame.draw.polygon(screen, col, [(ix+22, sy), (ix+38, sy-10), (ix+38, sy+10)])
        # Dorsal fin
        pygame.draw.polygon(screen, col, [(ix-8, sy-12), (ix+8, sy-12), (ix, sy-24)])
        # Eye
        ex = ix + (14 if self.direction > 0 else -14)
        pygame.draw.circle(screen, (255, 60, 60), (ex, sy-2), 5)
        pygame.draw.circle(screen, (0, 0, 0),     (ex, sy-2), 3)
        pygame.draw.circle(screen, (255, 255, 255), (ex+1, sy-3), 1)
        # Alert glow
        if self.alert:
            pulse = int(40 + 30 * math.sin(t * 0.01))
            s = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 0, 0, pulse), (35, 35), 32, 2)
            screen.blit(s, (ix-35, sy-35))

class OriginCircler:
    """Map 5 — massive slow creature that orbits the center"""
    def __init__(self, center_x, center_y, radius=220):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.radius = radius
        self.angle = 0
        self.speed = 0.004
        self.caught = False

    @property
    def x(self):
        return self.center_x + self.radius * math.cos(self.angle)

    @property
    def y(self):
        return self.center_y + self.radius * math.sin(self.angle)

    def update(self, fish_x, fish_y, camera_y):
        self.angle += self.speed
        screen_y = self.y - camera_y
        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_y - screen_y) ** 2)
        if dist < 40:
            self.caught = True

    def draw(self, screen, camera_y):
        sy = int(self.y - camera_y)
        sx = int(self.x)
        if sy < -80 or sy > 720:
            return
        t = pygame.time.get_ticks()
        glow = int(15 + 10 * math.sin(t * 0.002))

        # Massive dark body
        s = pygame.Surface((120, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (5, 5, 15, 200), (0, 0, 120, 80))
        pygame.draw.ellipse(s, (0, glow, glow + 5, 80), (10, 10, 100, 60))
        screen.blit(s, (sx - 60, sy - 40))

        # Huge eye
        pygame.draw.circle(screen, (0, 30, 20), (sx + 20, sy - 10), 14)
        pygame.draw.circle(screen, (0, 80, 40), (sx + 20, sy - 10), 8)
        pygame.draw.circle(screen, (200, 255, 200), (sx + 24, sy - 14), 3)

        # Tentacles trailing behind
        for i in range(5):
            wave = math.sin(t * 0.004 + i * 0.8) * 18
            tx = sx - 50 - i * 10
            ty = sy + int(wave)
            pygame.draw.line(screen, (5, 5, 15),
                             (sx - 40, sy), (tx, ty), 3)


def create_enemies_for_map(map_id):
    enemies = []
    if map_id == 2:
        # Patrol fish guarding the drop-off
        enemies.append(PatrolFish(300, 900, 150))
        enemies.append(PatrolFish(550, 1100, 120))
        enemies.append(PatrolFish(200, 1300, 100))
    elif map_id == 3:
        # Blind hunters in the trench
        enemies.append(BlindHunter(250, 1700))
        enemies.append(BlindHunter(550, 2000))
        enemies.append(BlindHunter(350, 2300))
    elif map_id == 4:
        # Mix
        enemies.append(BlindHunter(300, 2700))
        enemies.append(BlindHunter(600, 3100))
        enemies.append(PatrolFish(400, 3500, 80))
    elif map_id == 5:
        enemies.append(OriginCircler(400, 4500, 200))
        enemies.append(BlindHunter(200, 4200))
        enemies.append(BlindHunter(600, 4700))
    return enemies