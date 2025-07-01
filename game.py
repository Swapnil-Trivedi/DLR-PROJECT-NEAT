import pygame
import neat
import os
import time
import math
import pickle
from player import Player
from platform_model import Platform
from neat.checkpoint import Checkpointer

pygame.init()
WIDTH, HEIGHT = 1400, 600
FPS = 60
GRAVITY = 0.4
GENERATION = 0
BEST_SCORE = 0
GENERATION_TO_RUN = 100

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump King AI")
font = pygame.font.SysFont("comicsans", 28)

def get_fixed_level():
    platforms = []
    ground_y = HEIGHT - 40
    platforms.append(Platform(0, ground_y, 100, 20, "start"))

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

    end_x = pads[-1][0] + 240
    platforms.append(Platform(end_x, ground_y, 100, 20, "end"))
    return platforms

def draw_window(win, players, platforms, gen, best_score, score):
    win.fill((255, 255, 255))
    for plat in platforms:
        plat.draw(win)

    for p in players:
        p.draw(win)

    gen_text = font.render(f"Generation: {gen}", 1, (0, 0, 0))
    alive_text = font.render(f"Alive: {len(players)}", 1, (0, 0, 0))
    best_text = font.render(f"Best Score: {best_score}", 1, (0, 0, 0))
    score_text = font.render(f"Score: {score}", 1, (0, 0, 0))

    win.blit(gen_text, (10, 10))
    win.blit(alive_text, (10, 40))
    win.blit(best_text, (WIDTH - best_text.get_width() - 10, 10))
    win.blit(score_text, (WIDTH - score_text.get_width() - 10, 40))

    pygame.display.update()

def eval_genomes(genomes, config):
    global GENERATION, BEST_SCORE
    GENERATION += 1

    nets = []
    players = []
    ge = []
    platforms = get_fixed_level()
    score = 0
    start_time = time.time()
    last_genocide = time.time()

    landed_platforms = [set() for _ in range(len(genomes))]

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player(10, HEIGHT - 70))  # Start from first platform
        ge.append(genome)

    clock = pygame.time.Clock()
    run = True

    while run and len(players) > 0:
        clock.tick(FPS)
        elapsed = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        for i in range(len(players) - 1, -1, -1):
            player = players[i]
            player.apply_gravity(GRAVITY)
            player.update()

            inputs = (
                player.x,
                player.y,
                player.vel_x,
                player.vel_y,
                player.get_nearest_platform_x(platforms),
                player.get_nearest_platform_y(platforms)
            )

            output = nets[i].activate(inputs)
            angle = output[0] * 180 - 90  # Map output to [-90, 90] degrees

            if player.on_ground:
                dx = player.fixed_power * math.cos(math.radians(angle))
                dy = player.fixed_power * math.sin(math.radians(angle))
                if dx > 0 and dy < 0:
                    ge[i].fitness += 5  # Forward-upward jump bonus
                player.jump(dx, dy)

            player.on_ground = False
            landed = False

            for plat in platforms:
                result = player.check_collision(plat)
                if result == "land":
                    player.land_on(plat)

                    if plat.type == "pad" and plat not in landed_platforms[i]:
                        ge[i].fitness += 25
                        score += 1
                        landed_platforms[i].add(plat)

                    elif plat.type == "end":
                        ge[i].fitness += 30
                        score += 10
                        BEST_SCORE = max(BEST_SCORE, score)
                        with open("best_genome.pkl", "wb") as f:
                            pickle.dump(ge[i], f)
                        run = False
                        break

                    landed = True
                    break

                elif result == "slide":
                    player.slide()
                    ge[i].fitness += 5  # reward for hitting edge

            if not landed and player.on_ground:
                ge[i].fitness -= 5  # idle penalty

            if player.y > HEIGHT + 50 or player.x < -50 or player.x > WIDTH + 50:
                ge[i].fitness -= 20
                nets.pop(i)
                ge.pop(i)
                players.pop(i)
                landed_platforms.pop(i)
                continue

        # Genocide logic every 20 seconds
        if time.time() - last_genocide > 20 and len(players) > 4:
            fitnesses = [(idx, ge[idx].fitness) for idx in range(len(players))]
            fitnesses.sort(key=lambda x: x[1], reverse=True)
            top_50 = int(len(players) * 0.5)
            bottom_50 = int(len(players) * 0.50)

            kill_indices = [idx for idx, _ in fitnesses[top_50:top_50 + bottom_50]]
            for idx in sorted(kill_indices, reverse=True):
                nets.pop(idx)
                ge.pop(idx)
                players.pop(idx)
                landed_platforms.pop(idx)

            last_genocide = time.time()

        draw_window(win, players, platforms, GENERATION, BEST_SCORE, score)

        if elapsed > 60:
            break

def run(config_file):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Save checkpoint every 20 generations
    p.add_reporter(Checkpointer(
        generation_interval=20,
        time_interval_seconds=None,
        filename_prefix="neat-checkpoint-extinction"
    ))

    winner = p.run(eval_genomes, GENERATION_TO_RUN)

    print("\nBest genome:\n", winner)
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.ini")
    run(config_path)
