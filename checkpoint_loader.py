import os
from settings import SCALE

CHECKPOINT_RADIUS = int(60 * SCALE)


def load_checkpoints():
    """
    Reads checkpoints.txt (created by place_checkpoints.py).
    Returns two lists:
      - checkpoints_1920: raw coordinates in 1920x1080 space
      - checkpoints: scaled coordinates for the current screen
    """
    checkpoints_1920 = []

    if os.path.exists('checkpoints.txt'):
        with open('checkpoints.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if ',' in line:
                    parts = line.split(',')
                    checkpoints_1920.append((int(parts[0]), int(parts[1])))
        print(f"Loaded {len(checkpoints_1920)} checkpoints from checkpoints.txt")
    else:
        print("WARNING: No checkpoints.txt found. Run place_checkpoints.py first!")

    checkpoints = [(int(x * SCALE), int(y * SCALE)) for x, y in checkpoints_1920]

    return checkpoints_1920, checkpoints
