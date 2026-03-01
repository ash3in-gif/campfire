import pygame
import sys
import numpy as np

def make_spooky_tone(freq, duration, volume=0.3):
    sample_rate = 44100
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames, False)
    # Combine sine waves for an eerie sound
    wave = (np.sin(2 * np.pi * freq * t) * 0.5 +
            np.sin(2 * np.pi * freq * 1.5 * t) * 0.3 +
            np.sin(2 * np.pi * freq * 0.5 * t) * 0.2)
    # Tremolo effect
    tremolo = 0.7 + 0.3 * np.sin(2 * np.pi * 6 * t)
    wave *= tremolo
    fade = int(sample_rate * 0.2)
    wave[:fade] *= np.linspace(0, 1, fade)
    wave[-fade:] *= np.linspace(1, 0, fade)
    wave = (wave * 32767 * volume).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

def run_death_screen(screen, clock):
    font_big = pygame.font.SysFont(None, 80)
    font_med = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)

    # Stop all currently playing sounds
    pygame.mixer.stop()

    # Generate spooky tones
    spooky_notes = [
        make_spooky_tone(110, 2.0, 0.25),
        make_spooky_tone(98,  2.5, 0.20),
        make_spooky_tone(82,  3.0, 0.22),
        make_spooky_tone(73,  2.0, 0.18),
    ]

    # Blood particles
    blood = []
    for i in range(60):
        import random
        angle = random.uniform(0, 6.28)
        speed = random.uniform(1, 5)
        blood.append({
            'x': 400.0, 'y': 300.0,
            'vx': speed * __import__('math').cos(angle),
            'vy': speed * __import__('math').sin(angle),
            'r': random.randint(8, 18),
            'alpha': 255
        })

    t = 0
    note_idx = 0
    last_note = -999
    note_interval = 90

    # Play first note immediately
    spooky_notes[0].play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return

        t += 1

        # Cycle spooky notes
        if t - last_note > note_interval:
            note_idx = (note_idx + 1) % len(spooky_notes)
            spooky_notes[note_idx].play()
            last_note = t
            note_interval = 80 + (note_idx * 20)

        # Dark red background
        bg_r = min(40, t // 3)
        screen.fill((bg_r, 0, 0))

        # Update and draw blood
        for drop in blood:
            drop['x'] += drop['vx']
            drop['y'] += drop['vy']
            drop['vy'] += 0.1  # gravity
            drop['vx'] *= 0.98
            drop['alpha'] = max(80, drop['alpha'] - 0.3)
            r = max(3, drop['r'] - t // 120)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 0, 0, int(drop['alpha'])), (r, r), r)
            screen.blit(s, (int(drop['x']) - r, int(drop['y']) - r))

        # Dead fish body — on its side
        fish_x, fish_y = 400, 300
        pygame.draw.ellipse(screen, (180, 120, 20),
                            (fish_x - 30, fish_y - 10, 60, 20))
        # Tail flopped down
        pygame.draw.polygon(screen, (160, 100, 10), [
            (fish_x - 30, fish_y + 5),
            (fish_x - 48, fish_y + 18),
            (fish_x - 48, fish_y - 4),
        ])
        # Fin drooping
        pygame.draw.polygon(screen, (160, 100, 10), [
            (fish_x - 10, fish_y - 10),
            (fish_x + 5,  fish_y - 10),
            (fish_x,      fish_y - 22),
        ])
        # Dead X eyes
        eye_x, eye_y = fish_x + 18, fish_y - 3
        pygame.draw.line(screen, (30, 30, 30),
                         (eye_x - 4, eye_y - 4), (eye_x + 4, eye_y + 4), 2)
        pygame.draw.line(screen, (30, 30, 30),
                         (eye_x + 4, eye_y - 4), (eye_x - 4, eye_y + 4), 2)

        # Knife — stabbed through the fish
        knife_wobble = __import__('math').sin(t * 0.05) * 2
        kx, ky = fish_x + 5, int(fish_y - 50 + knife_wobble)
        # Handle
        pygame.draw.rect(screen, (80, 50, 20), (kx - 5, ky - 20, 10, 20))
        pygame.draw.rect(screen, (60, 35, 10), (kx - 7, ky - 22, 14, 5))
        # Blade
        pygame.draw.polygon(screen, (200, 200, 210), [
            (kx - 3, ky),
            (kx + 3, ky),
            (kx + 1, ky + 40),
            (kx - 1, ky + 40),
        ])
        # Blade shine
        pygame.draw.line(screen, (240, 240, 255),
                         (kx + 1, ky + 2), (kx + 1, ky + 35), 1)
        # Blood on blade
        pygame.draw.polygon(screen, (160, 0, 0), [
            (kx - 3, ky + 20),
            (kx + 3, ky + 20),
            (kx + 2, ky + 38),
            (kx - 2, ky + 38),
        ])

        # Text
        alpha = min(255, t * 4)

        title_surf = font_big.render("YOU DIED", True, (220, 30, 30))
        title_surf.set_alpha(alpha)
        title_rect = title_surf.get_rect(center=(400, 160))
        screen.blit(title_surf, title_rect)

        sub_surf = font_med.render("The fisherman was waiting.", True, (180, 100, 100))
        sub_surf.set_alpha(min(255, max(0, (t - 30) * 4)))
        sub_rect = sub_surf.get_rect(center=(400, 460))
        screen.blit(sub_surf, sub_rect)

        if t > 80 and (t // 40) % 2 == 0:
            prompt = font_small.render("Press SPACE to try again", True, (140, 60, 60))
            prompt_rect = prompt.get_rect(center=(400, 530))
            screen.blit(prompt, prompt_rect)

        pygame.display.flip()
        clock.tick(60)
