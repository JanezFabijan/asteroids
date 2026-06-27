from circleshape import CircleShape
import pygame
from constants import ASTEROID_MAX_RADIUS


class Shot(CircleShape):
    def __init__(self, x: float, y: float, radius: float, rotation: float = 0.0, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        super().__init__(x, y, radius)
        self.rotation = rotation
        self.color = color
        self.length = max(30, int(self.radius * 8))
        self.width = max(1, int(self.radius * 0.4))
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def _create_image(self):
        size = self.length + self.width * 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = pygame.Vector2(size // 2, size // 2)
        start = center - pygame.Vector2(0, self.length / 2)
        end = center + pygame.Vector2(0, self.length / 2)
        pygame.draw.line(surface, self.color, start, end, self.width)
        image = pygame.transform.rotozoom(surface, -self.rotation, 1)
        return image

    def draw(self, screen):
        self.rect.center = self.position
        screen.blit(self.image, self.rect)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position


class Missile(Shot):
    def __init__(self, x: float, y: float, radius: float, rotation: float = 0.0, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        super().__init__(x, y, radius, rotation, color)
        self.exploded = False

    def _create_image(self):
        size = self.length + self.width * 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = pygame.Vector2(size // 2, size // 2)
        nose = center + pygame.Vector2(0, self.length / 2)
        tail = center - pygame.Vector2(0, self.length / 2)
        pygame.draw.line(surface, self.color, tail, nose, self.width)
        pygame.draw.circle(surface, self.color, (int(center.x), int(center.y)), max(2, self.width), 0)
        return pygame.transform.rotozoom(surface, -self.rotation, 1)


class Explosion(CircleShape):
    def __init__(self, x: float, y: float, radius: float, color: tuple[int, int, int] = (255, 140, 0)) -> None:
        super().__init__(x, y, radius)
        self.color = color
        self.duration = 0.25
        self.age = 0.0

    def draw(self, screen):
        alpha = max(0, int(255 * max(0.0, 1 - self.age / self.duration)))
        surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        center = (int(self.radius), int(self.radius))
        pygame.draw.circle(surface, (*self.color, alpha), center, int(self.radius))
        pygame.draw.circle(surface, (255, 255, 255, alpha // 2), center, int(self.radius), max(2, int(self.radius * 0.08)))
        screen.blit(surface, (self.position.x - self.radius, self.position.y - self.radius))

    def update(self, dt):
        self.age += dt
        if self.age >= self.duration:
            self.kill()