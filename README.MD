# Advanced Autonomous Vehicle Simulation

Self-driving vehicle simulation built with Python, Pygame, and NEAT.

## What It Does

- Simulates cars driving around 2D tracks.
- Uses sensor lines to measure the distance to road boundaries.
- Lets AI-controlled cars choose when to turn, speed up, or slow down.
- Rewards cars for making forward progress through ordered checkpoints.
- Stops cars that crash or remain stuck so training can continue efficiently.

## Tech

Python, Pygame, NEAT-Python

## How It Works

Each car receives five simulated sensor readings. A neural network uses those readings to choose a driving action. Cars that make more progress receive higher scores, and NEAT carries stronger behaviors into later generations.

The project also includes checkpoint loading, multiple tracks, collision detection, and stall detection.

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Engineering Notes

The training score is based on ordered checkpoint progress rather than raw driving distance. This prevents cars from gaining points by moving in circles or repeatedly crossing the same area.
