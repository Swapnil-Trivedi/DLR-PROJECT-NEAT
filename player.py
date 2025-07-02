import pygame
import math

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 20, 30
        self.vel_x, self.vel_y = 0, 0
        self.on_ground = False
        # Aiming system
        self.aiming = False
        self.aim_timer = 0
        self.aim_max_time = 120
        self.fixed_power = 15

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def handle_input(self, event):
        if self.on_ground:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.aiming = True
                self.aim_timer = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and self.aiming:
                dx, dy = self.get_aim_direction()
                self.jump(dx, dy)
                self.aiming = False

    def apply_gravity(self, g):
        self.vel_y += g
        self.vel_y = min(self.vel_y, 15)  # cap fall speed

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

        if self.aiming:
            self.aim_timer += 1
            if self.aim_timer > self.aim_max_time:
                self.aim_timer = 0

    def jump(self, dx, dy):
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        norm_dx = dx / dist
        norm_dy = dy / dist
        self.vel_x = norm_dx * self.fixed_power
        self.vel_y = norm_dy * self.fixed_power
        self.on_ground = False

    def get_aim_direction(self):
        range_x = 200
        range_y = 150
        t = -1 * self.aim_timer / self.aim_max_time * 0.5 * math.pi
        dx = math.cos(t) * (range_x // 2)
        dy = math.sin(t) * (range_y // 2)
        return dx, dy

    def draw_trajectory(self, win):
        if not self.aiming:
            return
        dx, dy = self.get_aim_direction()
        angle = math.atan2(dy, dx)
        vx = math.cos(angle) * self.fixed_power
        vy = math.sin(angle) * self.fixed_power
        g = 0.4
        t = 0
        points = []
        while t < 2.5:
            x = self.x + self.width // 2 + vx * t
            y = self.y + self.height // 2 + vy * t + 0.5 * g * t * t
            points.append((int(x), int(y)))
            t += 0.1
        for point in points:
            pygame.draw.circle(win, (200, 0, 0), point, 3)

    def check_collision(self, plat):
        px, py, pw, ph = self.x, self.y, self.width, self.height
        sx, sy, sw, sh = plat.x, plat.y, plat.width, plat.height

        if px + pw > sx and px < sx + sw and py + ph > sy and py < sy + sh:
            # Check if landing on top
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