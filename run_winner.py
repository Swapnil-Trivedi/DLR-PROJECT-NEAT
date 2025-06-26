import neat
import pickle
import numpy as np
import pygame
from jumpking_env import JumpKingEnv

# Constants
WIDTH, HEIGHT = 1400, 600

def run_winner(config_path, genome_path="best_genome.pkl"):
    # Load NEAT config
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Load the best genome
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Create the neural network from the genome
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Set up the environment with rendering
    env = JumpKingEnv(render_mode="human")
    clock = pygame.time.Clock()

    obs, _ = env.reset()
    done = False
    step_count = 0
    max_steps = 2000

    while not done and step_count < max_steps:
        env.render()
        clock.tick(60)  # Limit FPS for viewability (adjust if needed)

        # Normalize input for NEAT
        norm_obs = np.array([
            obs[0] / WIDTH,
            obs[1] / HEIGHT,
            (obs[2] + 15) / 30,
            (obs[3] + 15) / 30,
        ])

        action_prob = net.activate(norm_obs)
        action = np.argmax(action_prob)

        obs, _, done, _, _ = env.step(action)
        step_count += 1

    env.close()

if __name__ == "__main__":
    run_winner("neat-config.ini")
