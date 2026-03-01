import pygame
import math


class Gate:
    def __init__(self, y, required_memories):
        self.y = y
        self.required = required_memories
        self.open = False
        self.open_anim = 0.0
        self.font_big   = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 22)

    def update(self, collected_count):
        self.open = collected_count >= self.required
        if self.open:
            self.open_anim = min(1.0, self.open_anim + 0.025)
        else:
            self.open_anim = max(0.0, self.open_anim - 0.025)

    def blocks(self, fish_y, camera_y):
        if self.open:
            return False
        return (fish_y + camera_y) > (self.y - 20)

    def push_fish(self, fish_y, camera_y):
        world_y = fish_y + camera_y
        if world_y > self.y - 20:
            return fish_y - (world_y - (self.y - 20))
        return fish_y

    def draw(self, screen, camera_y, collected_count):
        sy = int(self.y - camera_y)
        if sy < -60 or sy > 680:
            return

        t = pygame.time.get_ticks()

        if self.open_anim >= 1.0:
            return  # fully gone

        if self.open:
            # Dissolving — shrink from centre outward
            alpha = max(0, int(200 * (1.0 - self.open_anim)))
            w = int(800 * (1.0 - self.open_anim))
            s = pygame.Surface((w, 10), pygame.SRCALPHA)
            s.fill((0, 220, 140, alpha))
            screen.blit(s, (400 - w // 2, sy - 5))
        else:
            # Locked bar — solid with pulse
            pulse = int(140 + 80 * math.sin(t * 0.004))

            # Thick bar
            bar = pygame.Surface((800, 12), pygame.SRCALPHA)
            bar.fill((0, pulse // 2, 80, 220))
            screen.blit(bar, (0, sy - 6))

            # Bright border lines
            pygame.draw.line(screen, (0, pulse, 180), (0, sy - 6), (800, sy - 6), 2)
            pygame.draw.line(screen, (0, pulse, 180), (0, sy + 6), (800, sy + 6), 2)

            # Lock body (drawn, not emoji)
            lx, ly = 400, sy
            # Shackle arc
            pygame.draw.arc(screen, (0, 200, 140),
                            (lx - 10, ly - 18, 20, 18), 0, math.pi, 3)
            # Body
            pygame.draw.rect(screen, (0, 180, 120),
                             (lx - 13, ly - 6, 26, 20), border_radius=4)
            # Keyhole
            pygame.draw.circle(screen, (0, 60, 40), (lx, ly + 2), 4)
            pygame.draw.rect(screen, (0, 60, 40), (lx - 2, ly + 2, 4, 6))

            # Progress bar above the gate
            remaining = self.required - collected_count
            have = collected_count
            total = self.required

            bar_w = 260
            bar_h = 12
            bx = 400 - bar_w // 2
            by = sy - 40

            # Background
            bg = pygame.Surface((bar_w + 4, bar_h + 4), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            pygame.draw.rect(bg, (0, 120, 100),
                             (0, 0, bar_w + 4, bar_h + 4), 1, border_radius=6)
            screen.blit(bg, (bx - 2, by - 2))

            # Fill
            fill_w = int(bar_w * min(1.0, have / max(1, total)))
            if fill_w > 0:
                pygame.draw.rect(screen, (0, 200, 140),
                                 (bx, by, fill_w, bar_h), border_radius=5)

            # Label
            label = f"Memories: {have} / {total}  -- swim down to pass"
            ts = self.font_small.render(label, True, (160, 230, 210))
            screen.blit(ts, (400 - ts.get_width() // 2, by - 20))
