import pygame

class Platform:
    def __init__(self, x, y, width, height, type="pad"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type  # 'start', 'end', or 'pad'

    def draw(self, win):
        if self.type == "start":
            color = (0, 100, 255)   # Blue
        elif self.type == "end":
            color = (255, 100, 0)   # Orange
        else:
            color = (0, 200, 0)     # Green
        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height))
