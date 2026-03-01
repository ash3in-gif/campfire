import pygame
import math


class OxygenSystem:
    def __init__(self, max_oxygen=1800):
        self.max_oxygen = max_oxygen   # frames of air (30s at 60fps)
        self.oxygen = float(max_oxygen)
        self.dead = False
        self.warning = False
        self.font = pygame.font.SysFont(None, 24)
        self.bubble_timer = 0

    def set_max(self, new_max):
        self.max_oxygen = new_max
        self.oxygen = float(new_max)

    def update(self, depth_ratio, at_surface):
        if self.dead:
            return
        if at_surface:
            # Refill fast at surface
            self.oxygen = min(self.max_oxygen, self.oxygen + 12)
            return
        # Drain faster the deeper you go
        drain = 0.5 + depth_ratio * 1.5
        self.oxygen -= drain
        if self.oxygen <= 0:
            self.oxygen = 0
            self.dead = True
        self.warning = self.oxygen < self.max_oxygen * 0.25

    def refill(self, amount=300):
        self.oxygen = min(self.max_oxygen, self.oxygen + amount)

    def reset(self):
        self.oxygen = float(self.max_oxygen)
        self.dead = False
        self.warning = False

    def draw(self, screen):
        # Bar position — bottom left
        bx, by = 14, 560
        bw, bh = 180, 16

        ratio = self.oxygen / self.max_oxygen

        # Background
        bg = pygame.Surface((bw + 4, bh + 4), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        pygame.draw.rect(bg, (0, 80, 120), (0, 0, bw + 4, bh + 4), 1, border_radius=6)
        screen.blit(bg, (bx - 2, by - 2))

        # Fill colour — green → yellow → red
        if ratio > 0.5:
            r = int(255 * (1 - ratio) * 2)
            g = 200
        else:
            r = 220
            g = int(200 * ratio * 2)
        fill_col = (r, g, 60)

        fill_w = int(bw * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, fill_col,
                             (bx, by, fill_w, bh), border_radius=5)

        # Pulse border when low
        t = pygame.time.get_ticks()
        if self.warning:
            pulse = int(80 + 60 * math.sin(t * 0.008))
            pygame.draw.rect(screen, (255, pulse, 0),
                             (bx - 2, by - 2, bw + 4, bh + 4), 2, border_radius=6)

        # Label
        label = self.font.render("O2", True, (180, 220, 240))
        screen.blit(label, (bx + bw + 8, by))

        # Critical warning text
        if self.warning:
            warn_alpha = int(128 + 127 * math.sin(t * 0.01))
            ws = self.font.render("LOW OXYGEN!", True, (255, 80, 80))
            ws.set_alpha(warn_alpha)
            screen.blit(ws, (bx + bw // 2 - ws.get_width() // 2, by - 22))


class OxygenRefill:
    """Pickup that restores oxygen — hidden in anemones, rocks, vents"""
    def __init__(self, x, y, amount=300, rtype="bubble"):
        self.x = x
        self.y = y
        self.amount = amount
        self.rtype = rtype
        self.collected = False
        self.respawn_timer = 0
        self.RESPAWN = 1800  # 30s

    def update(self):
        if self.collected:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.collected = False

    def draw(self, screen, camera_y):
        if self.collected:
            return
        sy = int(self.y - camera_y)
        if sy < -20 or sy > 650:
            return
        t = pygame.time.get_ticks()
        pulse = int(30 + 15 * math.sin(t * 0.005))

        # Glow
        gs = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(gs, (100, 200, 255, pulse), (16, 16), 14)
        screen.blit(gs, (self.x - 16, sy - 16))

        # Icon
        pygame.draw.circle(screen, (140, 220, 255), (self.x, sy), 7)
        pygame.draw.circle(screen, (200, 240, 255), (self.x - 2, sy - 2), 3)

        # Tiny O2 label
        f = pygame.font.SysFont(None, 16)
        ts = f.render("O2", True, (0, 40, 80))
        screen.blit(ts, (self.x - ts.get_width() // 2, sy - ts.get_height() // 2))

    def check_collect(self, fish_x, fish_y, camera_y, oxygen_system):
        if self.collected:
            return False
        sy = self.y - camera_y
        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_y - sy) ** 2)
        if dist < 30:
            self.collected = True
            self.respawn_timer = self.RESPAWN
            oxygen_system.refill(self.amount)
            return True
        return False
