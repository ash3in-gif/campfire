import pygame
import math
import random

class Collectible:
    def __init__(self, x, y, ctype, title, description):
        self.x = x
        self.y = y
        self.type = ctype
        self.title = title
        self.description = description
        self.collected = False
        self.pulse = random.uniform(0, 6.28)

    def draw(self, screen, camera_y):
        if self.collected:
            return
        sy = int(self.y - camera_y)
        if sy < -30 or sy > 650:
            return
        t = pygame.time.get_ticks()
        glow = int(40 + 20 * math.sin(t * 0.004 + self.pulse))

        if self.type == "shell":
            col = (220, 180, 120)
            pygame.draw.ellipse(screen, col, (self.x - 10, sy - 7, 20, 14))
            pygame.draw.line(screen, (180, 140, 80), (self.x, sy - 7), (self.x, sy + 7), 1)
            for i in range(3):
                pygame.draw.line(screen, (180, 140, 80),
                                 (self.x - 8 + i * 8, sy - 7),
                                 (self.x - 6 + i * 6, sy + 7), 1)
        elif self.type == "bottle":
            col = (100, 200, 160)
            pygame.draw.rect(screen, col, (self.x - 4, sy - 10, 8, 18), border_radius=3)
            pygame.draw.rect(screen, (80, 160, 130), (self.x - 2, sy - 14, 4, 5))
            pygame.draw.rect(screen, (240, 230, 180), (self.x - 3, sy - 8, 6, 12))
        elif self.type == "photo":
            pygame.draw.rect(screen, (240, 235, 210), (self.x - 12, sy - 9, 24, 18))
            pygame.draw.rect(screen, (180, 160, 120), (self.x - 10, sy - 7, 20, 12))
            pygame.draw.rect(screen, (200, 180, 140), (self.x - 12, sy - 9, 24, 18), 2)
        elif self.type == "tag":
            pygame.draw.rect(screen, (200, 60, 60), (self.x - 8, sy - 10, 16, 20), border_radius=2)
            pygame.draw.circle(screen, (150, 150, 150), (self.x, sy - 10), 3)
            font = pygame.font.SysFont(None, 14)
            ts = font.render("ID", True, (255, 255, 255))
            screen.blit(ts, (self.x - 5, sy - 6))
        elif self.type == "anchor":
            pygame.draw.line(screen, (130, 130, 150), (self.x, sy - 12), (self.x, sy + 8), 3)
            pygame.draw.line(screen, (130, 130, 150), (self.x - 8, sy + 8), (self.x + 8, sy + 8), 3)
            pygame.draw.line(screen, (130, 130, 150), (self.x - 6, sy + 4), (self.x - 10, sy + 8), 2)
            pygame.draw.line(screen, (130, 130, 150), (self.x + 6, sy + 4), (self.x + 10, sy + 8), 2)
            pygame.draw.circle(screen, (130, 130, 150), (self.x, sy - 12), 4, 2)
        elif self.type == "eye":
            pygame.draw.circle(screen, (20, 20, 40), (self.x, sy), 12)
            pygame.draw.circle(screen, (0, glow + 100, glow + 80), (self.x, sy), 8)
            pygame.draw.circle(screen, (200, 255, 220), (self.x, sy), 3)
            pygame.draw.circle(screen, (0, 0, 0), (self.x, sy), 2)

        # Glow ring
        gs = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(gs, (200, 240, 255, glow), (20, 20), 18)
        screen.blit(gs, (self.x - 20, sy - 20))

    def check_collect(self, fish_x, fish_y, camera_y):
        if self.collected:
            return False
        sy = self.y - camera_y
        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_y - sy) ** 2)
        if dist < 35:
            self.collected = True
            return True
        return False


def create_collectibles():
    items = []
    items.append(Collectible(180, 200, "shell", "A Conch Shell",
        "Still warm from the sun. Someone left it here."))
    items.append(Collectible(580, 350, "photo", "A Photograph",
        "A family on a boat. They look happy. The water looks clean."))
    items.append(Collectible(320, 480, "bottle", "Message in a Bottle",
        "It reads: To whoever finds this, the ocean is forever. Signed 1987."))
    items.append(Collectible(250, 850, "tag", "A Fishing Tag",
        "ID 4471. Species: Bluefin Tuna. Status: Unknown."))
    items.append(Collectible(600, 1000, "anchor", "A Broken Anchor",
        "The chain snapped. Whatever it held is long gone."))
    items.append(Collectible(150, 1200, "bottle", "Another Bottle",
        "Empty. No message. Just plastic. Here for 400 years."))
    items.append(Collectible(500, 1350, "photo", "A Torn Photo",
        "The same family. Older now. The water looks different."))
    items.append(Collectible(300, 1700, "tag", "Research Tag 0012",
        "Last signal 2019. The scientist retired after seeing the data."))
    items.append(Collectible(550, 2000, "shell", "A Bleached Shell",
        "White. Hollow. It left when the water warmed."))
    items.append(Collectible(200, 2300, "anchor", "Ship Log Plate",
        "SS Meridian, lost 1943. 31 crew. The sea remembers."))
    items.append(Collectible(400, 2700, "eye", "Something Watching",
        "It doesn't move. But you feel it notice you."))
    items.append(Collectible(200, 3000, "eye", "A Signal",
        "A pulse. Regular. Not natural. Someone sent this."))
    items.append(Collectible(600, 3300, "eye", "The Last Record",
        "A dive computer. Final entry: It is not empty down here."))
    items.append(Collectible(350, 3600, "eye", "Origin",
        "Everything started here. Long before the reef. Before us."))
    return items


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class CollectibleDisplay:
    def __init__(self):
        self.active = False
        self.title = ""
        self.desc = ""
        self.timer = 0
        self.DURATION = 280
        self.font_title = pygame.font.SysFont(None, 28)
        self.font_desc  = pygame.font.SysFont(None, 23)
        self.collected_items = []

    def trigger(self, title, desc):
        self.active = True
        self.title = title
        self.desc = desc
        self.timer = self.DURATION
        self.collected_items.append(title)

    def update_and_draw(self, screen):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            return

        # Fade in and out
        if self.timer > self.DURATION - 30:
            alpha = int(255 * (self.DURATION - self.timer) / 30)
        elif self.timer < 60:
            alpha = int(255 * self.timer / 60)
        else:
            alpha = 255

        BOX_W = 300
        PAD   = 10
        max_text_w = BOX_W - PAD * 2 - 36  # leave room for icon

        title_lines = wrap_text(self.title, self.font_title, max_text_w)
        desc_lines  = wrap_text(self.desc,  self.font_desc,  max_text_w)

        line_h_title = self.font_title.get_height() + 3
        line_h_desc  = self.font_desc.get_height()  + 2
        content_h = (len(title_lines) * line_h_title +
                     len(desc_lines)  * line_h_desc  +
                     PAD * 2 + 6)
        BOX_H = max(56, content_h)

        # Position: top-right corner, always on screen
        bx = 800 - BOX_W - 14
        by = 14

        # Background box
        box = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
        box.fill((0, 15, 35, 200))
        pygame.draw.rect(box, (0, 160, 180), (0, 0, BOX_W, BOX_H), 2, border_radius=8)
        box.set_alpha(alpha)
        screen.blit(box, (bx, by))

        # Icon circle
        icon_surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(icon_surf, (0, 180, 160, 220), (14, 14), 13)
        icon_surf.set_alpha(alpha)
        screen.blit(icon_surf, (bx + PAD, by + PAD))
        star = self.font_title.render("✦", True, (255, 240, 180))
        star.set_alpha(alpha)
        screen.blit(star, (bx + PAD + 5, by + PAD + 4))

        # Title lines
        tx = bx + PAD + 34
        ty = by + PAD
        for line in title_lines:
            ts = self.font_title.render(line, True, (160, 230, 255))
            ts.set_alpha(alpha)
            screen.blit(ts, (tx, ty))
            ty += line_h_title

        ty += 4
        # Desc lines
        for line in desc_lines:
            ds = self.font_desc.render(line, True, (180, 215, 225))
            ds.set_alpha(alpha)
            screen.blit(ds, (tx, ty))
            ty += line_h_desc

    def draw_counter(self, screen, font, total):
        count = len(self.collected_items)
        text = f"Memories: {count}/{total}"
        ts = font.render(text, True, (200, 230, 220))
        tw = ts.get_width()
        # Dark pill behind text
        pad = 6
        pill = pygame.Surface((tw + pad * 2, ts.get_height() + pad), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 150))
        pygame.draw.rect(pill, (0, 100, 120), (0, 0, tw + pad * 2, ts.get_height() + pad), 1, border_radius=6)
        screen.blit(pill, (14, 70))
        screen.blit(ts, (14 + pad, 70 + pad // 2))
