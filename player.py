from circleshape import CircleShape
from constants import PLAYER_FLASH_DURATION, PLAYER_FLASH_INTERVAL_SECONDS, PLAYER_LIVES, PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_SPEED, SHOT_RADIUS, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS
import pygame
from shot import Shot

PLAYER_FIGHTER_IMAGE = None

def get_player_fighter_image():
    global PLAYER_FIGHTER_IMAGE
    if PLAYER_FIGHTER_IMAGE is None:
        image = pygame.image.load("assets/images/fighter.png").convert()
        bg_color = image.get_at((0, 0))[:3]
        image.set_colorkey(bg_color)
        image = pygame.transform.flip(image, False, True)
        PLAYER_FIGHTER_IMAGE = image
    return PLAYER_FIGHTER_IMAGE


class Player(CircleShape):
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.front_shoot_cooldown = 0.0
        self.rear_shoot_cooldown = 0.0
        self.lives = PLAYER_LIVES
        self.invulnerable = False
        self.flash_timer = 0.0
        self.flash_interval = 0.0
        self.visible = True
        self.base_image = pygame.transform.smoothscale(get_player_fighter_image(), (int(self.radius * 4), int(self.radius * 4)))
        self.base_image.set_colorkey(self.base_image.get_at((0, 0))[:3])
        self.image = self.base_image
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def take_hit(self) -> None:
        if self.invulnerable:
            return
        self.lives = max(0, self.lives - 1)
        self.invulnerable = True
        self.flash_timer = PLAYER_FLASH_DURATION
        self.flash_interval = PLAYER_FLASH_INTERVAL_SECONDS
        self.visible = False

    def draw(self, screen):
        if not self.visible:
            return
        screen.blit(self.image, self.rect)
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
        self._update_image()
    
    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        self.front_shoot_cooldown -= dt
        self.rear_shoot_cooldown -= dt

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot(self.front_cannon_offsets(), (255, 0, 0), front=True)
        if keys[pygame.K_x]:
            self.shoot(self.rear_cannon_offsets(), (0, 255, 0), front=False)

        self.rect.center = self.position

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
        self.rect.center = self.position

    def _update_image(self) -> None:
        self.image = pygame.transform.rotozoom(self.base_image, -self.rotation, 1)
        bg_color = self.base_image.get_at((0, 0))[:3]
        self.image.set_colorkey(bg_color)
        self.rect = self.image.get_rect(center=self.position)
        self.mask = pygame.mask.from_surface(self.image)

    def shoot(self, offsets, color=(255, 255, 255), front=True):
        if front:
            if self.front_shoot_cooldown > 0:
                return
            self.front_shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        else:
            if self.rear_shoot_cooldown > 0:
                return
            self.rear_shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS

        forward = pygame.Vector2(0, 1).rotate(self.rotation)

        for offset in offsets:
            shot_pos = self.position + offset
            shot = Shot(shot_pos.x, shot_pos.y, SHOT_RADIUS, self.rotation, color)
            shot.velocity = forward * PLAYER_SHOOT_SPEED

    def front_cannon_offsets(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = forward.rotate(-90)
        return [
            forward * self.radius * 0.9 + right * self.radius * 0.6,
            forward * self.radius * 0.9 - right * self.radius * 0.6,
        ]

    def rear_cannon_offsets(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = forward.rotate(-90)
        return [
            forward * self.radius * 0.4 + right * self.radius * 1.0,
            forward * self.radius * 0.4 - right * self.radius * 1.0,
        ]
