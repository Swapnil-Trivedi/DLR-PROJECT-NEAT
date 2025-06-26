import neat
import numpy as np
import random
import pickle
from jumpking_env import JumpKingEnv
from utils import create_log_dir, init_csv_log, log_generation, close_csv_log, get_next_run_number


# Constants
WIDTH, HEIGHT = 1400, 600

def eval_genomes(genomes, config, render_genome=None):
    env = JumpKingEnv(render_mode=None)  # No window for training speed

    for genome_id, genome in genomes:
        env.game.reset_player()  # Reset only player
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        fitness = 0.0
        obs = env.game._get_obs()
        done = False
        step_count = 0
        max_steps = 1000

        while not done and step_count < max_steps:
            env.render()

            norm_obs = np.array([
                obs[0] / WIDTH,        # player x
                obs[1] / HEIGHT,       # player y
                obs[2] / WIDTH,        # next pad center x
                obs[3] / HEIGHT        # next pad center y
            ])

            action_prob = net.activate(norm_obs)
            action = np.argmax(action_prob)

            obs, reward, done, _, _ = env.step(action)
            fitness += reward
            step_count += 1

        genome.fitness = fitness

    env.close()


def run(config_file):
    config = neat.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_file
    )

    p = neat.Population(config)

    # Reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(generation_interval=10, filename_prefix='neat-checkpoint-'))

    generations = 200
    
    for gen in range(generations):
        print(f"\n=== Generation {gen + 1} ===")
        render_genome = random.choice(list(p.population.keys()))
        p.run(lambda genomes, config: eval_genomes(genomes, config, render_genome=render_genome), 1)

    # Save best genome
    best = stats.best_genome()
    print("\nBest genome:\n{!s}".format(best))

    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best, f)
    print("Saved best genome to 'best_genome.pkl'")


if __name__ == "__main__":
    run("neat-config.ini")
