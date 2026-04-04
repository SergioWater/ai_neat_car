"""
CHECKPOINT PLACEMENT TOOL
=========================
Run this script. It opens your map in a window.
Click on the road in DRIVING ORDER to place checkpoints.

Controls:
  LEFT CLICK  = place a checkpoint
  RIGHT CLICK = undo last checkpoint
  S           = save and quit
  Q           = quit without saving

It saves the coordinates to checkpoints.txt and prints them
in the format you can paste directly into newcar.py.
"""
import pygame
import sys

pygame.init()

# Load the map
track_image = pygame.image.load('map3.png')
MAP_W, MAP_H = track_image.get_size()  # 1920 x 1080

# Scale to fit screen (80% of screen width)
info = pygame.display.Info()
TARGET_W = int(info.current_w * 0.8)
SCALE = TARGET_W / MAP_W
WIN_W = int(MAP_W * SCALE)
WIN_H = int(MAP_H * SCALE)

screen = pygame.display.set_mode((WIN_W, WIN_H))
track_image = track_image.convert()
pygame.display.set_caption("Click on the road to place checkpoints (S = save, Q = quit)")

scaled_track = pygame.transform.scale(track_image, (WIN_W, WIN_H))

checkpoints = []  # stores (x, y) in ORIGINAL 1920x1080 coordinates

font = pygame.font.SysFont("Arial", int(18 * SCALE))
font_big = pygame.font.SysFont("Arial", int(24 * SCALE))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if event.button == 1:  # LEFT CLICK = place checkpoint
                # Convert screen coords back to 1920x1080
                orig_x = int(mx / SCALE)
                orig_y = int(my / SCALE)
                checkpoints.append((orig_x, orig_y))
                print(f"  Checkpoint {len(checkpoints)-1}: ({orig_x}, {orig_y})")

            elif event.button == 3:  # RIGHT CLICK = undo
                if checkpoints:
                    removed = checkpoints.pop()
                    print(f"  Removed checkpoint: {removed}")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                # Save and quit
                print("\n--- SAVE ---")
                print(f"Total checkpoints: {len(checkpoints)}\n")

                # Save to file
                with open("checkpoints.txt", "w") as f:
                    for i, (cx, cy) in enumerate(checkpoints):
                        f.write(f"{cx},{cy}\n")

                # Print in code format
                print("# Paste this into newcar.py:")
                print("CHECKPOINTS_1920 = [")
                for i, (cx, cy) in enumerate(checkpoints):
                    print(f"    ({cx}, {cy}),    # {i}")
                print("]")

                running = False

            elif event.key == pygame.K_q:
                print("Quit without saving.")
                running = False

    # Draw
    screen.blit(scaled_track, (0, 0))

    # Draw placed checkpoints
    for i, (cx, cy) in enumerate(checkpoints):
        # Convert to screen coords
        sx = int(cx * SCALE)
        sy = int(cy * SCALE)

        # Connecting line to previous
        if i > 0:
            px, py = checkpoints[i-1]
            pygame.draw.line(screen, (255, 200, 0), (int(px*SCALE), int(py*SCALE)), (sx, sy), 2)

        # Circle
        if i == 0:
            color = (0, 220, 100)  # green for start
        else:
            color = (255, 180, 0)  # gold

        pygame.draw.circle(screen, color, (sx, sy), int(12 * SCALE))
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), int(12 * SCALE), 2)

        # Number
        text = font.render(str(i), True, (0, 0, 0))
        text_rect = text.get_rect(center=(sx, sy))
        screen.blit(text, text_rect)

    # Instructions
    instr = font_big.render(
        f"Checkpoints: {len(checkpoints)}  |  LEFT CLICK = place  |  RIGHT CLICK = undo  |  S = save  |  Q = quit",
        True, (255, 255, 255)
    )
    # Dark background for text
    bg_rect = instr.get_rect(topleft=(10, 10))
    bg_surface = pygame.Surface((bg_rect.width + 20, bg_rect.height + 10))
    bg_surface.fill((0, 0, 0))
    bg_surface.set_alpha(180)
    screen.blit(bg_surface, (0, 0))
    screen.blit(instr, (10, 5))

    pygame.display.flip()

pygame.quit()
