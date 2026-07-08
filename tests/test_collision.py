import unittest

from circleshape import circle_intersects_polygon
import pygame
from player_ship_shape import build_player_ship_polygon_from_surface


class CirclePolygonCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_circle_outside_polygon_returns_false(self):
        polygon = [
            pygame.Vector2(0, -20),
            pygame.Vector2(15, 10),
            pygame.Vector2(-15, 10),
        ]
        self.assertFalse(circle_intersects_polygon(pygame.Vector2(100, 100), 3, polygon))

    def test_circle_touching_polygon_returns_true(self):
        polygon = [
            pygame.Vector2(0, -20),
            pygame.Vector2(15, 10),
            pygame.Vector2(-15, 10),
        ]
        self.assertTrue(circle_intersects_polygon(pygame.Vector2(15, 10), 1, polygon))

    def test_build_player_ship_polygon_from_surface_returns_outline_points(self):
        surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.polygon(
            surface,
            (255, 255, 255, 255),
            [(40, 5), (65, 60), (40, 50), (15, 60)],
        )

        polygon = build_player_ship_polygon_from_surface(surface, fallback_radius=20)

        self.assertGreaterEqual(len(polygon), 3)
        self.assertTrue(any(point.y < 0 for point in polygon))
        self.assertTrue(any(point.y > 0 for point in polygon))

    def test_build_player_ship_polygon_from_surface_falls_back_for_empty_surface(self):
        surface = pygame.Surface((80, 80), pygame.SRCALPHA)

        polygon = build_player_ship_polygon_from_surface(surface, fallback_radius=20)

        self.assertEqual(len(polygon), 7)


if __name__ == "__main__":
    unittest.main()
