import pygame
from settings import SCALE


def draw_checkpoints(screen, checkpoints, best_checkpoint_reached):
    """Draw checkpoint markers on the track."""
    for idx, (cx, cy) in enumerate(checkpoints):
        if idx < best_checkpoint_reached:
            color = (0, 180, 80)      # passed — green
        elif idx == best_checkpoint_reached:
            color = (255, 200, 0)     # next target — gold
        else:
            color = (120, 120, 120)   # future — gray

        r = max(4, int(8 * SCALE))
        pygame.draw.circle(screen, color, (cx, cy), r, 0)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), r, 1)


def draw_cars(screen, cars):
    """Draw all alive cars."""
    for car in cars:
        if car.is_alive():
            car.draw(screen)


def draw_hud(screen, generation, still_alive, longest_time, best_cp, total_cp):
    """Draw the heads-up display text."""
    font = pygame.font.SysFont("Arial", int(30 * SCALE))

    text_gen = font.render(f"Generation: {generation}", True, (255, 215, 0))
    screen.blit(text_gen, (int(50 * SCALE), int(50 * SCALE)))

    text_alive = font.render(f"Alive: {still_alive}", True, (255, 215, 0))
    screen.blit(text_alive, (int(50 * SCALE), int(90 * SCALE)))

    text_longest = font.render(f"Longest Time: {longest_time}", True, (0, 255, 0))
    screen.blit(text_longest, (int(50 * SCALE), int(130 * SCALE)))

    text_cp = font.render(f"Best Checkpoint: {best_cp}/{total_cp}", True, (255, 200, 0))
    screen.blit(text_cp, (int(50 * SCALE), int(170 * SCALE)))


def render_frame(screen, track_image, cars, checkpoints, generation, still_alive, longest_time):
    """Render one complete frame: track, checkpoints, cars, HUD."""
    screen.blit(track_image, (0, 0))

    # Find best checkpoint reached by any car
    best_cp = 0
    for car in cars:
        if car.checkpoints_reached > best_cp:
            best_cp = car.checkpoints_reached

    draw_checkpoints(screen, checkpoints, best_cp)
    draw_cars(screen, cars)
    draw_hud(screen, generation, still_alive, longest_time, best_cp, len(checkpoints))

    pygame.display.flip()
