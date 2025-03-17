import pygame
import random
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 800, 800
FOOD_RESPAWN_TIME = 5000
FOOD_COUNT = 64
PREY_COUNT = 32
PREDATOR_SPAWN_TIME = 10000
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
    def __init__(self, x, y, size, speed, hunger_rate, reproduction_time, is_predator=False, foods=None, predators=None, prey=None):
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
        self.foods = foods if foods is not None else []
        self.predators = predators if predators is not None else []
        self.prey = prey if prey is not None else []

    def move(self):
        dx, dy = 0, 0
        if self.is_predator:
            if self.prey:
                closest_prey = min(self.prey, key=lambda p: (p.x - self.x) ** 2 + (p.y - self.y) ** 2)
                dx, dy = closest_prey.x - self.x, closest_prey.y - self.y
        else:
            if self.foods and self.predators:
                closest_predator = min(self.predators, key=lambda p: (p.x - self.x) ** 2 + (p.y - self.y) ** 2)
                best_food = min(self.foods, key=lambda f: (f.x - self.x) ** 2 + (f.y - self.y) ** 2 - ((f.x - closest_predator.x) ** 2 + (f.y - closest_predator.y) ** 2))
                dx, dy = best_food.x - self.x, best_food.y - self.y
            elif self.foods:
                closest_food = min(self.foods, key=lambda f: (f.x - self.x) ** 2 + (f.y - self.y) ** 2)
                dx, dy = closest_food.x - self.x, closest_food.y - self.y
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.x += int(self.speed * dx / dist)
        self.y += int(self.speed * dy / dist)

    def eat(self):
        if self.is_predator:
            for p in self.prey[:]:
                if abs(self.x - p.x) < self.size and abs(self.y - p.y) < self.size:
                    self.energy = min(100, self.energy + 50)
                    self.prey.remove(p)
                    self.eaten_count += 1
                    self.size += 2
        else:
            for food in self.foods:
                if abs(self.x - food.x) < self.size and abs(self.y - food.y) < self.size:
                    self.energy = min(100, self.energy + 50)
                    quarter = 1 if food.x < WIDTH // 2 and food.y < HEIGHT // 2 else 2 if food.x >= WIDTH // 2 and food.y < HEIGHT // 2 else 3 if food.x < WIDTH // 2 and food.y >= HEIGHT // 2 else 4
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
            return [Cell(self.x + offset * plus_or_minus_x, self.y + offset * plus_or_minus_y, self.base_size, self.speed, self.hunger_rate, self.reproduction_time, self.is_predator, self.foods, self.predators)]
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


def fitness(prey_params, predator_params):
    foods = [Food() for _ in range(FOOD_COUNT)]
    prey = [Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), size=prey_params[0], speed=prey_params[1], hunger_rate=prey_params[2], reproduction_time=prey_params[3], foods=foods, predators=None) for _ in range(PREY_COUNT)]
    predators = [Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), size=predator_params[0], speed=predator_params[1], hunger_rate=predator_params[2], reproduction_time=predator_params[3], is_predator=True, foods=foods, predators=prey)]
    last_predator_spawn = pygame.time.get_ticks()
    time_elapsed = 0
    prey_count_history = []
    predator_count_history = []
    running = True
    while running:
        dt = clock.tick(60)
        time_elapsed += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for food in foods:
            food.draw()
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
        if time_elapsed >= 1000:
            prey_count_history.append(len(prey))
            predator_count_history.append(len(predators))
            time_elapsed = 0
        if not prey or not predators:
            running = False
        pygame.display.flip()
    return len(prey_count_history)


def crossover(parent1, parent2):
    child = []
    for p1, p2 in zip(parent1, parent2):
        child.append(random.choice([p1, p2]))
    return tuple(child)


def mutate(params):
    size, speed, hunger_rate, reproduction_time = params
    size += random.randint(-1, 1)
    speed += random.uniform(-0.1, 0.1)
    hunger_rate += random.uniform(-0.5, 0.5)
    reproduction_time += random.randint(-500, 500)
    return (size, speed, hunger_rate, reproduction_time)


population_size = 20
generations = 50
mutation_rate = 0.1
population = [(generate_parameters(), generate_parameters()) for _ in range(population_size)]
for generation in range(generations):
    fitness_scores = [(fitness(prey, predator), prey, predator) for prey, predator in population]
    fitness_scores.sort(reverse=True, key=lambda x: x[0])
    selected = fitness_scores[:population_size // 2]
    new_population = []
    for i in range(population_size // 2):
        for j in range(i + 1, population_size // 2):
            parent1 = selected[i][1], selected[i][2]
            parent2 = selected[j][1], selected[j][2]
            child1 = crossover(parent1[0], parent2[0]), crossover(parent1[1], parent2[1])
            child2 = crossover(parent2[0], parent1[0]), crossover(parent2[1], parent1[1])
            new_population.extend([child1, child2])
    population = []
    for prey, predator in new_population:
        if random.random() < mutation_rate:
            prey = mutate(prey)
        if random.random() < mutation_rate:
            predator = mutate(predator)
        population.append((prey, predator))
best_prey, best_predator = fitness_scores[0][1], fitness_scores[0][2]
print(f"Best prey settings: {best_prey}")
print(f"Best predator settings: {best_predator}")
pygame.quit()
