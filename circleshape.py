import math
import pygame


def point_in_polygon(point: pygame.Vector2, polygon: list[pygame.Vector2]) -> bool:
    x, y = point.x, point.y
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i].x, polygon[i].y
        x2, y2 = polygon[(i + 1) % n].x, polygon[(i + 1) % n].y
        if ((y1 > y) != (y2 > y)):
            xinters = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xinters:
                inside = not inside
    return inside


def point_to_segment_distance(point: pygame.Vector2, a: pygame.Vector2, b: pygame.Vector2) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    if dx == 0 and dy == 0:
        return math.hypot(point.x - a.x, point.y - a.y)

    t = ((point.x - a.x) * dx + (point.y - a.y) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    projection = pygame.Vector2(a.x + t * dx, a.y + t * dy)
    return math.hypot(point.x - projection.x, point.y - projection.y)


def circle_intersects_polygon(center: pygame.Vector2, radius: float, polygon: list[pygame.Vector2]) -> bool:
    if not polygon:
        return False

    if point_in_polygon(center, polygon):
        return True

    for index in range(len(polygon)):
        start = polygon[index]
        end = polygon[(index + 1) % len(polygon)]
        if point_to_segment_distance(center, start, end) <= radius:
            return True

    return False


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
        self_polygon = getattr(self, "collision_polygon", None)
        other_polygon = getattr(other, "collision_polygon", None)

        if self_polygon and hasattr(other, "position") and hasattr(other, "radius"):
            return circle_intersects_polygon(other.position, other.radius, self_polygon)

        if other_polygon and hasattr(self, "position") and hasattr(self, "radius"):
            return circle_intersects_polygon(self.position, self.radius, other_polygon)

        if hasattr(self, "mask") and self.mask is not None and hasattr(other, "mask") and other.mask is not None:
            if hasattr(self, "rect") and hasattr(other, "rect"):
                offset = (int(other.rect.left - self.rect.left), int(other.rect.top - self.rect.top))
                return self.mask.overlap(other.mask, offset) is not None

        if hasattr(self, "collision_radius"):
            r1 = self.collision_radius
        else:
            r1 = self.radius

        if hasattr(other, "collision_radius"):
            r2 = other.collision_radius
        else:
            r2 = getattr(other, "radius", 0)

        distance = self.position.distance_to(other.position)
        return distance <= (r1 + r2)
