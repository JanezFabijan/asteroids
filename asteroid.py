from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
import pygame
from logger import log_event
import random

ASTEROID_BASE_IMAGE = None

def get_asteroid_base_image():
    global ASTEROID_BASE_IMAGE
    if ASTEROID_BASE_IMAGE is None:
        loaded = pygame.image.load("assets/images/asteroid.png").convert()
        bg_color = loaded.get_at((0, 0))[:3]
        loaded.set_colorkey(bg_color)
        ASTEROID_BASE_IMAGE = loaded
    return ASTEROID_BASE_IMAGE

class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        base_image = get_asteroid_base_image()
        diameter = max(1, int(radius * 2))
        self.image = pygame.transform.smoothscale(base_image, (diameter, diameter))
        self.image.set_colorkey(base_image.get_colorkey())
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        self.rect.center = self.position
        screen.blit(self.image, self.rect)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
    
    def split(self) -> int:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return 100
        
        log_event("asteroid_split")
        random_offset = random.uniform(20, 50)
        asteroid_1_rotation = self.velocity.rotate(random_offset)
        asteroid_2_rotation = self.velocity.rotate(-random_offset)
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)

        asteroid_1.velocity = asteroid_1_rotation * 1.2
        asteroid_2.velocity = asteroid_2_rotation * 1.2
        return 0
