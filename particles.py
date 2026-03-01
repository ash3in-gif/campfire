import pygame
import random
import math

class Bubble:
    def __init__(self, x, y):
        self.x = float(x) + random.uniform(-6, 6)
        self.y = float(y) + random.uniform(-4, 4)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.8, -0.2)
        self.r = random.randint(2, 5)
        self.alpha = random.randint(120, 200)
        self.life = random.randint(30, 70)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.age += 1
        self.alpha = max(0, int(200 * (1 - self.age / self.life)))

    def draw(self, screen):
        if self.alpha <= 0:
            return
        s = pygame.Surface((self.r * 2 + 2, self.r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (180, 220, 255, self.alpha), (self.r + 1, self.r + 1), self.r)
        pygame.draw.circle(s, (255, 255, 255, self.alpha // 2), (self.r, self.r), max(1, self.r - 1), 1)
        screen.blit(s, (int(self.x) - self.r - 1, int(self.y) - self.r - 1))

    @property
    def dead(self):
        return self.age >= self.life


class BubbleTrail:
    def __init__(self):
        self.bubbles = []
        self.spawn_timer = 0

    def update(self, fish_x, fish_y, speed):
        self.spawn_timer += 1
        interval = max(2, int(8 - speed * 3))
        if self.spawn_timer >= interval:
            self.bubbles.append(Bubble(fish_x, fish_y))
            self.spawn_timer = 0
        for b in self.bubbles:
            b.update()
        self.bubbles = [b for b in self.bubbles if not b.dead]

    def draw(self, screen):
        for b in self.bubbles:
            b.draw(screen)
