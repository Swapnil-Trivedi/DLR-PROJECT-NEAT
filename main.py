import pygame
import neat
from player import Player
from platform_model import Platform

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 1400, 600  # Wider window for spacious level
FPS = 90
GRAVITY = 0.4
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump King")
clock = pygame.time.Clock()

# Define the platform level (same as before)
def get_fixed_level():
    platforms = []
    ground_y = HEIGHT - 40
    # Start platform (left ground)
    platforms.append(Platform(0, ground_y, 100, 20, "start"))

    # Intermediate pads, smooth ascending jumps
    pads = [
        (180, HEIGHT - 140),
        (350, HEIGHT - 200),
        (520, HEIGHT - 260),
        (700, HEIGHT - 230),
        (880, HEIGHT - 280),
        (1050, HEIGHT - 200),
    ]
    for x, y in pads:
        platforms.append(Platform(x, y, 100, 20, "pad"))

    # End platform at ground level, right of last pad
    end_x = pads[-1][0] + 240
    platforms.append(Platform(end_x, ground_y, 100, 20, "end"))

    return platforms

# Function to evaluate the genomes in the population
def eval_genomes(genomes, config):
    """
    Evaluates each genome (neural network) in the current population.
    """
    global WIN
    win = WIN
    score = 0
    nets = []
    players = []
    ge = []

    # Create the neural networks and player objects
    for genome_id, genome in genomes:
        genome.fitness = 0  # Start with zero fitness
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player(220, HEIGHT - 60))  # Starting position of player
        ge.append(genome)

    platforms = get_fixed_level()
    run = True

    while run and len(players) > 0:
        clock.tick(FPS)
        win.fill((255, 255, 255))  # Clear the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        for i, player in enumerate(players):
            player.apply_gravity(GRAVITY)
            player.update()

            # Feed the neural network with current inputs (player state)
            output = nets[players.index(player)].activate((player.x, player.y, player.vel_x, player.vel_y))

            # Decide whether to jump based on the neural network output
            if output[0] > 0.5:
                # Jump if the network says so
                dx, dy = player.get_aim_direction()
                player.jump(dx, dy)

            player.on_ground = False
            for plat in platforms:
                result = player.check_collision(plat)
                if result == "land":
                    player.land_on(plat)
                    genome.fitness += 1  # Increase fitness when landing on a pad
                    if plat.type == "end":
                        print("Goal reached!")
                        genome.fitness += 10  # Reward for reaching the goal
                        run = False
                        break
                    break
                elif result == "slide":
                    player.slide()

            # Remove players that fall out of bounds
            if player.y > HEIGHT + 50 or player.x < -50 or player.x > WIDTH + 50:
                nets.pop(players.index(player))
                ge.pop(players.index(player))
                players.pop(players.index(player))

            player.draw(win)
            player.draw_trajectory(win)

        # Draw platforms and update display
        for plat in platforms:
            plat.draw(win)

        # Update the display
        pygame.display.update()

# NEAT configuration and training setup
def run(config_file):
    """
    Runs the NEAT algorithm to train a neural network to play the game.
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population for the NEAT algorithm
    p = neat.Population(config)

    # Add a reporter to show progress
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for a given number of generations
    winner = p.run(eval_genomes, 50)

    # Print the winner genome
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    # Run the NEAT algorithm with the configuration file
    run("config-feedforward.ini")
