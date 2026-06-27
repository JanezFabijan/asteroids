import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_MAX_RADIUS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
import sys
from shot import Shot, Missile, Explosion

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)

    # Load background image and scale to screen size
    bg_image = pygame.image.load("assets/images/asteroid_background.png").convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()
    dt = 0.0

    def create_button_rect(center, width=260, height=80):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = center
        return rect

    def draw_button(label, center):
        button_rect = create_button_rect(center)
        pygame.draw.rect(screen, "black", button_rect)
        pygame.draw.rect(screen, "white", button_rect, 3)
        button_text = font.render(label, True, "white")
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))
        return button_rect

    def reset_game():
        nonlocal score, player, asteroidField, updatable, drawable, asteroids, shots, state
        score = 0
        state = "playing"

        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        shots = pygame.sprite.Group()

        Player.containers = (updatable, drawable)
        Asteroid.containers = (asteroids, updatable, drawable)
        Shot.containers = (shots, updatable, drawable)
        Missile.containers = (shots, updatable, drawable)
        Explosion.containers = (updatable, drawable)
        AsteroidField.containers = (updatable)

        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        asteroidField = AsteroidField()

    score = 0
    state = "menu"
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    player = None
    asteroidField = None

    play_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
    replay_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu" and play_button_rect.collidepoint(event.pos):
                    reset_game()
                elif state == "game_over" and replay_button_rect.collidepoint(event.pos):
                    reset_game()

        if state == "playing":
            updatable.update(dt)

            for asteroid in asteroids:
                if asteroid.collides_with(player) and not player.invulnerable:
                    log_event("player_hit")
                    player.take_hit()
                    asteroid.kill()
                    if player.lives <= 0:
                        state = "game_over"
                        break

            for asteroid in list(asteroids):
                for shot in list(shots):
                    if asteroid.collides_with(shot):
                        if isinstance(shot, Missile):
                            log_event("missile_impact")
                            score += 100
                            shot.kill()
                            asteroid.kill()
                            Explosion(asteroid.position.x, asteroid.position.y, ASTEROID_MAX_RADIUS)
                            for nearby_asteroid in list(asteroids):
                                if nearby_asteroid.alive() and nearby_asteroid.position.distance_to(asteroid.position) <= ASTEROID_MAX_RADIUS:
                                    nearby_asteroid.kill()
                        else:
                            log_event("asteroid_shot")
                            score += asteroid.split()
                            shot.kill()
                        break

        screen.blit(bg_image, (0, 0))

        if state == "menu":
            title_surface = font.render("Asteroids", True, "white")
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
            screen.blit(title_surface, title_rect)
            play_button_rect = draw_button("Play", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
        elif state == "game_over":
            for element in drawable:
                element.draw(screen)
            game_over_surface = font.render("GAME OVER", True, "red")
            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
            screen.blit(game_over_surface, game_over_rect)
            replay_button_rect = draw_button("Replay", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
        else:
            for element in drawable:
                element.draw(screen)
            score_surface = font.render(f"Score: {score}", True, "white")
            screen.blit(score_surface, (10, 10))
            lives_surface = font.render(
                f"Lives: {'♥' * player.lives}", True, "white"
            )
            screen.blit(lives_surface, (10, 50))

        pygame.display.flip()

        game_time = clock.tick(60)
        dt = game_time / 1000

    # print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    # print(f"Screen width: {SCREEN_WIDTH}")
    # print(f"Screen height: {SCREEN_HEIGHT}")


if __name__ == "__main__":
    main()
