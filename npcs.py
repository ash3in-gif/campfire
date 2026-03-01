import pygame

class NPC:
    def __init__(self, x, y, dialogue, color=(255, 220, 100), name=""):
        self.x = x
        self.y = y
        self.dialogue = dialogue
        self.color = color
        self.name = name
        self.talking = False

def create_npcs():
    npcs = []

    # ── THE REEF ──────────────────────────────────────────────────────────────
    npcs.append(NPC(160, 180, "Welcome to the reef, little one. Isn't it beautiful here?",
                    (255, 200, 80), "Elder Finn"))
    npcs.append(NPC(420, 220, "I was born here. I'll die here. The reef is all there is.",
                    (100, 220, 255), "Coral"))
    npcs.append(NPC(620, 290, "They say the deep ones glow. I think that's just a story.",
                    (180, 255, 120), "Spark"))
    npcs.append(NPC(280, 400, "Your mother said not to go past the rocks. She meant it.",
                    (255, 160, 100), "Aunt Eel"))
    npcs.append(NPC(520, 450, "I went to the drop-off once. Just once. Don't ask what I saw.",
                    (200, 200, 255), "Old Grouper"))

    # ── THE DROP-OFF ─────────────────────────────────────────────────────────
    npcs.append(NPC(200, 750, "...", (120, 120, 140), ""))
    npcs.append(NPC(560, 850, "Turn back. There is nothing here worth knowing.",
                    (110, 110, 130), "Pale Snapper"))
    npcs.append(NPC(340, 1000, "The nets come from above. They don't know we're here.",
                    (100, 100, 120), "Grey Fish"))
    npcs.append(NPC(480, 1180, "This ship fell from their world into ours. They never came back for it.",
                    (90, 90, 110), "Wreck Dweller"))
    npcs.append(NPC(200, 1380, "...", (80, 80, 100), ""))

    # ── THE TRENCH ────────────────────────────────────────────────────────────
    npcs.append(NPC(350, 1600, "You are the first young one to come this deep. Why?",
                    (60, 160, 190), "Deep Elder"))
    npcs.append(NPC(580, 1850, "The surface world is warm. Warming. They don't notice.",
                    (50, 140, 170), "Vent Fish"))
    npcs.append(NPC(200, 2050, "We watched their boats for centuries. Then the nets came. Then silence.",
                    (40, 120, 150), "The Ancient"))
    npcs.append(NPC(450, 2300, "The reef you know is already half of what it was. Ask Elder Finn.",
                    (30, 100, 130), "Truth Keeper"))

    # ── THE UNKNOWN ────────────────────────────────────────────────────────────
    npcs.append(NPC(300, 2700,
                    "You should not be here. Neither should I. Yet here we are.",
                    (0, 80, 60), "Void Dweller"))
    npcs.append(NPC(550, 3000,
                    "The signals started 40 years ago. We don't know what sends them.",
                    (0, 60, 80), "Signal Fish"))
    npcs.append(NPC(180, 3300,
                    "Time is different here. The pressure makes everything slow.",
                    (10, 40, 60), "Pale Form"))
    npcs.append(NPC(620, 3600,
                    "Go back. Tell them what you've seen. That is all we ask.",
                    (0, 50, 40), "The Last One"))
    npcs.append(NPC(380, 4000,
                    "...",
                    (5, 5, 15), ""))
    npcs.append(NPC(200, 4400,
                    "We have been here since before the reef. We will be here after.",
                    (0, 30, 30), "Origin"))

    return npcs


def draw_dialogue_box(screen, text, name, npc_x, npc_screen_y, font):
    padding = 10
    max_width = 240

    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test = current_line + (" " if current_line else "") + word
        if font.size(test)[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    line_height = font.get_height() + 4
    box_w = max(font.size(l)[0] for l in lines) + padding * 2
    if name:
        name_font = pygame.font.SysFont(None, 22)
        box_w = max(box_w, name_font.size(name)[0] + padding * 2)
    box_h = line_height * len(lines) + padding * 2 + (18 if name else 0)

    box_x = npc_x - box_w // 2
    box_x = max(5, min(800 - box_w - 5, box_x))
    box_y = npc_screen_y - box_h - 22
    box_y = max(5, box_y)

    box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box_surf.fill((0, 0, 0, 185))
    screen.blit(box_surf, (box_x, box_y))
    pygame.draw.rect(screen, (100, 180, 220), (box_x, box_y, box_w, box_h), 1)

    offset = 0
    if name:
        name_font = pygame.font.SysFont(None, 22)
        ns = name_font.render(name, True, (120, 200, 240))
        screen.blit(ns, (box_x + padding, box_y + padding))
        offset = 18

    for i, line in enumerate(lines):
        text_surf = font.render(line, True, (230, 240, 245))
        screen.blit(text_surf, (box_x + padding, box_y + padding + offset + i * line_height))


def update_and_draw_npcs(screen, npcs, camera_y, fish_x, fish_y, font):
    for npc in npcs:
        screen_y = int(npc.y - camera_y)
        if screen_y < -50 or screen_y > 700:
            continue

        pygame.draw.ellipse(screen, npc.color,
                            (npc.x - 12, screen_y - 7, 24, 14))
        pygame.draw.polygon(screen, npc.color, [
            (npc.x - 12, screen_y),
            (npc.x - 22, screen_y - 6),
            (npc.x - 22, screen_y + 6)
        ])
        pygame.draw.circle(screen, (0, 0, 0), (npc.x + 5, screen_y - 1), 2)

        dist = ((fish_x - npc.x) ** 2 + (fish_y - screen_y) ** 2) ** 0.5
        if dist < 80:
            draw_dialogue_box(screen, npc.dialogue, npc.name, npc.x, screen_y, font)
