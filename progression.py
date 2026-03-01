import pygame
import sys
import math

# ── Map definitions ───────────────────────────────────────────────────────────

MAPS = [
    {
        "id": 1,
        "name": "The Coral Reef",
        "subtitle": "Where it all begins.",
        "depth": 600,
        "world_height": 800,
        "oxygen_max": 2400,       # generous
        "drain_mult": 0.6,
        "memories_to_gate": 3,
        "gate_y": 580,
        "color_surface": (0, 160, 210),
        "color_deep": (0, 80, 140),
        "enemy_ids": [],
        "unlock_requires": 0,     # always unlocked
        "description": [
            "Your first dive.",
            "Collect 3 memories to open the exit.",
            "No threats. Learn the controls.",
        ],
    },
    {
        "id": 2,
        "name": "The Shipwreck Fields",
        "subtitle": "Something sank here.",
        "depth": 1500,
        "world_height": 1800,
        "oxygen_max": 2000,
        "drain_mult": 0.9,
        "memories_to_gate": 5,
        "gate_y": 1400,
        "color_surface": (0, 120, 170),
        "color_deep": (10, 40, 80),
        "enemy_ids": [2],
        "unlock_requires": 1,
        "description": [
            "Patrol fish guard these waters.",
            "Collect 5 memories to pass the gate.",
            "Stay out of the red zone.",
        ],
    },
    {
        "id": 3,
        "name": "The Trench",
        "subtitle": "Darkness has ears.",
        "depth": 2500,
        "world_height": 3000,
        "oxygen_max": 1800,
        "drain_mult": 1.2,
        "memories_to_gate": 7,
        "gate_y": 2600,
        "color_surface": (0, 60, 100),
        "color_deep": (5, 15, 35),
        "enemy_ids": [3],
        "unlock_requires": 2,
        "description": [
            "Blind hunters patrol the dark.",
            "Move slowly - they hunt by sound.",
            "Collect 7 memories to proceed.",
        ],
    },
    {
        "id": 4,
        "name": "The Unknown",
        "subtitle": "You were warned.",
        "depth": 4000,
        "world_height": 4500,
        "oxygen_max": 1500,
        "drain_mult": 1.6,
        "memories_to_gate": 10,
        "gate_y": 4000,
        "color_surface": (0, 20, 50),
        "color_deep": (5, 5, 20),
        "enemy_ids": [4],
        "unlock_requires": 3,
        "description": [
            "Multiple threats. Jump scares.",
            "Oxygen drains fast under pressure.",
            "10 memories open the final path.",
        ],
    },
    {
        "id": 5,
        "name": "The Origin",
        "subtitle": "The truth lives here.",
        "depth": 5000,
        "world_height": 5500,
        "oxygen_max": 1200,
        "drain_mult": 2.0,
        "memories_to_gate": 4,
        "gate_y": 5000,
        "color_surface": (0, 5, 20),
        "color_deep": (2, 2, 10),
        "enemy_ids": [5],
        "unlock_requires": 4,
        "description": [
            "One ancient creature circles.",
            "Find 4 fragments. Learn the origin.",
            "Running out of air here is instant death.",
        ],
    },
]

UPGRADES = [
    {"name": "Bigger Tank",     "desc": "+20% oxygen capacity",  "stat": "oxygen",  "value": 1.2},
    {"name": "Speed Burst",     "desc": "SPACE to dash forward", "stat": "dash",    "value": 1},
    {"name": "Sonar Ping",      "desc": "Q reveals O₂ nearby",  "stat": "sonar",   "value": 1},
    {"name": "Pressure Suit",   "desc": "-30% oxygen drain",     "stat": "drain",   "value": 0.7},
]


def get_map(map_id):
    for m in MAPS:
        if m["id"] == map_id:
            return m
    return MAPS[0]


# ── Save state (in-memory, resets on quit) ────────────────────────────────────

save_data = {
    "maps_unlocked": 1,   # highest map unlocked
    "upgrades": [],       # list of upgrade stat names acquired
}


def unlock_next_map():
    if save_data["maps_unlocked"] < 5:
        save_data["maps_unlocked"] += 1


def add_upgrade(upgrade):
    if upgrade["stat"] not in save_data["upgrades"]:
        save_data["upgrades"].append(upgrade["stat"])


def has_upgrade(stat):
    return stat in save_data["upgrades"]


# ── Map complete screen ────────────────────────────────────────────────────────

def run_map_complete(screen, clock, map_id, memories_collected, deaths):
    font_big   = pygame.font.SysFont(None, 62)
    font_med   = pygame.font.SysFont(None, 34)
    font_small = pygame.font.SysFont(None, 26)
    font_btn   = pygame.font.SysFont(None, 30)

    # Unlock next map
    if map_id >= save_data["maps_unlocked"]:
        unlock_next_map()

    # Pick upgrade to offer (one per map, not already owned)
    offered_upgrade = None
    for upg in UPGRADES:
        if upg["stat"] not in save_data["upgrades"]:
            offered_upgrade = upg
            break

    t = 0
    btn_w, btn_h = 220, 46
    continue_rect = (290, 480, btn_w, btn_h)
    menu_rect     = (290, 536, btn_w, btn_h)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(continue_rect).collidepoint(mx, my):
                    if offered_upgrade:
                        add_upgrade(offered_upgrade)
                    return "next"
                if pygame.Rect(menu_rect).collidepoint(mx, my):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if offered_upgrade:
                        add_upgrade(offered_upgrade)
                    return "next"

        t += 1
        # Background
        blue = min(60, t // 4)
        screen.fill((0, blue // 2, blue))

        # Light rays
        for i in range(4):
            rx = (i * 200 + t // 4) % 900 - 50
            rs = pygame.Surface((18, 600), pygame.SRCALPHA)
            rs.fill((100, 200, 180, 12))
            screen.blit(rs, (rx, 0))

        alpha = min(255, t * 5)

        title = font_big.render("DIVE COMPLETE", True, (100, 220, 200))
        title.set_alpha(alpha)
        screen.blit(title, title.get_rect(center=(400, 100)))

        m = get_map(map_id)
        sub = font_med.render(m["name"], True, (160, 210, 230))
        sub.set_alpha(alpha)
        screen.blit(sub, sub.get_rect(center=(400, 155)))

        # Stats
        stats = [
            f"Memories collected:  {memories_collected}",
            f"Times caught:        {deaths}",
        ]
        for i, s in enumerate(stats):
            ts = font_small.render(s, True, (180, 220, 215))
            ts.set_alpha(min(255, max(0, (t - 20) * 5)))
            screen.blit(ts, ts.get_rect(center=(400, 220 + i * 32)))

        # Upgrade offer
        if offered_upgrade:
            uy = 310
            box = pygame.Surface((340, 90), pygame.SRCALPHA)
            box.fill((0, 40, 60, 180))
            pygame.draw.rect(box, (0, 160, 140), (0, 0, 340, 90), 2, border_radius=10)
            box.set_alpha(min(255, max(0, (t - 30) * 5)))
            screen.blit(box, (230, uy))

            ut = font_med.render("  Upgrade Unlocked!", True, (100, 240, 200))
            ut.set_alpha(min(255, max(0, (t - 30) * 5)))
            screen.blit(ut, ut.get_rect(center=(400, uy + 22)))

            un = font_small.render(f"{offered_upgrade['name']} - {offered_upgrade['desc']}",
                                   True, (180, 230, 220))
            un.set_alpha(min(255, max(0, (t - 30) * 5)))
            screen.blit(un, un.get_rect(center=(400, uy + 58)))

        # Buttons
        for rect, label, col in [
            (continue_rect, ">  Next Dive", (0, 120, 80)),
            (menu_rect,     "[M]  Map Select", (0, 80, 120)),
        ]:
            hovered = pygame.Rect(rect).collidepoint(mx, my)
            c = tuple(min(255, v + 25) for v in col) if hovered else col
            pygame.draw.rect(screen, c, rect, border_radius=10)
            pygame.draw.rect(screen, (100, 200, 180), rect, 2, border_radius=10)
            ts = font_btn.render(label, True, (220, 245, 240))
            screen.blit(ts, ts.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)))

        pygame.display.flip()
        clock.tick(60)


# ── Map select screen ─────────────────────────────────────────────────────────


def run_map_select(screen, clock):
    font_title = pygame.font.SysFont(None, 56)
    font_name  = pygame.font.SysFont(None, 32)
    font_sub   = pygame.font.SysFont(None, 24)
    font_desc  = pygame.font.SysFont(None, 22)
    font_btn   = pygame.font.SysFont(None, 28)

    selected = 0
    t = 0
    back_rect = pygame.Rect(30, 540, 150, 44)
    play_rect = pygame.Rect(500, 455, 180, 76)

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_RIGHT:
                    selected = min(4, selected + 1)
                if event.key == pygame.K_RETURN:
                    if MAPS[selected]["id"] <= save_data["maps_unlocked"]:
                        return MAPS[selected]["id"]

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Back button
                if back_rect.collidepoint(mx, my):
                    return None
                # Play button
                if play_rect.collidepoint(mx, my):
                    if MAPS[selected]["id"] <= save_data["maps_unlocked"]:
                        return MAPS[selected]["id"]
                # Card click - just select, don't launch
                for i in range(5):
                    card_rect = pygame.Rect(80 + i * 130, 100, 110, 340)
                    if card_rect.collidepoint(mx, my):
                        if MAPS[i]["id"] <= save_data["maps_unlocked"]:
                            selected = i

        t += 1

        # Background
        screen.fill((0, 15, 40))
        for i in range(5):
            rx = (i * 180 + t // 5) % 900 - 50
            rs = pygame.Surface((16, 600), pygame.SRCALPHA)
            rs.fill((60, 130, 220, 10))
            screen.blit(rs, (rx, 0))

        title = font_title.render("Select Your Dive", True, (160, 220, 255))
        screen.blit(title, title.get_rect(center=(400, 50)))

        # Map cards
        for i, m in enumerate(MAPS):
            unlocked = m["id"] <= save_data["maps_unlocked"]
            card_x = 80 + i * 130
            is_sel = i == selected

            card_col   = (0, 40, 70)   if unlocked else (20, 20, 30)
            border_col = (0, 180, 160) if is_sel else ((0, 100, 120) if unlocked else (40, 40, 50))
            card = pygame.Surface((110, 340), pygame.SRCALPHA)
            card.fill((*card_col, 210))
            pygame.draw.rect(card, border_col, (0, 0, 110, 340), 2, border_radius=10)
            if is_sel:
                glow_s = pygame.Surface((110, 340), pygame.SRCALPHA)
                pygame.draw.rect(glow_s, (0, 180, 160, 30), (0, 0, 110, 340), border_radius=10)
                card.blit(glow_s, (0, 0))
            screen.blit(card, (card_x, 100))

            depth_col = (0, 160, 140) if unlocked else (60, 60, 60)
            ds = font_sub.render(f"{m['depth']}m", True, depth_col)
            screen.blit(ds, (card_x + 55 - ds.get_width() // 2, 115))

            num_col = (100, 200, 220) if unlocked else (60, 60, 70)
            ns = font_name.render(f"#{m['id']}", True, num_col)
            screen.blit(ns, (card_x + 55 - ns.get_width() // 2, 140))

            if not unlocked:
                ls = font_name.render("[LOCKED]", True, (80, 80, 90))
                screen.blit(ls, (card_x + 55 - ls.get_width() // 2, 175))
            else:
                ny = 170
                for word in m["name"].split():
                    ws = font_desc.render(word, True, (180, 220, 230))
                    screen.blit(ws, (card_x + 55 - ws.get_width() // 2, ny))
                    ny += 22

            if unlocked and m["enemy_ids"]:
                threat = font_desc.render("! Threats", True, (200, 100, 80))
                screen.blit(threat, (card_x + 55 - threat.get_width() // 2, 380))

        # Detail panel
        m = MAPS[selected]
        unlocked = m["id"] <= save_data["maps_unlocked"]
        panel = pygame.Surface((600, 90), pygame.SRCALPHA)
        panel.fill((0, 20, 50, 200))
        pygame.draw.rect(panel, (0, 120, 140), (0, 0, 600, 90), 1, border_radius=8)
        screen.blit(panel, (100, 450))

        screen.blit(font_name.render(m["name"],     True, (160, 230, 255)), (115, 458))
        screen.blit(font_sub.render(m["subtitle"],  True, (120, 180, 200)), (115, 486))

        if unlocked:
            for di, dl in enumerate(m["description"][:2]):
                ds2 = font_desc.render(dl, True, (140, 190, 200))
                screen.blit(ds2, (115 + (di % 2) * 280, 508))

            # Play button
            ph = play_rect.collidepoint(mx, my)
            pygame.draw.rect(screen, (0, 170, 100) if ph else (0, 140, 80),
                             play_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 200, 140), play_rect, 2, border_radius=10)
            pts = font_btn.render(">  Dive In", True, (220, 255, 240))
            screen.blit(pts, pts.get_rect(center=play_rect.center))

        # Back button
        bh = back_rect.collidepoint(mx, my)
        pygame.draw.rect(screen, (0, 80, 130) if bh else (0, 60, 100),
                         back_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 120, 160), back_rect, 1, border_radius=8)
        bs2 = font_btn.render("<  Back", True, (180, 220, 240))
        screen.blit(bs2, bs2.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)
