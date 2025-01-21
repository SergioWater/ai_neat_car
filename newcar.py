import math
import sys
import os

import neat
import pygame

# Constants
WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)  # White border color

current_generation = 0  # Generation counter

# NEW: Keep track of the best (longest) time across all generations
longest_time_overall = 0

class Car:
    def __init__(self, collision_mask, track_offset):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert()  # convert() speeds up blitting
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # Starting Position
        self.position = [830, 920]
        self.angle = 0
        self.speed = 0
        self.speed_set = False
        
        # Keep track of center
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]

        # For sensor distances
        self.radars = []

        # Alive (not crashed)
        self.alive = True

        # Some stats
        self.distance = 0
        self.time = 0

        # Pre-made collision mask and offset
        self.collision_mask = collision_mask
        self.track_offset = track_offset

    def draw(self, screen):
        """Draw the car."""
        screen.blit(self.rotated_sprite, self.position)

    def check_collision(self):
        """Check if any corner of the car touches the border using mask-based collision."""
        for corner in self.corners:
            corner_x = int(corner[0] - self.track_offset[0])
            corner_y = int(corner[1] - self.track_offset[1])

            # If corner is outside map bounds, consider that a crash
            if corner_x < 0 or corner_x >= self.collision_mask.get_size()[0] \
               or corner_y < 0 or corner_y >= self.collision_mask.get_size()[1]:
                self.alive = False
                return

            # If the mask at that position is 1 -> border
            if self.collision_mask.get_at((corner_x, corner_y)):
                self.alive = False
                return

    def update_radars(self):
        """Check distances to the border at multiple angles using the collision mask."""
        self.radars.clear()
        radar_angles = [-90, -45, 0, 45, 90]  # fewer angles for performance

        for angle in radar_angles:
            length = 0
            hit_border = False

            # Move the radar line step by step
            while not hit_border and length < 300:
                length += 1
                check_x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + angle))) * length)
                check_y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + angle))) * length)

                # Translate to mask coordinates
                mx = check_x - self.track_offset[0]
                my = check_y - self.track_offset[1]

                # Check if within bounds
                if mx < 0 or mx >= self.collision_mask.get_size()[0] or \
                   my < 0 or my >= self.collision_mask.get_size()[1]:
                    hit_border = True
                else:
                    if self.collision_mask.get_at((mx, my)):
                        hit_border = True

            dist = length
            self.radars.append(dist / 30.0)  # scale down the distance

    def update(self):
        """Update car movement, collisions, etc."""
        # Initial speed
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Rotate the sprite around its center
        self.rotated_sprite = pygame.transform.rotate(self.sprite, self.angle)

        # Move the car
        rad_angle = math.radians(360 - self.angle)
        self.position[0] += math.cos(rad_angle) * self.speed
        self.position[1] += math.sin(rad_angle) * self.speed

        # Clamp positions
        self.position[0] = max(20, min(self.position[0], WIDTH - 120))
        self.position[1] = max(20, min(self.position[1], HEIGHT - 120))

        # Update distance and time
        self.distance += self.speed
        self.time += 1

        # Recompute center
        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2
        ]

        # Find corners for collision checking
        half_size = CAR_SIZE_X / 2.0
        angle_offsets = [30, 150, 210, 330]  # corners
        self.corners = []
        for offset in angle_offsets:
            corner_x = self.center[0] + math.cos(math.radians(360 - (self.angle + offset))) * half_size
            corner_y = self.center[1] + math.sin(math.radians(360 - (self.angle + offset))) * half_size
            self.corners.append((corner_x, corner_y))

        # Collision check
        self.check_collision()

        # Radar update
        if self.alive:
            self.update_radars()

    def get_data(self):
        """Returns the distances from the radars."""
        return self.radars

    def is_alive(self):
        return self.alive

    def get_reward(self):
        # Reward based on distance traveled
        return self.distance / 30.0

def run_simulation(genomes, config):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Load track (map) as an image
    track_image = pygame.image.load('map3.png').convert()

    # Create collision mask (white pixels = 1)
    collision_mask = pygame.mask.from_threshold(track_image, BORDER_COLOR, (1, 1, 1, 255))
    track_offset = (0, 0)

    global current_generation
    current_generation += 1

    # We also need to read/modify the global "longest_time_overall"
    global longest_time_overall

    nets = []
    cars = []
    ge = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        genome.fitness = 0
        ge.append(genome)

        cars.append(Car(collision_mask, track_offset))

    frame_counter = 0

    # This generation’s best (just for internal comparison)
    max_time_alive = 0

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        still_alive = 0

        for i, car in enumerate(cars):
            if car.is_alive():
                inputs = car.get_data()
                # Ensure we always have 5 inputs
                while len(inputs) < 5:
                    inputs.append(0.0)

                output = nets[i].activate(inputs)
                choice = output.index(max(output))

                # Perform chosen action
                if choice == 0:
                    car.angle += 10  # Left
                elif choice == 1:
                    car.angle -= 10  # Right
                elif choice == 2:
                    if car.speed > 12:
                        car.speed -= 2
                else:
                    car.speed += 2

                # Update the car
                car.update()

                # Increase genome fitness
                ge[i].fitness += car.get_reward()

                if car.is_alive():
                    still_alive += 1
                    # Track the longest time in this generation
                    if car.time > max_time_alive:
                        max_time_alive = car.time

        # If no cars are left, end this generation
        if still_alive == 0:
            break

        frame_counter += 1
        # Stop after ~20 seconds
        if frame_counter >= 30 * 40:
            break

        # Update our global best time if this gen's max is higher
        if max_time_alive > longest_time_overall:
            longest_time_overall = max_time_alive

        # Draw the track and the cars
        screen.blit(track_image, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display info
        font = pygame.font.SysFont("Arial", 30)

        text_gen = font.render(f"Generation: {current_generation}", True, (0, 0, 0))
        screen.blit(text_gen, (50, 50))

        text_alive = font.render(f"Alive: {still_alive}", True, (0, 0, 0))
        screen.blit(text_alive, (50, 90))

        # NEW: Display the all-time longest time (across all generations)
        text_longest = font.render(f"Longest Time: {longest_time_overall}", True, (0, 255, 0))
        screen.blit(text_longest, (50, 130))

        pygame.display.flip()
        clock.tick(30)  # 30 FPS

def main():
    # Load NEAT config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Create population
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run up to 1000 generations
    winner = p.run(run_simulation, 1000)

if __name__ == "__main__":
    main()