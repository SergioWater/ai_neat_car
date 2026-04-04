import math
import pygame
from settings import SCALE, WIDTH, HEIGHT, CAR_SIZE_X, CAR_SIZE_Y, CAR_FILE, STALL_WINDOW, STALL_THRESHOLD


class Car:
    def __init__(self, collision_mask, track_offset, checkpoints, checkpoint_radius):
        self.sprite = pygame.image.load(CAR_FILE).convert()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # Starting Position (Scaled)
        self.position = [830 * SCALE, 920 * SCALE]
        self.angle = 0
        self.speed = 0
        self.speed_set = False

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]

        self.radars = []
        self.alive = True
        self.distance = 0
        self.time = 0

        self.collision_mask = collision_mask
        self.track_offset = track_offset

        # Progress tracking
        self.start_position = list(self.position)
        self.position_history = []
        self.checkpoints_reached = 0

        # Store checkpoint references
        self.checkpoints = checkpoints
        self.checkpoint_radius = checkpoint_radius

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)

    def check_collision(self):
        for corner in self.corners:
            corner_x = int(corner[0] - self.track_offset[0])
            corner_y = int(corner[1] - self.track_offset[1])

            if corner_x < 0 or corner_x >= self.collision_mask.get_size()[0] \
               or corner_y < 0 or corner_y >= self.collision_mask.get_size()[1]:
                self.alive = False
                return

            if self.collision_mask.get_at((corner_x, corner_y)):
                self.alive = False
                return

    def update_radars(self):
        self.radars.clear()
        radar_angles = [-90, -45, 0, 45, 90]

        for angle in radar_angles:
            length = 0
            hit_border = False

            while not hit_border and length < 300 * SCALE:
                length += 1
                check_x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + angle))) * length)
                check_y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + angle))) * length)

                mx = check_x - self.track_offset[0]
                my = check_y - self.track_offset[1]

                if mx < 0 or mx >= self.collision_mask.get_size()[0] or \
                   my < 0 or my >= self.collision_mask.get_size()[1]:
                    hit_border = True
                else:
                    if self.collision_mask.get_at((mx, my)):
                        hit_border = True

            self.radars.append(length / (30.0 * SCALE))

    def update(self):
        if not self.speed_set:
            self.speed = 20 * SCALE
            self.speed_set = True

        self.rotated_sprite = pygame.transform.rotate(self.sprite, self.angle)

        rad_angle = math.radians(360 - self.angle)
        self.position[0] += math.cos(rad_angle) * self.speed
        self.position[1] += math.sin(rad_angle) * self.speed

        self.position[0] = max(20 * SCALE, min(self.position[0], WIDTH - 120 * SCALE))
        self.position[1] = max(20 * SCALE, min(self.position[1], HEIGHT - 120 * SCALE))

        self.distance += self.speed
        self.time += 1

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2
        ]

        half_size = CAR_SIZE_X / 2.0
        angle_offsets = [30, 150, 210, 330]
        self.corners = []
        for offset in angle_offsets:
            corner_x = self.center[0] + math.cos(math.radians(360 - (self.angle + offset))) * half_size
            corner_y = self.center[1] + math.sin(math.radians(360 - (self.angle + offset))) * half_size
            self.corners.append((corner_x, corner_y))

        self.check_collision()

        if self.alive:
            self.update_radars()

        # Checkpoint detection — strictly sequential, no repeats possible
        if self.alive and self.checkpoints_reached < len(self.checkpoints):
            next_cp = self.checkpoints[self.checkpoints_reached]
            dist_to_cp = math.sqrt(
                (self.center[0] - next_cp[0]) ** 2 +
                (self.center[1] - next_cp[1]) ** 2
            )
            if dist_to_cp < self.checkpoint_radius:
                self.checkpoints_reached += 1

        # Rolling window stall detection
        if self.alive:
            self.position_history.append((self.center[0], self.center[1]))
            if len(self.position_history) > STALL_WINDOW:
                old = self.position_history[-STALL_WINDOW]
                dx = self.center[0] - old[0]
                dy = self.center[1] - old[1]
                if math.sqrt(dx * dx + dy * dy) < STALL_THRESHOLD:
                    self.alive = False

    def get_data(self):
        return self.radars

    def is_alive(self):
        return self.alive

    def get_reward(self):
        """
        Fitness = checkpoints_reached * 1000
                + fractional progress toward next checkpoint (0-999)

        Checkpoints are strictly sequential — a car can never re-collect
        a checkpoint it already passed. Going backwards earns nothing.
        """
        fitness = self.checkpoints_reached * 1000.0

        # Fractional progress toward next checkpoint
        if self.checkpoints_reached < len(self.checkpoints):
            next_cp = self.checkpoints[self.checkpoints_reached]
            dist_to_next = math.sqrt(
                (self.center[0] - next_cp[0]) ** 2 +
                (self.center[1] - next_cp[1]) ** 2
            )
            if self.checkpoints_reached > 0:
                prev_cp = self.checkpoints[self.checkpoints_reached - 1]
            else:
                prev_cp = (int(self.start_position[0] + CAR_SIZE_X / 2),
                           int(self.start_position[1] + CAR_SIZE_Y / 2))

            total_dist = math.sqrt(
                (next_cp[0] - prev_cp[0]) ** 2 +
                (next_cp[1] - prev_cp[1]) ** 2
            )
            if total_dist > 0:
                progress = max(0.0, min(1.0, 1.0 - (dist_to_next / total_dist)))
                fitness += progress * 999.0

        return fitness
