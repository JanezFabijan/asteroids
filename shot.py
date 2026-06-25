from circleshape import CircleShape
import pygame
from constants import PLAYER_SHOOT_SPEED

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