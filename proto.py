import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Single Cell Evolution Simulation")

# Colors
black = (0, 0, 0)
initial_color = (0, 255, 0)
final_color = (255, 0, 0)

# Cell class
class Cell:
    def __init__(self):
        self.x = width // 2
        self.y = height // 2
        self.size = 10
        self.color = initial_color
        self.age = 0
        self.max_age = 100  # Define a maximum age for normalization

    def move(self):
        self.x += random.randint(-5, 5)
        self.y += random.randint(-5, 5)
        self.x = max(0, min(self.x, width))
        self.y = max(0, min(self.y, height))

    def evolve(self):
        self.age += 0.1
        normalized_age = min(self.age / self.max_age, 1)
        self.color = (
            int(initial_color[0] + normalized_age * (final_color[0] - initial_color[0])),
            int(initial_color[1] + normalized_age * (final_color[1] - initial_color[1])),
            int(initial_color[2] + normalized_age * (final_color[2] - initial_color[2]))
        )

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

# Main loop
def main():
    clock = pygame.time.Clock()
    cell = Cell()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        cell.move()
        cell.evolve()

        screen.fill(black)
        cell.draw(screen)
        pygame.display.flip()

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()