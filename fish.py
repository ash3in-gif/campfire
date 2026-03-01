import pygame
import math

def draw_fish(screen, x, y, velocity_x, velocity_y, depth):
    t = pygame.time.get_ticks()

    # Is the fish moving?
    speed = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
    is_moving = speed > 0.3

    # Angle based on velocity — tilt up/down
    if is_moving:
        angle = math.degrees(math.atan2(-velocity_y, abs(velocity_x)))
        angle = max(-35, min(35, angle))  # clamp tilt
    else:
        angle = 0  # idle — level

    # Tail wag — faster when moving, slow idle drift when still
    if is_moving:
        wag = math.sin(t * 0.01) * 8
    else:
        wag = math.sin(t * 0.003) * 3

    # Facing direction
    facing_left = velocity_x < -0.1 if is_moving else False

    # Colors
    body_r = max(0, min(255, int(255 - depth * 200)))
    body_g = max(0, min(255, int(180 - depth * 160)))
    body_b = max(0, min(255, int(20 + depth * 100)))
    body_color = (body_r, body_g, body_b)

    fin_r = max(0, min(255, body_r - 50))
    fin_g = max(0, min(255, body_g - 30))
    fin_b = max(0, min(255, body_b + 20))
    fin_color = (fin_r, fin_g, fin_b)

    stripe_r = max(0, min(255, body_r - 80))
    stripe_g = max(0, min(255, body_g - 60))
    stripe_b = max(0, min(255, body_b + 30))
    stripe_color = (stripe_r, stripe_g, stripe_b)

    # Build fish surface (larger — 80x60)
    fish_surf = pygame.Surface((80, 60), pygame.SRCALPHA)
    cx, cy = 40, 30  # center of fish surface

    # --- Tail ---
    tail_wag = int(wag)
    pygame.draw.polygon(fish_surf, fin_color, [
        (cx - 20, cy + tail_wag),
        (cx - 38, cy - 14 + tail_wag),
        (cx - 38, cy + 14 + tail_wag),
    ])
    # Tail detail lines
    pygame.draw.line(fish_surf, stripe_color,
                     (cx - 20, cy + tail_wag),
                     (cx - 35, cy - 10 + tail_wag), 1)
    pygame.draw.line(fish_surf, stripe_color,
                     (cx - 20, cy + tail_wag),
                     (cx - 35, cy + 10 + tail_wag), 1)

    # --- Body ---
    pygame.draw.ellipse(fish_surf, body_color, (cx - 18, cy - 12, 38, 24))

    # --- Stripes ---
    pygame.draw.line(fish_surf, stripe_color,
                     (cx - 2, cy - 11), (cx - 2, cy + 11), 2)
    pygame.draw.line(fish_surf, stripe_color,
                     (cx + 6, cy - 10), (cx + 6, cy + 10), 2)

    # --- Pectoral fin (side fin) ---
    pygame.draw.polygon(fish_surf, fin_color, [
        (cx + 2, cy + 2),
        (cx - 8, cy + 14),
        (cx + 10, cy + 12),
    ])

    # --- Dorsal fin (top fin) ---
    pygame.draw.polygon(fish_surf, fin_color, [
        (cx - 6, cy - 12),
        (cx + 6, cy - 12),
        (cx + 10, cy - 22),
        (cx - 2, cy - 24),
        (cx - 10, cy - 18),
    ])
    # Dorsal fin rays
    pygame.draw.line(fish_surf, stripe_color,
                     (cx - 4, cy - 12), (cx - 6, cy - 20), 1)
    pygame.draw.line(fish_surf, stripe_color,
                     (cx + 2, cy - 12), (cx + 4, cy - 22), 1)

    # --- Anal fin (bottom fin) ---
    pygame.draw.polygon(fish_surf, fin_color, [
        (cx - 4, cy + 12),
        (cx + 4, cy + 12),
        (cx, cy + 20),
    ])

    # --- Eye ---
    pygame.draw.circle(fish_surf, (255, 255, 220), (cx + 15, cy - 3), 5)
    pygame.draw.circle(fish_surf, (20, 20, 30), (cx + 16, cy - 3), 3)
    pygame.draw.circle(fish_surf, (255, 255, 255), (cx + 17, cy - 4), 1)

    # --- Mouth ---
    pygame.draw.arc(fish_surf, (30, 20, 20),
                    (cx + 18, cy + 1, 8, 6), 3.3, 5.0, 2)

    # --- Gill line ---
    pygame.draw.arc(fish_surf, stripe_color,
                    (cx + 4, cy - 10, 14, 20), 1.8, 4.5, 2)

    # --- Lip detail ---
    pygame.draw.circle(fish_surf, (body_r, max(0, body_g - 20), body_b),
                       (cx + 20, cy + 2), 3)

    # Flip if facing left
    if facing_left:
        fish_surf = pygame.transform.flip(fish_surf, True, False)
        rot_angle = -angle
    else:
        rot_angle = angle

    # Rotate for tilt
    rotated = pygame.transform.rotate(fish_surf, rot_angle)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)