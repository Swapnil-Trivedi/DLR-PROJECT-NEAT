import pygame
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from player import Player
from platform_model import Platform

WIDTH, HEIGHT = 1400, 600
GRAVITY = 0.4

class Game:
    def __init__(self, render_mode="human"):
        self.render_mode = render_mode
        self.display = None
        self.WIDTH = WIDTH    
        self.HEIGHT = HEIGHT
        self.highest_score = 0  # tracks best score across all runs
        self.reset()  # initializes current player and score
        if self.render_mode == "human":
            self.display = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Jump King")
        self.clock = pygame.time.Clock()
        self.FPS = 90
        self.score = 0
        self.landed_pads = set()
        self.platforms = []
        self.player = None
        self.done = False

        self.reset()

    def get_fixed_level(self):
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

    def reset(self):
        pygame.init()
        self.score = 0
        self.landed_pads = set()
        self.platforms = self.get_fixed_level()
        self.player = Player(self.platforms[0].x + 20, self.platforms[0].y - 40)
        self.done = False
        return self._get_obs()

    def step(self, action):
        # Track jump start
        if self.player.on_ground and not getattr(self.player, 'jumping', False):
            self.player.jumping = False  # reset jump state
        if self.player.on_ground and action in [1, 2]:
            # Player is about to jump
            self.player.jumping = True
            self.player.jump_start_x = self.player.x
            self.player.jump_start_y = self.player.y
            self.player.max_jump_y = self.player.y  # reset max height tracker
    
        self.player.apply_gravity(GRAVITY)
        self.player.update()
    
        # If jumping, track max jump height
        if getattr(self.player, 'jumping', False):
            if self.player.y > self.player.max_jump_y:
                self.player.max_jump_y = self.player.y
    
        self.player.on_ground = False
        reward = 0.01  # small positive reward for being alive
    
        # Reward for horizontal progress (moving right from start)
        progress = max(0, self.player.x - self.platforms[0].x)
        reward += progress * 0.001  # scale it down
    
        landed_this_step = False
    
        for plat in self.platforms:
            result = self.player.check_collision(plat)
            if result == "land":
                self.player.land_on(plat)
                landed_this_step = True
    
                # If just landed, give jump height/distance rewards
                if getattr(self.player, 'jumping', False):
                    jump_height = self.player.max_jump_y - self.player.jump_start_y
                    jump_distance = abs(self.player.x - self.player.jump_start_x)
    
                    # Scale and add jump rewards (tweak these)
                    reward += jump_height * 0.05  
                    reward += jump_distance * 0.02
    
                    self.player.jumping = False  # reset jump flag
    
                if plat.type == "end":
                    reward = 100.0  # ultimate reward for goal
                    self.done = True
                elif plat.type == "pad" and id(plat) not in self.landed_pads:
                    reward += 5.0  # big reward for new pad
                    self.landed_pads.add(id(plat))
                break
            elif result == "slide":
                self.player.slide()
    
        # Out-of-bounds = fail with big penalty
        if (self.player.y < -20 or self.player.y > HEIGHT + 50 or
            self.player.x < -50 or self.player.x > WIDTH + 50):
            reward = -10.0
            self.done = True
    
        return self._get_obs(), reward, self.done, False, {}



    def _get_obs(self):
        return np.array([
            self.player.x, self.player.y,
            self.player.vel_x, self.player.vel_y
        ], dtype=np.float32)

    def render(self):
        if self.render_mode != "human":
            return
        self.display.fill((255, 255, 255))
        for plat in self.platforms:
            plat.draw(self.display)
        self.player.draw(self.display)
        self.player.draw_trajectory(self.display)

        font = pygame.font.SysFont(None, 24)
        self.display.blit(font.render(f"Score: {self.score}", True, (0, 0, 0)), (10, 10))
        self.display.blit(font.render(f"Highest Score: {self.highest_score}", True, (0, 0, 0)), (10, 40))
        pygame.display.update()
        self.clock.tick(self.FPS)


    def play_manually(self):
        run = True
        while run:
            self.clock.tick(self.FPS)
            self.display.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                self.player.handle_input(event)

            self.player.apply_gravity(GRAVITY)
            self.player.update()

            self.player.on_ground = False
            for plat in self.platforms:
                result = self.player.check_collision(plat)
                if result == "land":
                    self.player.land_on(plat)
                    if plat.type == "end":
                        print("Reached the goal! Restarting...")
                        pygame.time.delay(1500)
                        self.reset()
                        break
                elif result == "slide":
                    self.player.slide()

            # Check out-of-bounds
            if (self.player.y < -20 or self.player.y > HEIGHT + 50 or
                self.player.x < -50 or self.player.x > WIDTH + 50):
                print("Fell out of bounds. Restarting...")
                pygame.time.delay(1000)
                self.reset()
                continue

            for plat in self.platforms:
                plat.draw(self.display)

            self.player.draw(self.display)
            self.player.draw_trajectory(self.display)

            pygame.display.update()

    def reset_player(self):
            # Reset player to start position without resetting platforms or window
            self.player = Player(self.platforms[0].x + 20, self.platforms[0].y - 40)
            self.player.on_ground = True
            self.done = False
            self.score = 0
            self.landed_pads.clear()

    def close(self):
        pygame.quit()


# -------- GYM WRAPPER --------
class JumpKingEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, render_mode="human"):
        super().__init__()
        self.game = Game(render_mode=render_mode)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -15, -15], dtype=np.float32),
            high=np.array([WIDTH, HEIGHT, 15, 15], dtype=np.float32)
        )
        self.action_space = spaces.Discrete(3)

    def reset(self, seed=None, options=None):
        obs = self.game.reset()
        return obs, {}

    def step(self, action):
        return self.game.step(action)

    def render(self):
        self.game.render()

    def close(self):
        self.game.close()
