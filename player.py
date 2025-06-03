import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def jump(self, power=-10, forward=5):
        self.vel_y = power
        self.vel_x = forward

    def apply_gravity(self, gravity):
        self.vel_y += gravity

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def collide_with(self, platform):
        px, py, pw, ph = self.x, self.y, self.width, self.height
        plat_x, plat_y, plat_w, plat_h = platform.x, platform.y, platform.width, platform.height

        player_bottom = py + ph
        platform_top = plat_y
        platform_bottom = plat_y + plat_h
        platform_left = plat_x
        platform_right = plat_x + plat_w

        # Top collision check
        if (self.vel_y > 0 and
            player_bottom <= platform_top + 10 and
            px + pw > platform_left and
            px < platform_right and
            player_bottom >= platform_top):
            return "land"

        # Side/bottom collision
        if (px + pw > platform_left and
            px < platform_right and
            player_bottom > platform_top and
            py < platform_bottom):
            return "bounce"

        return None

    def land_on(self, platform):
        self.y = platform.y - self.height
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = True

    def bounce(self):
        self.vel_y = -5
        self.vel_x = -self.vel_x
