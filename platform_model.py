import pygame

class Platform:
    def __init__(self, x, y, width, height, type="pad"):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.type = type

    def draw(self, win):
        color = {
            "start": (100, 100, 255),
            "end": (255, 100, 0),
            "pad": (0, 200, 0)
        }.get(self.type, (0, 200, 0))
        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height))