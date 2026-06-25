import pygame

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        # must override
        pass

    def update(self, dt: float) -> None:
        # must override
        pass
    
    def collides_with(self, other) -> bool:
        if hasattr(self, "mask") and self.mask is not None and hasattr(other, "mask") and other.mask is not None:
            if hasattr(self, "rect") and hasattr(other, "rect"):
                offset = (int(other.rect.left - self.rect.left), int(other.rect.top - self.rect.top))
                return self.mask.overlap(other.mask, offset) is not None
        r1 = self.radius
        r2 = getattr(other, "radius", 0)
        distance = self.position.distance_to(other.position)
        return distance <= (r1 + r2)
