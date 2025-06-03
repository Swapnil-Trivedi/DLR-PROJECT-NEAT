import pygame
import random
import math
from player import Player
from platform_model import Platform

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 0.5
MAX_PADS = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)

# Window setup
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumping Agent")
clock = pygame.time.Clock()


def generate_level():
    """Builds a grounded start and end platform with floating random pads."""
    platforms = []

    # Start on ground (left)
    start = Platform(0, HEIGHT - 50, 100, 20, type="start")

    # End on ground (right)
    end = Platform(WIDTH - 100, HEIGHT - 50, 100, 20, type="end")

    platforms.append(start)

    # Generate random floating pads
    for _ in range(random.randint(5, MAX_PADS)):
        x = random.randint(150, WIDTH - 250)
        y = random.randint(100, HEIGHT - 200)
        platforms.append(Platform(x, y, 100, 20, type="pad"))

    platforms.append(end)
    return platforms


def draw_trajectory(surface, start_pos, power_x, power_y):
    """Draw dotted projectile path."""
    x, y = start_pos
    vx = power_x
    vy = power_y
    points = []

    for i in range(30):
        t = i * 0.3
        px = x + vx * t
        py = y + vy * t + 0.5 * GRAVITY * (t ** 2)
        if py > HEIGHT:
            break
        points.append((int(px), int(py)))

    for point in points:
        pygame.draw.circle(surface, GRAY, point, 3)


def handle_manual_jump(player, aim_state):
    """Handle aiming and jumping using spacebar."""
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and player.on_ground:
        aim_state["active"] = True

        # Step 1: Aim vertical
        if not aim_state["locked_y"]:
            aim_state["y"] -= aim_state["y_dir"] * 3
            if aim_state["y"] < 100 or aim_state["y"] > HEIGHT - 200:
                aim_state["y_dir"] *= -1
        else:
            # Step 2: Aim horizontal
            aim_state["x"] += aim_state["x_dir"] * 3
            if aim_state["x"] < 5 or aim_state["x"] > 15:
                aim_state["x_dir"] *= -1

    elif aim_state["active"] and not keys[pygame.K_SPACE]:
        # On release: perform jump
        player.jump(power=-aim_state["y"] / 10, forward=aim_state["x"])
        aim_state["active"] = False
        aim_state["locked_y"] = False
        aim_state["x"] = 5
        aim_state["y"] = 200

    elif aim_state["active"] and keys[pygame.K_RETURN]:
        aim_state["locked_y"] = True


def main():
    run = True
    score = 0
    platforms = generate_level()
    player = Player(20, HEIGHT - 70)

    aim_state = {
        "active": False,
        "locked_y": False,
        "y": 200,      # controls jump height
        "x": 5,        # controls forward velocity
        "y_dir": 1,
        "x_dir": 1
    }

    while run:
        clock.tick(FPS)
        win.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Handle manual input
        handle_manual_jump(player, aim_state)

        # Trajectory preview
        if aim_state["active"] and player.on_ground:
            draw_trajectory(win, (player.x + player.width // 2, player.y + player.height // 2),
                            aim_state["x"], -aim_state["y"] / 10)

        # Apply physics
        player.apply_gravity(GRAVITY)
        player.update()

        # Collision detection
        player.on_ground = False
        landed = False

        for plat in platforms:
            result = player.collide_with(plat)
            if result == "land":
                player.land_on(plat)
                landed = True

                if plat.type == "pad":
                    score += 1
                elif plat.type == "end":
                    print(f"SUCCESS! Final Score: {score}")
                    pygame.time.delay(1000)
                    return main()  # restart

                break
            elif result == "bounce":
                print("Bounced. Game Over.")
                pygame.time.delay(1000)
                return main()  # reset

        # Fell on ground?
        if player.y > HEIGHT - player.height:
            print("Fell on ground. Game Over.")
            pygame.time.delay(1000)
            return main()

        # Draw platforms
        for plat in platforms:
            plat.draw(win)

        # Draw player
        player.draw(win)

        # Draw score
        font = pygame.font.SysFont(None, 28)
        win.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
