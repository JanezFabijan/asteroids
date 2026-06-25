from circleshape import CircleShape
import pygame
from constants import LINE_WIDTH, PLAYER_SHOOT_SPEED

class Shot(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        diameter = max(1, int(radius * 2))
        self.rect = pygame.Rect(0, 0, diameter, diameter)
        self.rect.center = self.position
        self.mask = self._create_mask()

    def _create_mask(self):
        diameter = max(1, int(self.radius * 2))
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (diameter // 2, diameter // 2), self.radius)
        return pygame.mask.from_surface(surface)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position