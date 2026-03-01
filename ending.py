import pygame
import sys

def run_ending(screen, clock):
    font_big = pygame.font.SysFont(None, 42)
    font_med = pygame.font.SysFont(None, 30)
    font_small = pygame.font.SysFont(None, 24)

    messages = [
        "You swim back up.",
        "The reef looks the same.",
        "But now you see the net behind the coral.",
        "The fish that aren't there anymore.",
        "The trash disguised as shadow.",
        "The surface didn't change.",
        "You did.",
    ]

    t = 0
    current_msg = 0
    msg_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if current_msg < len(messages) - 1:
                        current_msg += 1
                        msg_timer = 0
                    else:
                        return

        t += 1
        msg_timer += 1

        # Background — muted teal, slowly brightening
        blue = min(120, t // 8)
        screen.fill((0, blue // 2, blue))

        # Light rays from above
        for i in range(4):
            ray_x = (i * 200 + t // 4) % 900 - 50
            ray_surf = pygame.Surface((20, 600), pygame.SRCALPHA)
            ray_surf.fill((150, 220, 200, 15))
            screen.blit(ray_surf, (ray_x, 0))

        # Sandy floor
        pygame.draw.rect(screen, (180, 160, 100), (0, 480, 800, 120))

        # Coral — muted, less vibrant than before
        for cx, cy, c1, c2 in [
            (120, 480, (160, 60, 30), (30, 120, 60)),
            (300, 480, (140, 50, 40), (20, 110, 50)),
            (550, 480, (170, 70, 35), (35, 130, 65)),
            (700, 480, (150, 55, 30), (25, 115, 55)),
        ]:
            pygame.draw.polygon(screen, c1, [
                (cx, cy), (cx - 10, cy + 30), (cx + 10, cy + 30)
            ])
            pygame.draw.polygon(screen, c2, [
                (cx + 14, cy + 5), (cx + 4, cy + 30), (cx + 24, cy + 30)
            ])

        # Hidden trash now visible — plastic bag
        pygame.draw.ellipse(screen, (200, 200, 180), (460, 450, 30, 20))
        pygame.draw.line(screen, (180, 180, 160), (475, 450), (475, 435), 1)

        # Fishing net disguised as shadow
        net_alpha = min(180, t * 2)
        net_surf = pygame.Surface((120, 80), pygame.SRCALPHA)
        for ni in range(5):
            pygame.draw.line(net_surf, (80, 80, 70, net_alpha),
                             (ni * 25, 0), (ni * 25, 80), 1)
        for ni in range(4):
            pygame.draw.line(net_surf, (80, 80, 70, net_alpha),
                             (0, ni * 25), (120, ni * 25), 1)
        screen.blit(net_surf, (180, 410))

        # Empty space where fish should be — just faint outlines
        pygame.draw.ellipse(screen, (60, 100, 90), (580, 350, 20, 10), 1)
        pygame.draw.ellipse(screen, (60, 100, 90), (620, 380, 16, 8), 1)

        # Message box
        alpha = min(255, msg_timer * 6)
        if current_msg < len(messages):
            msg = messages[current_msg]
            # Last message is bigger
            if current_msg == len(messages) - 1:
                msg_surf = font_big.render(msg, True, (240, 255, 240))
            else:
                msg_surf = font_med.render(msg, True, (200, 230, 220))
            msg_surf.set_alpha(alpha)
            msg_rect = msg_surf.get_rect(center=(400, 200))

            # Background box behind text
            box_surf = pygame.Surface((msg_surf.get_width() + 30, msg_surf.get_height() + 20), pygame.SRCALPHA)
            box_surf.fill((0, 0, 0, 120))
            box_surf.set_alpha(alpha)
            screen.blit(box_surf, (msg_rect.x - 15, msg_rect.y - 10))
            screen.blit(msg_surf, msg_rect)

        # Blinking prompt
        if msg_timer > 60 and (t // 40) % 2 == 0:
            if current_msg < len(messages) - 1:
                prompt = font_small.render("Press SPACE to continue", True, (150, 190, 180))
            else:
                prompt = font_small.render("Press SPACE to play again", True, (150, 190, 180))
            prompt_rect = prompt.get_rect(center=(400, 540))
            screen.blit(prompt, prompt_rect)

        pygame.display.flip()
        clock.tick(60)
