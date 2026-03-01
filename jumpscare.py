import pygame
import numpy as np
import random
import math

def make_scare_sound():
    sample_rate = 44100
    frames = int(0.8 * sample_rate)
    t = np.linspace(0, 0.8, frames, False)
    # Harsh discordant noise + low boom
    noise = np.random.uniform(-1, 1, frames)
    boom = np.sin(2 * np.pi * 40 * t) * np.exp(-t * 3)
    screech = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 5) * 0.4
    wave = noise * 0.3 + boom * 0.5 + screech
    wave = np.clip(wave, -1, 1)
    fade = int(sample_rate * 0.05)
    wave[-fade:] *= np.linspace(1, 0, fade)
    wave = (wave * 32767 * 0.6).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((wave, wave)))

scare_sound = None

def get_scare_sound():
    global scare_sound
    if scare_sound is None:
        scare_sound = make_scare_sound()
    return scare_sound

class JumpScare:
    """Triggers a jumpscare when fish swims over a hidden scare point"""
    def __init__(self, x, y, scare_type="eye"):
        self.x = x
        self.y = y
        self.type = scare_type
        self.triggered = False
        self.active = False
        self.timer = 0
        self.DURATION = 90
        self.flash_col = random.choice([
            (200, 0, 0), (0, 0, 200), (200, 200, 0)
        ])

    def check(self, fish_x, fish_y, camera_y):
        if self.triggered:
            return False
        sy = self.y - camera_y
        dist = math.sqrt((fish_x - self.x) ** 2 + (fish_y - sy) ** 2)
        if dist < 60:
            self.triggered = True
            self.active = True
            self.timer = self.DURATION
            pygame.mixer.stop()
            get_scare_sound().play()
            return True
        return False

    def update_and_draw(self, screen):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            return

        progress = 1 - (self.timer / self.DURATION)

        if self.type == "eye":
            # Massive eye appears
            if self.timer > 60:
                flash_alpha = min(200, (self.DURATION - self.timer) * 20)
                flash = pygame.Surface((800, 600), pygame.SRCALPHA)
                flash.fill((0, 0, 0, flash_alpha))
                screen.blit(flash, (0, 0))

                eye_size = int(30 + (self.DURATION - self.timer) * 3)
                ex, ey = 400, 300
                pygame.draw.ellipse(screen, (240, 230, 200),
                                    (ex - eye_size, ey - eye_size // 2,
                                     eye_size * 2, eye_size))
                pygame.draw.circle(screen, (20, 60, 20),
                                   (ex, ey), eye_size // 3)
                pygame.draw.circle(screen, (0, 0, 0),
                                   (ex, ey), eye_size // 5)
                pygame.draw.circle(screen, (255, 255, 255),
                                   (ex + eye_size // 8, ey - eye_size // 8),
                                   eye_size // 10)
            else:
                # Fade out
                fade_alpha = int(180 * self.timer / 60)
                flash = pygame.Surface((800, 600), pygame.SRCALPHA)
                flash.fill((0, 0, 0, fade_alpha))
                screen.blit(flash, (0, 0))

        elif self.type == "flash":
            # Screen flash + silhouette
            if self.timer > 70:
                flash_alpha = min(220, (self.DURATION - self.timer) * 30)
                flash = pygame.Surface((800, 600), pygame.SRCALPHA)
                flash.fill((*self.flash_col, flash_alpha))
                screen.blit(flash, (0, 0))

                # Dark creature silhouette
                cx, cy = 400, 300
                sz = int(20 + (self.DURATION - self.timer) * 5)
                pygame.draw.ellipse(screen, (10, 10, 20),
                                    (cx - sz, cy - sz // 2, sz * 2, sz))
                # Tentacles
                for i in range(6):
                    angle = i * math.pi / 3
                    tx = int(cx + sz * math.cos(angle))
                    ty = int(cy + sz // 2 * math.sin(angle))
                    pygame.draw.line(screen, (10, 10, 20),
                                     (cx, cy), (tx + random.randint(-10, 10),
                                                ty + random.randint(-10, 10)), 3)
            else:
                fade_alpha = int(180 * self.timer / 70)
                flash = pygame.Surface((800, 600), pygame.SRCALPHA)
                flash.fill((0, 0, 0, fade_alpha))
                screen.blit(flash, (0, 0))

        elif self.type == "face":
            # Ghostly face
            if self.timer > 50:
                alpha = min(200, (self.DURATION - self.timer) * 15)
                fx, fy = 400, 280
                sz = int(15 + (self.DURATION - self.timer) * 4)
                face_surf = pygame.Surface((sz * 4, sz * 5), pygame.SRCALPHA)
                # Head
                pygame.draw.ellipse(face_surf, (200, 210, 180, alpha),
                                    (0, 0, sz * 4, sz * 5))
                # Eyes
                pygame.draw.ellipse(face_surf, (0, 0, 0, alpha),
                                    (sz, sz, sz, sz + 4))
                pygame.draw.ellipse(face_surf, (0, 0, 0, alpha),
                                    (sz * 2 + 4, sz, sz, sz + 4))
                # Mouth
                pygame.draw.arc(face_surf, (0, 0, 0, alpha),
                                (sz, sz * 3, sz * 2, sz), math.pi, 2 * math.pi, 3)
                screen.blit(face_surf, (fx - sz * 2, fy - sz * 2))
            else:
                fade_alpha = int(160 * self.timer / 50)
                flash = pygame.Surface((800, 600), pygame.SRCALPHA)
                flash.fill((0, 0, 0, fade_alpha))
                screen.blit(flash, (0, 0))


def create_scarespots():
    spots = []
    # Scattered through the Unknown (2500+)
    spots.append(JumpScare(300, 2650, "eye"))
    spots.append(JumpScare(550, 2900, "flash"))
    spots.append(JumpScare(180, 3150, "face"))
    spots.append(JumpScare(620, 3400, "eye"))
    spots.append(JumpScare(380, 3700, "flash"))
    spots.append(JumpScare(250, 4000, "face"))
    spots.append(JumpScare(500, 4300, "eye"))
    return spots
