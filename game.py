import pygame
import neat
from player import Player
from platform_model import Platform
import math

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 1400, 600
FPS = 90
GRAVITY = 0.4
MAX_FRAMES = 1000

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump NEAT")
clock = pygame.time.Clock()

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

# def eval_genomes(genomes, config):
#     global WIN
#     win = WIN
#     nets = []
#     players = []
#     ge = []

#     for genome_id, genome in genomes:
#         genome.fitness = 0
#         net = neat.nn.FeedForwardNetwork.create(genome, config)
#         nets.append(net)
#         players.append(Player(20, HEIGHT - 70))  # Just above start platform
#         ge.append(genome)

#     platforms = get_fixed_level()
#     run = True
#     frame_count = 0

#     while run and len(players) > 0 and frame_count < MAX_FRAMES:
#         clock.tick(FPS)
#         win.fill((255, 255, 255))
#         frame_count += 1

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#                 pygame.quit()
#                 quit()

#         for i, player in enumerate(players):
#             player.apply_gravity(GRAVITY)
#             player.update()

#             # Find next platform to aim for (right of player)
#             try:
#                 next_plat = min(
#                     [p for p in platforms if p.x > player.x],
#                     key=lambda p: p.x
#                 )
#             except ValueError:
#                 next_plat = platforms[-1]  # fallback to end

#             # Input to NEAT: normalized
#             input_vector = [
#                 player.x / WIDTH,
#                 player.y / HEIGHT,
#                 player.vel_x / 10.0,
#                 player.vel_y / 10.0,
#                 (next_plat.x - player.x) / WIDTH,
#                 (next_plat.y - player.y) / HEIGHT
#             ]
#             output = nets[i].activate(input_vector)

#             if player.on_ground and output[0] > 0.5:
#                 dx, dy = player.get_aim_direction()
#                 player.jump(dx, dy)

#             # Collision check
#             player.on_ground = False
#             for plat in platforms:
#                 result = player.check_collision(plat)
#                 if result == "land":
#                     player.land_on(plat)
#                     ge[i].fitness += 5  # reward for landing
#                     if plat.type == "end":
#                         print("Goal reached!")
#                         ge[i].fitness += 20
#                         run = False
#                     break
#                 elif result == "slide":
#                     player.slide()

#             # Distance-based shaping reward
#             dx = abs(next_plat.x - player.x)
#             dy = abs(next_plat.y - player.y)
#             ge[i].fitness += 1.0 / (dx + dy + 5)

#             # Out of bounds removal
#             if player.y > HEIGHT + 100 or player.x < -100 or player.x > WIDTH + 100:
#                 nets.pop(i)
#                 ge.pop(i)
#                 players.pop(i)
#                 continue

#             # Draw agent
#             player.draw(win)
#             player.draw_trajectory(win)

#         for plat in platforms:
#             plat.draw(win)

#         pygame.display.update()

def eval_genomes(genomes, config):
    global WIN
    win = WIN
    nets, players, ge = [], [], []
    stay_timer, last_platform = [], []
    platforms = get_fixed_level()
    start_plat = platforms[0]

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        player = Player(start_plat.x + 10, start_plat.y - 30)
        nets.append(net)
        players.append(player)
        ge.append(genome)
        stay_timer.append(0)
        last_platform.append(None)

    while len(players) > 0:
        clock.tick(FPS)
        win.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        to_remove = []

        for i, player in enumerate(players):
            player.apply_gravity(GRAVITY)
            player.update()

            next_plat = None
            min_dx = float('inf')
            for plat in platforms:
                if plat.x + plat.width >= player.x + player.width:
                    dx = plat.x - player.x
                    if dx < min_dx:
                        min_dx = dx
                        next_plat = plat

            dx_to_plat = next_plat.x - player.x if next_plat else 0
            dy_to_plat = next_plat.y - player.y if next_plat else 0

            inputs = (player.x, player.y, player.vel_x, player.vel_y, dx_to_plat, dy_to_plat)
            output = nets[i].activate(inputs)

            if player.on_ground:
                angle = output[0] * (math.pi / 2) - math.pi / 2
                dx = math.cos(angle) * player.fixed_power
                dy = math.sin(angle) * player.fixed_power
                player.jump(dx, dy)

            player.on_ground = False
            landed = False

            for plat in platforms:
                result = player.check_collision(plat)
                if result == "land":
                    player.land_on(plat)
                    if plat != last_platform[i]:
                        ge[i].fitness += 15
                        last_platform[i] = plat
                        stay_timer[i] = 0
                    else:
                        stay_timer[i] += 1
                        if stay_timer[i] > 2 * FPS:
                            ge[i].fitness -= 5
                    if plat.type == "end":
                        ge[i].fitness += 20
                    landed = True
                    break
                elif result == "slide":
                    ge[i].fitness += 5

            if player.y > HEIGHT + 50 or player.x < -50 or player.x > WIDTH + 50:
                ge[i].fitness -= 20
                to_remove.append(i)

            player.draw(win)

        for i in sorted(to_remove, reverse=True):
            nets.pop(i)
            ge.pop(i)
            players.pop(i)
            stay_timer.pop(i)
            last_platform.pop(i)

        for plat in platforms:
            plat.draw(win)

        pygame.display.update()



def run(config_file):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(eval_genomes, 500)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    run("config-feedforward.ini")
