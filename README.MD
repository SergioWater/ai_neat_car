Neural Car Driving with NEAT

This repository contains code that uses the NEAT (NeuroEvolution of Augmenting Topologies) algorithm to train a virtual car to drive around a 2D track built in Pygame. Over multiple generations, the neural networks evolve and (hopefully) learn to survive longer without crashing into borders.

How It Works
	1.	Car and Track
	•	A Car class represents each car’s position, speed, angle, and collision detection.
	•	A collision mask (from pygame.mask) is used to detect border collisions in a track image (map3.png).
	•	Radars (sensor lines) detect distance to the nearest border at several angles.
	2.	Neural Networks (NEAT)
	•	Each car is controlled by a neural network created by the NEAT library.
	•	The neural network receives sensor readings (radar distances) and outputs which action to take (turn left, turn right, speed up, or slow down).
	•	A reward system measures how far a car travels, improving the genome’s fitness score.
	3.	Evolution
	•	After each generation, the best-performing networks are kept and evolve (via mutation/crossover) to form the next generation.
	•	Over multiple generations, the networks should adapt to crash less and drive farther.

Requirements
	•	Python 3.8+ (or any recent version)
	•	Conda (for environment management)
	•	Pygame
	•	NEAT-Python
