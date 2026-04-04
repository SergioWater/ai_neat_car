import sys
import neat
import pygame
from settings import WIDTH, HEIGHT, BORDER_COLOR, SCALE, MAP_FILE, MAX_FRAMES, FPS
from checkpoint_loader import load_checkpoints, CHECKPOINT_RADIUS
from car import Car
from renderer import render_frame

# Load checkpoints once at module level
CHECKPOINTS_1920, CHECKPOINTS = load_checkpoints()

# Globals for cross-generation tracking
current_generation = 0
longest_time_overall = 0


def run_simulation(genomes, config):
    global current_generation, longest_time_overall

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Load track
    track_image = pygame.image.load(MAP_FILE).convert()
    track_image = pygame.transform.scale(track_image, (WIDTH, HEIGHT))

    # Create collision mask (white pixels = 1)
    collision_mask = pygame.mask.from_threshold(track_image, BORDER_COLOR, (1, 1, 1, 255))
    track_offset = (0, 0)

    current_generation += 1

    nets = []
    cars = []
    ge = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        ge.append(genome)
        cars.append(Car(collision_mask, track_offset, CHECKPOINTS, CHECKPOINT_RADIUS))

    frame_counter = 0
    max_time_alive = 0

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit(0)

        still_alive = 0

        for i, car in enumerate(cars):
            if car.is_alive():
                inputs = car.get_data()
                while len(inputs) < 5:
                    inputs.append(0.0)

                output = nets[i].activate(inputs)
                choice = output.index(max(output))

                if choice == 0:
                    car.angle += 10
                elif choice == 1:
                    car.angle -= 10
                elif choice == 2:
                    if car.speed > 6 * SCALE:
                        car.speed -= 2 * SCALE
                else:
                    car.speed += 2 * SCALE

                car.update()

                # Assign fitness when car dies
                if not car.is_alive():
                    ge[i].fitness = car.get_reward()

                if car.is_alive():
                    still_alive += 1
                    if car.time > max_time_alive:
                        max_time_alive = car.time

        if still_alive == 0:
            break

        frame_counter += 1
        if frame_counter >= MAX_FRAMES:
            break

        if max_time_alive > longest_time_overall:
            longest_time_overall = max_time_alive

        # Render
        render_frame(screen, track_image, cars, CHECKPOINTS,
                     current_generation, still_alive, longest_time_overall)

        clock.tick(FPS)

    # Assign fitness to survivors
    for i, car in enumerate(cars):
        if car.is_alive():
            ge[i].fitness = car.get_reward()
