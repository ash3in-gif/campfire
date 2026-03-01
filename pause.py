import pygame
import sys

def run_pause_menu(screen, clock):
    font_title = pygame.font.SysFont(None, 60)
    font_btn   = pygame.font.SysFont(None, 34)

    btn_w, btn_h = 220, 48
    cx = 400
    buttons = [
        ("▶   Resume",       (cx - btn_w // 2, 260, btn_w, btn_h), "resume"),
        ("↺   Restart",      (cx - btn_w // 2, 325, btn_w, btn_h), "restart"),
        ("⌂   Main Menu",    (cx - btn_w // 2, 390, btn_w, btn_h), "menu"),
        ("✕   Quit Game",    (cx - btn_w // 2, 455, btn_w, btn_h), "quit"),
    ]

    # Darken overlay
    overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
    overlay.fill((0, 10, 30, 180))

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect, action in buttons:
                    if pygame.Rect(rect).collidepoint(mx, my):
                        return action

        screen.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Surface((300, 280), pygame.SRCALPHA)
        panel.fill((0, 30, 60, 200))
        pygame.draw.rect(panel, (0, 140, 200), (0, 0, 300, 280), 2, border_radius=14)
        screen.blit(panel, (250, 230))

        title = font_title.render("PAUSED", True, (160, 220, 255))
        tr = title.get_rect(center=(400, 210))
        screen.blit(title, tr)

        for label, rect, action in buttons:
            hovered = pygame.Rect(rect).collidepoint(mx, my)
            x, y, w, h = rect
            col = (0, 100, 40) if action == "resume" else \
                  (120, 40, 40) if action == "quit" else \
                  (0, 80, 120)
            if hovered:
                col = tuple(min(255, c + 30) for c in col)
            pygame.draw.rect(screen, col, rect, border_radius=10)
            pygame.draw.rect(screen, (100, 180, 220) if hovered else (60, 120, 160),
                             rect, 2, border_radius=10)
            ts = font_btn.render(label, True, (220, 240, 255))
            tr2 = ts.get_rect(center=(x + w // 2, y + h // 2))
            screen.blit(ts, tr2)

        pygame.display.flip()
        clock.tick(60)
