import pygame

# Initialize Pygame and get screen info
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Calculate SCALE factor (80% of screen width vs 1920)
TARGET_WIDTH = int(SCREEN_WIDTH * 0.8)
SCALE = TARGET_WIDTH / 1920.0

# Scaled Constants
WIDTH = int(1920 * SCALE)
HEIGHT = int(1080 * SCALE)

CAR_SIZE_X = int(60 * SCALE)
CAR_SIZE_Y = int(60 * SCALE)

BORDER_COLOR = (255, 255, 255, 255)  # White border color

# Track map file
MAP_FILE = 'Tracks/map3.png'

# Car sprite file
CAR_FILE = 'car.png'

# Stall detection
STALL_WINDOW = 60
STALL_THRESHOLD = 30 * SCALE

# Safety timeout (frames) — 5 minutes at 30 FPS
MAX_FRAMES = 30 * 300

# FPS
FPS = 30
