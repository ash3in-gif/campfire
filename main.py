import pygame
import sys
import math
import random

from world import generate_world, draw_world, WorldObject
from npcs import create_npcs, update_and_draw_npcs
from sound import update_sound
from titlescreen import run_title_screen, settings
from ending import run_ending
from fish import draw_fish
from death import run_death_screen
from particles import BubbleTrail
from collectibles import create_collectibles, CollectibleDisplay
from jumpscare import create_scarespots
from pause import run_pause_menu
from oxygen import OxygenSystem, OxygenRefill
from enemies import create_enemies_for_map
from gates import Gate
from progression import (MAPS, get_map, save_data, has_upgrade,
                          run_map_complete, run_map_select)

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Below the Blue")
clock = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────────────────────────────
font         = pygame.font.SysFont(None, 26)
small_font   = pygame.font.SysFont(None, 22)
warning_font = pygame.font.SysFont(None, 34)
obj_font     = pygame.font.SysFont(None, 25)

# ── HUD helpers ───────────────────────────────────────────────────────────────
def draw_hud_pill(screen, text, fnt, x, y, text_color=(220, 235, 245)):
    ts = fnt.render(text, True, text_color)
    tw, th = ts.get_width(), ts.get_height()
    pad = 6
    pill = pygame.Surface((tw + pad * 2, th + pad), pygame.SRCALPHA)
    pill.fill((0, 0, 0, 160))
    pygame.draw.rect(pill, (0, 100, 140), (0, 0, tw + pad * 2, th + pad), 1, border_radius=6)
    screen.blit(pill, (x, y))
    screen.blit(ts, (x + pad, y + pad // 2))
    return th + pad + 4

# ── Map objectives ────────────────────────────────────────────────────────────
MAP_OBJECTIVES = {
    1: ["Explore the reef. Talk to the fish.",
        "Find the 3 memories hidden in the reef.",
        "Swim to the exit below."],
    2: ["Enter the Shipwreck Fields.",
        "Avoid the patrol fish — red means danger.",
        "Collect 5 memories to open the gate."],
    3: ["You are in the Trench.",
        "Move SLOWLY. Blind hunters track sound.",
        "Collect 7 memories to go deeper."],
    4: ["The Unknown. Multiple threats.",
        "Oxygen drains fast — find refills.",
        "10 memories open the final gate."],
    5: ["The Origin. One chance.",
        "The ancient creature circles. Do not cross its path.",
        "Find 4 fragments. Learn what started everything."],
}

# ── Oxygen refill placements per map ─────────────────────────────────────────
def create_refills_for_map(map_id):
    refills = []
    if map_id == 1:
        positions = [(180, 300), (500, 450), (320, 550)]
    elif map_id == 2:
        positions = [(200, 400), (600, 650), (350, 900), (480, 1200), (150, 1350)]
    elif map_id == 3:
        positions = [(300, 700), (550, 1000), (200, 1300), (600, 1700), (350, 2100), (480, 2400)]
    elif map_id == 4:
        positions = [(250, 600), (600, 1000), (180, 1500), (500, 2200), (350, 2800), (600, 3400)]
    elif map_id == 5:
        positions = [(300, 800), (550, 1500), (200, 2500), (450, 3500), (380, 4500)]
    else:
        positions = []
    for x, y in positions:
        refills.append(OxygenRefill(x, y, amount=350))
    return refills

# ── Game state ────────────────────────────────────────────────────────────────
current_map_id   = 1
deaths_this_map  = 0

def build_map(map_id):
    """Construct everything for a given map"""
    m = get_map(map_id)
    world   = generate_world()
    npcs    = create_npcs()
    cols    = create_collectibles()
    scares  = create_scarespots() if map_id >= 4 else []
    enemies = create_enemies_for_map(map_id)
    refills = create_refills_for_map(map_id)
    gate    = Gate(m["gate_y"], m["memories_to_gate"]) if m["gate_y"] else None

    oxy = OxygenSystem(m["oxygen_max"])
    if has_upgrade("oxygen"):
        oxy.set_max(int(m["oxygen_max"] * 1.2))

    return {
        "world":   world,
        "npcs":    npcs,
        "cols":    cols,
        "scares":  scares,
        "enemies": enemies,
        "refills": refills,
        "gate":    gate,
        "oxy":     oxy,
        "map":     m,
    }

def reset_state(map_id):
    global camera_y, fish_x, fish_y, velocity_x, velocity_y
    global warned_surface, second_warned_surface
    global bubble_trail, disp
    global warning_text, warning_timer
    global obj_idx, obj_text, obj_timer
    global state

    state = build_map(map_id)
    camera_y = 0
    fish_x, fish_y = WIDTH // 2, 300
    velocity_x = velocity_y = 0
    warned_surface = second_warned_surface = False
    bubble_trail = BubbleTrail()
    disp = CollectibleDisplay()
    warning_text = ""
    warning_timer = 0
    obj_idx  = 0
    obj_text = MAP_OBJECTIVES[map_id][0]
    obj_timer = 300

# Initial build
state = build_map(current_map_id)
camera_y = 0
fish_x, fish_y = WIDTH // 2, 300
velocity_x = velocity_y = 0
warned_surface = second_warned_surface = False
bubble_trail = BubbleTrail()
disp = CollectibleDisplay()
warning_text = ""
warning_timer = 0
obj_idx  = 0
obj_text = MAP_OBJECTIVES[current_map_id][0]
obj_timer = 300

WORLD_HEIGHT_DEFAULT = 5000
dash_cooldown = 0
sonar_timer   = 0

# ── Title + Map select loop (back returns to title) ─────────────────────
while True:
    run_title_screen(screen, clock)
    chosen = run_map_select(screen, clock)
    if chosen:
        current_map_id = chosen
        reset_state(current_map_id)
        break
    # back pressed — loop to title

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_depth_ratio(y, world_h):
    return min(y / world_h, 1.0)

def get_ocean_color(depth):
    if depth < 0.5:
        t2 = depth * 2
        r = max(0, min(255, int(0   + (5  - 0)   * t2)))
        g = max(0, min(255, int(150 + (15 - 150) * t2)))
        b = max(0, min(255, int(200 + (40 - 200) * t2)))
    else:
        t2 = (depth - 0.5) * 2
        r = max(0, min(255, int(5  + (10 - 5)  * t2)))
        g = max(0, min(255, int(15 + (5  - 15) * t2)))
        b = max(0, min(255, int(40 + (15 - 40) * t2)))
    return (r, g, b)

def get_swim_drag(depth):
    drag = 0.92 - depth * 0.06
    if has_upgrade("drain"):
        drag = min(0.94, drag + 0.02)
    return drag

def advance_objective(map_id):
    global obj_idx, obj_text, obj_timer
    objectives = MAP_OBJECTIVES[map_id]
    if obj_idx < len(objectives) - 1:
        obj_idx  += 1
        obj_text  = objectives[obj_idx]
        obj_timer = 300

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:
    m         = state["map"]
    oxy       = state["oxy"]
    gate      = state["gate"]
    WORLD_H   = m["world_height"]
    drain_m   = m["drain_mult"]
    if has_upgrade("drain"):
        drain_m *= 0.7

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                result = run_pause_menu(screen, clock)
                if result == "restart":
                    deaths_this_map += 1
                    reset_state(current_map_id)
                    continue
                elif result == "menu":
                    run_title_screen(screen, clock)
                    chosen = run_map_select(screen, clock)
                    if chosen is None:
                        chosen = current_map_id
                    current_map_id = chosen
                    reset_state(current_map_id)
                    continue
                elif result == "quit":
                    pygame.quit(); sys.exit()
            # Dash
            if event.key == pygame.K_SPACE and has_upgrade("dash") and dash_cooldown <= 0:
                dx = velocity_x / (abs(velocity_x) or 1)
                dy = velocity_y / (abs(velocity_y) or 1)
                velocity_x += dx * 6
                velocity_y += dy * 4
                dash_cooldown = 120
            # Sonar
            if event.key == pygame.K_q and has_upgrade("sonar"):
                sonar_timer = 180

    actual_depth = fish_y + camera_y
    depth = get_depth_ratio(actual_depth, WORLD_H)
    at_surface = actual_depth < 80

    # Update oxygen
    oxy.update(depth * drain_m, at_surface)
    if dash_cooldown > 0:
        dash_cooldown -= 1
    if sonar_timer > 0:
        sonar_timer -= 1

    if settings.get("sfx", True):
        update_sound(depth)

    drag = get_swim_drag(depth)

    # Objective advancement
    if obj_timer > 0:
        obj_timer -= 1
    mem_count = len(disp.collected_items)
    if mem_count >= 1 and obj_idx == 0:
        advance_objective(current_map_id)

    # ── Map complete: reached the exit (past gate, deep enough) ───────────────
    exit_depth = m["gate_y"] if m["gate_y"] else m["depth"] - 50
    if actual_depth > exit_depth and (gate is None or gate.open):
        result = run_map_complete(screen, clock, current_map_id,
                                  mem_count, deaths_this_map)
        deaths_this_map = 0
        if result == "next":
            current_map_id = min(5, current_map_id + 1)
        chosen = run_map_select(screen, clock)
        if chosen is None:
            run_title_screen(screen, clock)
            chosen = run_map_select(screen, clock)
        if chosen:
            current_map_id = chosen
        reset_state(current_map_id)
        continue

    # ── Death by oxygen ───────────────────────────────────────────────────────
    if oxy.dead:
        deaths_this_map += 1
        run_death_screen(screen, clock)
        reset_state(current_map_id)
        continue

    # ── Enemy death ───────────────────────────────────────────────────────────
    fish_speed = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
    caught = False
    for enemy in state["enemies"]:
        if hasattr(enemy, "update"):
            if hasattr(enemy, "hearing_range"):
                enemy.update(fish_x, fish_y, camera_y, fish_speed)
            elif hasattr(enemy, "center_x"):
                enemy.update(fish_x, fish_y, camera_y)
            else:
                enemy.update(fish_x, fish_y, camera_y)
        if enemy.caught:
            caught = True
    if caught:
        deaths_this_map += 1
        run_death_screen(screen, clock)
        reset_state(current_map_id)
        continue

    # ── Input ─────────────────────────────────────────────────────────────────
    keys = pygame.key.get_pressed()
    speed = max(0.2, 0.8 - depth * 0.5)
    if keys[pygame.K_LEFT]:  velocity_x -= speed
    if keys[pygame.K_RIGHT]: velocity_x += speed
    if keys[pygame.K_UP]:    velocity_y -= speed
    if keys[pygame.K_DOWN]:  velocity_y += speed

    velocity_x *= drag
    velocity_y *= drag
    fish_x += velocity_x
    fish_y += velocity_y
    actual_depth = fish_y + camera_y
    

    # ── Gate block ────────────────────────────────────────────────────────────
    if gate:
        gate.update(mem_count)
        if gate.blocks(fish_y, camera_y):
            fish_y = gate.push_fish(fish_y, camera_y)
            velocity_y = min(0, velocity_y)
            remaining = gate.required - mem_count
            warning_text = f"Collect {remaining} more {'memory' if remaining == 1 else 'memories'} to unlock the gate!"
            warning_timer = max(warning_timer, 90)

    # ── Surface boundary ──────────────────────────────────────────────────────
    if actual_depth < 0:
        if not warned_surface:
            fish_y = max(fish_y, -camera_y + 5)
            velocity_y = abs(velocity_y) * 0.5
            warned_surface = True
            warning_text  = "!  You can't go above the surface!"
            warning_timer = 180
        elif not second_warned_surface:
            fish_y = max(fish_y, -camera_y + 5)
            velocity_y = abs(velocity_y) * 0.5
            second_warned_surface = True
            warning_text  = "!!  Last warning! Go up again and you DIE!"
            warning_timer = 180
        else:
            deaths_this_map += 1
            run_death_screen(screen, clock)
            reset_state(current_map_id)
            continue

    # ── Camera ────────────────────────────────────────────────────────────────
    if fish_y > HEIGHT * 0.6:
        camera_y += fish_y - HEIGHT * 0.6
        fish_y = HEIGHT * 0.6
    if fish_y < HEIGHT * 0.4 and camera_y > 0:
        camera_y -= HEIGHT * 0.4 - fish_y
        fish_y = HEIGHT * 0.4
        camera_y = max(camera_y, 0)
    fish_x = max(20, min(WIDTH - 20, fish_x))

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill(get_ocean_color(depth))
    draw_world(screen, state["world"], camera_y, depth)

    # O2 refills
    for rf in state["refills"]:
        rf.update()
        rf.draw(screen, camera_y)
        if sonar_timer > 0:
            # Highlight nearby refills
            sy = rf.y - camera_y
            dist2 = math.sqrt((fish_x - rf.x) ** 2 + (fish_y - sy) ** 2)
            if dist2 < 300 and not rf.collected:
                s = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(s, (100, 220, 255, 80), (10, 10), 10)
                screen.blit(s, (int(rf.x) - 10, int(sy) - 10))
        rf.check_collect(fish_x, fish_y, camera_y, oxy)

    # Gate
    if gate:
        gate.draw(screen, camera_y, mem_count)

    # Collectibles
    for c in state["cols"]:
        c.draw(screen, camera_y)
        if c.check_collect(fish_x, fish_y, camera_y):
            disp.trigger(c.title, c.description)

    # Jump scares
    if actual_depth > 2500:
        for sp in state["scares"]:
            sp.check(fish_x, fish_y, camera_y)

    # NPCs
    update_and_draw_npcs(screen, state["npcs"], camera_y, fish_x, fish_y, font)

    # Enemies
    for enemy in state["enemies"]:
        enemy.draw(screen, camera_y)

    # Bubbles
    bubble_trail.update(fish_x, fish_y, fish_speed)
    bubble_trail.draw(screen)

    # Fish
    draw_fish(screen, fish_x, fish_y, velocity_x, velocity_y, depth)

    # Scares on top
    for sp in state["scares"]:
        sp.update_and_draw(screen)

    # Light rays near surface
    if depth < 0.15:
        ray_alpha = int(30 * (1 - depth / 0.15))
        for i in range(5):
            rx = (i * 180 + pygame.time.get_ticks() // 50) % WIDTH
            rs = pygame.Surface((10, HEIGHT), pygame.SRCALPHA)
            rs.fill((255, 255, 200, ray_alpha))
            screen.blit(rs, (rx, 0))

    # ── HUD ───────────────────────────────────────────────────────────────────
    actual_depth_m = fish_y + camera_y

    if actual_depth_m < 600:
        zone, zcol = "The Reef",      (255, 255, 255)
    elif actual_depth_m < 1500:
        zone, zcol = "The Drop-Off",  (200, 200, 220)
    elif actual_depth_m < 2500:
        zone, zcol = "The Trench",    (160, 160, 190)
    elif actual_depth_m < 5000:
        zone, zcol = "The Unknown",   (120, 120, 170)
    else:
        zone, zcol = "...",            (80, 80, 120)

    hud_y = 14
    if settings.get("show_zone", True):
        h = draw_hud_pill(screen, zone, font, 14, hud_y, zcol)
        hud_y += h
    if settings.get("show_depth", True):
        h = draw_hud_pill(screen, f"Depth: {int(actual_depth_m)}m", small_font, 14, hud_y)
        hud_y += h

    disp.draw_counter(screen, small_font, len(state["cols"]))

    # Map name pill top right
    map_label = f"Map {current_map_id}: {m['name']}"
    draw_hud_pill(screen, map_label, small_font, WIDTH - 260, 14, (160, 210, 230))
    draw_hud_pill(screen, "ESC — Pause", small_font, WIDTH - 130, 36)

    # Upgrade hints
    if has_upgrade("dash"):
        draw_hud_pill(screen, "SPACE — Dash", small_font, WIDTH - 148, 58, (180, 240, 180))
    if has_upgrade("sonar"):
        draw_hud_pill(screen, "Q — Sonar", small_font, WIDTH - 120, 80, (180, 220, 255))

    # Oxygen bar
    oxy.draw(screen)

    # Objective bar
    if obj_timer > 0:
        if obj_timer > 270:
            oa = int(255 * (300 - obj_timer) / 30)
        elif obj_timer < 60:
            oa = int(255 * obj_timer / 60)
        else:
            oa = 255
        ots = obj_font.render(f">  {obj_text}", True, (200, 230, 215))
        ow = ots.get_width()
        oh = ots.get_height()
        ox2 = WIDTH // 2 - ow // 2
        oy2 = HEIGHT - 40
        pad = 8
        pill = pygame.Surface((ow + pad * 2, oh + pad), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 160))
        pygame.draw.rect(pill, (0, 120, 140), (0, 0, ow + pad * 2, oh + pad), 1, border_radius=8)
        pill.set_alpha(oa)
        ots.set_alpha(oa)
        screen.blit(pill, (ox2 - pad, oy2 - pad // 2))
        screen.blit(ots, (ox2, oy2))

    # Collectible popup
    disp.update_and_draw(screen)

    # Warning
    if warning_timer > 0:
        warning_timer -= 1
        wa = min(255, warning_timer * 4) if warning_timer < 60 else 255
        # colour: red=second surface warning, yellow=first surface, cyan=gate
        if '!!' in warning_text or 'DIE' in warning_text:
            wc = (255, 60, 60)
        elif 'above' in warning_text:
            wc = (255, 200, 50)
        else:
            wc = (0, 220, 180)
        ws = warning_font.render(warning_text, True, wc)
        wb = pygame.Surface((ws.get_width() + 24, ws.get_height() + 16), pygame.SRCALPHA)
        wb.fill((0, 0, 0, 160))
        wb.set_alpha(wa); ws.set_alpha(wa)
        wx = WIDTH // 2 - wb.get_width() // 2
        wy = HEIGHT // 2 - 60
        screen.blit(wb, (wx, wy))
        screen.blit(ws, (wx + 12, wy + 8))

    pygame.display.flip()
    clock.tick(60)
