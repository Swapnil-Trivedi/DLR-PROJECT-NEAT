import pygame
import math

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 20, 30
        self.vel_x, self.vel_y = 0, 0
        self.on_ground = False
        self.charging = False
        self.charge_time = 0
        self.max_charge_time = 60

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def draw_charge_bar(self, win):
        if self.charging:
            ratio = min(self.charge_time / self.max_charge_time, 1)
            pygame.draw.rect(win, (150, 150, 150), (self.x, self.y - 10, 60, 5))
            pygame.draw.rect(win, (0, 200, 0), (self.x, self.y - 10, 60 * ratio, 5))

    def handle_input(self, event):
        if self.on_ground:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.charging = True
                self.charge_time = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.charging:
                power = min(self.charge_time / self.max_charge_time, 1)
                self.jump(power)
                self.charging = False

        if self.charging:
            self.charge_time += 1

    def apply_gravity(self, g):
        self.vel_y += g

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def jump(self, power):
        angle = -math.pi / 4
        speed = power * 20
        self.vel_x = speed * math.cos(angle)
        self.vel_y = speed * math.sin(angle)
        self.on_ground = False

    def check_collision(self, plat):
        px, py, pw, ph = self.x, self.y, self.width, self.height
        sx, sy, sw, sh = plat.x, plat.y, plat.width, plat.height

        if px + pw > sx and px < sx + sw:
            if py + ph <= sy + 10 and py + ph >= sy and self.vel_y > 0:
                return "land"
            elif py < sy + sh and py + ph > sy:
                return "slide"
        return None

    def land_on(self, plat):
        self.y = plat.y - self.height
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = True

    def slide(self):
        self.vel_x = 0
