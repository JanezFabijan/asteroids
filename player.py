from circleshape import CircleShape
from constants import PLAYER_FLASH_DURATION, PLAYER_FLASH_INTERVAL_SECONDS, PLAYER_LIVES, PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_SPEED, SHOT_RADIUS, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS
import pygame
from shot import Shot


class Player(CircleShape):
    
    def __init__(self, x: int, y: int):
        super().__init__(x,y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_cooldown = 0.0
        self.lives = PLAYER_LIVES
        self.invulnerable = False
        self.flash_timer = 0.0
        self.flash_interval = 0.0
        self.visible = True

    def take_hit(self) -> None:
        if self.invulnerable:
            return
        self.lives = max(0, self.lives - 1)
        self.invulnerable = True
        self.flash_timer = PLAYER_FLASH_DURATION
        self.flash_interval = PLAYER_FLASH_INTERVAL_SECONDS
        self.visible = False

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        if not self.visible:
            return
        points = self.triangle()
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)
    

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        self.shoot_cooldown -= dt

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

        if self.invulnerable:
            self.flash_timer -= dt
            self.flash_interval -= dt
            if self.flash_interval <= 0:
                self.visible = not self.visible
                self.flash_interval += PLAYER_FLASH_INTERVAL_SECONDS
            if self.flash_timer <= 0:
                self.invulnerable = False
                self.visible = True

    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        if self.shoot_cooldown > 0:
            return

        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED