import pygame


PLAYER_SHIP_POLYGON_TARGET_POINTS = 24
PLAYER_SHIP_POLYGON_EPSILON = 2.5
PLAYER_SHIP_MASK_ALPHA_THRESHOLD = 32
PLAYER_SHIP_COLORKEY_TOLERANCE = 4


def _rdp(points: list[pygame.Vector2], epsilon: float) -> list[pygame.Vector2]:
    if len(points) < 3:
        return points[:]

    start = points[0]
    end = points[-1]
    line = end - start
    line_length = line.length()

    max_distance = -1.0
    split_index = -1
    for index in range(1, len(points) - 1):
        point = points[index]
        if line_length == 0:
            distance = point.distance_to(start)
        else:
            distance = abs((point.x - start.x) * line.y - (point.y - start.y) * line.x) / line_length

        if distance > max_distance:
            max_distance = distance
            split_index = index

    if max_distance <= epsilon or split_index == -1:
        return [start, end]

    left = _rdp(points[: split_index + 1], epsilon)
    right = _rdp(points[split_index:], epsilon)
    return left[:-1] + right


def _dedupe_points(points: list[pygame.Vector2], minimum_spacing: float = 1.0) -> list[pygame.Vector2]:
    if not points:
        return []

    deduped = [points[0]]
    for point in points[1:]:
        if point.distance_to(deduped[-1]) >= minimum_spacing:
            deduped.append(point)

    if len(deduped) > 1 and deduped[0].distance_to(deduped[-1]) < minimum_spacing:
        deduped.pop()

    return deduped


def fallback_player_ship_polygon(radius: float) -> list[pygame.Vector2]:
    scale = radius * 1.15
    return [
        pygame.Vector2(0, -scale * 1.2),
        pygame.Vector2(scale * 0.55, -scale * 0.25),
        pygame.Vector2(scale * 0.9, scale * 0.7),
        pygame.Vector2(scale * 0.35, scale * 1.1),
        pygame.Vector2(-scale * 0.35, scale * 1.1),
        pygame.Vector2(-scale * 0.9, scale * 0.7),
        pygame.Vector2(-scale * 0.55, -scale * 0.25),
    ]


def _matches_colorkey(color: pygame.Color, colorkey: pygame.Color | tuple[int, ...] | None) -> bool:
    if colorkey is None:
        return False

    key = colorkey if isinstance(colorkey, pygame.Color) else pygame.Color(*colorkey)
    return all(abs(color[index] - key[index]) <= PLAYER_SHIP_COLORKEY_TOLERANCE for index in range(3))


def _visible_mask(surface: pygame.Surface, alpha_threshold: int) -> pygame.Mask:
    colorkey = surface.get_colorkey()
    if colorkey is None:
        return pygame.mask.from_surface(surface, threshold=alpha_threshold)

    mask = pygame.Mask(surface.get_size())
    width, height = surface.get_size()
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            if color.a >= alpha_threshold and not _matches_colorkey(color, colorkey):
                mask.set_at((x, y), 1)

    return mask


def _mask_bounds(mask: pygame.Mask) -> pygame.Rect | None:
    rects = mask.get_bounding_rects()
    if not rects:
        return None

    bounds = rects[0].copy()
    for rect in rects[1:]:
        bounds.union_ip(rect)
    return bounds


def build_player_ship_polygon_from_surface(
    surface: pygame.Surface,
    fallback_radius: float,
    target_points: int = PLAYER_SHIP_POLYGON_TARGET_POINTS,
    epsilon: float = PLAYER_SHIP_POLYGON_EPSILON,
    alpha_threshold: int = PLAYER_SHIP_MASK_ALPHA_THRESHOLD,
) -> list[pygame.Vector2]:
    mask = _visible_mask(surface, alpha_threshold)
    bounds = _mask_bounds(mask)
    if bounds is None or bounds.width < 2 or bounds.height < 2:
        return fallback_player_ship_polygon(fallback_radius)

    outline = mask.outline()
    if len(outline) < 3:
        return fallback_player_ship_polygon(fallback_radius)

    step = max(1, len(outline) // target_points)
    sampled_points = [pygame.Vector2(point) for point in outline[::step]]
    if sampled_points[-1] != pygame.Vector2(outline[-1]):
        sampled_points.append(pygame.Vector2(outline[-1]))

    simplified_points = _dedupe_points(_rdp(sampled_points, epsilon))
    if len(simplified_points) < 3:
        return fallback_player_ship_polygon(fallback_radius)

    center = pygame.Vector2(surface.get_width() / 2, surface.get_height() / 2)
    return [point - center for point in simplified_points]
