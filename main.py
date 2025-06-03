import pygame
from player import Player
from platform_model import Platform

pygame.init()
WIDTH, HEIGHT = 1200, 600  # wider window for easier layout
FPS = 60
GRAVITY = 0.4

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump King - Easy Level")
clock = pygame.time.Clock()

def get_fixed_level():
    platforms = []
    # Start and end platforms on extremes
    platforms.append(Platform(0, HEIGHT - 40, 100, 20, "start"))
    platforms.append(Platform(WIDTH - 100, 120, 100, 20, "end"))

    # Easy, spaced pads moving left to right, gradual vertical changes
    pads = [
        (180, HEIGHT - 140),  # after start
        (350, HEIGHT - 200),
        (520, HEIGHT - 260),
        (700, HEIGHT - 230),
        (880, HEIGHT - 280),
        (1050, HEIGHT - 200),
    ]

    for x, y in pads:
        platforms.append(Platform(x, y, 100, 20, "pad"))

    return platforms

# rest of main() as before...
# (Use the player.py and platform.py unchanged, just adjust main.py's window and level setup)

# Your main game loop will be same, just call get_fixed_level() here

def main():
    run = True
    score = 0
    landed_pads = set()
    platforms = get_fixed_level()
    player = Player(platforms[0].x + 20, platforms[0].y - 40)

    while run:
        clock.tick(FPS)
        win.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            player.handle_input(event)

        player.apply_gravity(GRAVITY)
        player.update()

        # Bounds check
        if player.y < -20 or player.y > HEIGHT + 50 or player.x < -50 or player.x > WIDTH + 50:
            print("Fell out of bounds. Restarting.")
            pygame.time.delay(1000)
            return main()

        player.on_ground = False

        for plat in platforms:
            result = player.check_collision(plat)
            if result == "land":
                player.land_on(plat)
                if plat.type == "end":
                    print("Reached the goal!")
                    pygame.time.delay(1500)
                    return main()
                elif plat.type == "pad" and id(plat) not in landed_pads:
                    score += 1
                    landed_pads.add(id(plat))
                break
            elif result == "slide":
                player.slide()

        for plat in platforms:
            plat.draw(win)

        player.draw(win)
        player.draw_charge_bar(win)

        font = pygame.font.SysFont(None, 24)
        win.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
