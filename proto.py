import pygame
import random
import matplotlib.pyplot as plt

# Constants
WIDTH, HEIGHT = 800, 800
FOOD_RESPAWN_TIME = 5000  # in milliseconds
FOOD_COUNT = 64
PREY_COUNT = 32
PREDATOR_SPAWN_TIME = 10000  # in milliseconds

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class Food:
    def __init__(self):
        self.respawn()

    def respawn(self, quarter=None):
        if quarter is None:
            quarter = random.randint(1, 4)
        if quarter == 1:
            self.x = random.randint(0, WIDTH // 2)
            self.y = random.randint(0, HEIGHT // 2)
        elif quarter == 2:
            self.x = random.randint(WIDTH // 2, WIDTH)
            self.y = random.randint(0, HEIGHT // 2)
        elif quarter == 3:
            self.x = random.randint(0, WIDTH // 2)
            self.y = random.randint(HEIGHT // 2, HEIGHT)
        else:
            self.x = random.randint(WIDTH // 2, WIDTH)
            self.y = random.randint(HEIGHT // 2, HEIGHT)

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), 5)


class Cell:
    def __init__(self, x, y, size, speed, hunger_rate, reproduction_time, is_predator=False):
        self.x, self.y = x, y
        self.base_size = size
        self.size = size
        self.speed = speed
        self.hunger_rate = hunger_rate
        self.reproduction_time = reproduction_time
        self.is_predator = is_predator
        self.energy = 100
        self.alive = True
        self.time_since_reproduction = 0
        self.eaten_count = 0

    def move(self):
        dx, dy = 0, 0
        if self.is_predator:
            if prey:
                closest_prey = min(prey, key=lambda p: (p.x - self.x) ** 2 + (p.y - self.y) ** 2)
                dx, dy = closest_prey.x - self.x, closest_prey.y - self.y
        else:
            if foods:
                closest_food = min(foods, key=lambda f: (f.x - self.x) ** 2 + (f.y - self.y) ** 2)
                dx, dy = closest_food.x - self.x, closest_food.y - self.y

        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.x += int(self.speed * dx / dist)
        self.y += int(self.speed * dy / dist)

    def eat(self):
        if self.is_predator:
            for p in prey[:]:
                if abs(self.x - p.x) < self.size and abs(self.y - p.y) < self.size:
                    self.energy = min(100, self.energy + 50)
                    prey.remove(p)
                    self.eaten_count += 1
                    self.size += 2
        else:
            for food in foods:
                if abs(self.x - food.x) < self.size and abs(self.y - food.y) < self.size:
                    self.energy = min(100, self.energy + 50)
                    quarter = 1 if food.x < WIDTH // 2 and food.y < HEIGHT // 2 else \
                        2 if food.x >= WIDTH // 2 and food.y < HEIGHT // 2 else \
                            3 if food.x < WIDTH // 2 and food.y >= HEIGHT // 2 else 4
                    food.respawn(quarter)
                    self.eaten_count += 1
                    self.size += 2

    def reproduce(self):
        if self.eaten_count >= 2:
            self.eaten_count = 0
            self.size = self.base_size
            offset = 5
            plus_or_minus_x = random.choice([-1, 1])
            plus_or_minus_y = random.choice([-1, 1])

            return [Cell(self.x + offset * plus_or_minus_x, self.y + offset * plus_or_minus_y,
                         self.base_size,
                         self.speed, self.hunger_rate,
                         self.reproduction_time, self.is_predator)]
        return []

    def update(self, dt):
        self.energy -= self.hunger_rate * dt / 1000
        self.time_since_reproduction += dt
        if self.energy <= 0:
            self.alive = False
        else:
            self.move()
            self.eat()

    def draw(self):
        if self.is_predator:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))
        else:
            pygame.draw.circle(screen, BLUE, (self.x, self.y), self.size)


def spawn_prey(size=10, speed=1.9, hunger_rate=2, reproduction_time=5000):
    return Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), size=size, speed=speed, hunger_rate=hunger_rate,
                reproduction_time=reproduction_time)


def spawn_predator(size=15, speed=2, hunger_rate=6, reproduction_time=7000):
    return Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), size=size, speed=speed, hunger_rate=hunger_rate,
                reproduction_time=reproduction_time, is_predator=True)


def generate_parameters():

    size = random.randint(5, 15)
    size_closest_multiple_of_5 = round(size / 3)
    speed = size_closest_multiple_of_5

    hunger_rate, reproduction_time = 0, 0
    while hunger_rate <= reproduction_time * .001:
        hunger_rate = random.uniform(3, 12)
        reproduction_time = random.randint(3000, 7000)

    return (size, speed, hunger_rate, reproduction_time)


runs = 10
best_time = 0
while runs > 0:
    prey_size, prey_speed, prey_hunger_rate, prey_reproduction_time = generate_parameters()
    predator_size, predator_speed, predator_hunger_rate, predator_reproduction_time = generate_parameters()

    # Initialize the game
    foods = [Food() for _ in range(FOOD_COUNT)]
    prey = [spawn_prey(size=prey_size, speed=prey_speed, hunger_rate=prey_hunger_rate,
                       reproduction_time=prey_reproduction_time) for _ in range(PREY_COUNT)]
    predators = [spawn_predator(size=predator_size, speed=predator_speed, hunger_rate=predator_hunger_rate,
                                reproduction_time=predator_reproduction_time)]
    last_predator_spawn = pygame.time.get_ticks()

    # Variables to record the number of alive prey and predators
    time_elapsed = 0
    prey_count_history = []
    predator_count_history = []

    running = True
    while running:
        dt = clock.tick(60)
        time_elapsed += dt
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update and draw food
        for food in foods:
            food.draw()

        # Update and draw prey
        new_prey = []
        for cell in prey[:]:
            cell.update(dt)
            if not cell.alive:
                prey.remove(cell)
            else:
                new_prey.append(cell)
                new_prey.extend(cell.reproduce())
                cell.draw()
        prey = new_prey

        # Update and draw predator
        new_predators = []
        for predator in predators[:]:
            predator.update(dt)
            if not predator.alive:
                predators.remove(predator)
            else:
                new_predators.append(predator)
                new_predators.extend(predator.reproduce())
                predator.draw()
        predators = new_predators

        # Record the number of alive prey and predators every second
        if time_elapsed >= 1000:
            prey_count_history.append(len(prey))
            predator_count_history.append(len(predators))
            time_elapsed = 0

        # Check if all prey or predators are dead
        if not prey or not predators:
            running = False

        pygame.display.flip()
    runs -= 1

    if len(prey_count_history) > best_time:
        best_time = len(prey_count_history)
        print(f"New best time! {best_time}")
        print(
            f"prey: {[prey_size, prey_speed, prey_hunger_rate, prey_reproduction_time]}, predator: {[predator_size, predator_speed, predator_hunger_rate, predator_reproduction_time]}")


    # Plot the number of alive prey and predators over time
    plt.plot(prey_count_history, label='Prey')
    plt.plot(predator_count_history, label='Predators')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Number Alive')
    plt.title(
        f"prey: {[prey_size, prey_speed, prey_hunger_rate, prey_reproduction_time]}, predator: {[predator_size, predator_speed, predator_hunger_rate, predator_reproduction_time]}")
    plt.legend()
    plt.savefig(f"run_{runs}.png")
pygame.quit()
