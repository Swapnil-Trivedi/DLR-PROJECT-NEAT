import pygame
import math

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 20, 30
        self.vel_x, self.vel_y = 0, 0
        self.on_ground = False
        self.fixed_power = 15

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def apply_gravity(self, g):
        self.vel_y += g
        self.vel_y = min(self.vel_y, 15)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def jump(self, dx, dy):
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        self.vel_x = dx
        self.vel_y = dy
        self.on_ground = False

    def check_collision(self, plat):
        px, py, pw, ph = self.x, self.y, self.width, self.height
        sx, sy, sw, sh = plat.x, plat.y, plat.width, plat.height
        if px + pw > sx and px < sx + sw and py + ph > sy and py < sy + sh:
            if self.vel_y > 0 and py + ph <= sy + 10:
                return "land"
            else:
                return "slide"
        return None

    def land_on(self, plat):
        self.y = plat.y - self.height
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = True

    def get_nearest_platform_x(self, platforms):
        visible = [p for p in platforms if p.y >= self.y]
        if not visible:
            return self.x
        nearest = min(visible, key=lambda p: abs(self.x - p.x))
        return nearest.x

    def get_nearest_platform_y(self, platforms):
        visible = [p for p in platforms if p.y >= self.y]
        if not visible:
            return self.y
        nearest = min(visible, key=lambda p: abs(self.y - p.y))
        return nearest.y
    def slide(self):
         # Simple slide behavior, e.g., reduce horizontal speed slightly
         self.vel_x *= 0.9  # friction-like effect