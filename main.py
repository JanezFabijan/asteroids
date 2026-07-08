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
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    render_scale = 1
    scaled_width = max(1, int(SCREEN_WIDTH * render_scale))
    scaled_height = max(1, int(SCREEN_HEIGHT * render_scale))
    offset_x = (screen_width - scaled_width) // 2
    offset_y = (screen_height - scaled_height) // 2
    font_size = max(64, int(32 * render_scale))
    small_font_size = max(64, int(24 * render_scale))
    font = pygame.font.Font(None, font_size)
    small_font = pygame.font.Font(None, small_font_size)

    def to_world_pos(pos):
        x = (pos[0] - offset_x) / render_scale
        y = (pos[1] - offset_y) / render_scale
        return (x, y)

    # Load background image and scale to the logical game size
    bg_image = pygame.image.load("assets/images/asteroid_background.png").convert()
    bg_image = pygame.transform.smoothscale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()
    dt = 0.0

    def create_button_rect(center, width=260, height=80):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = center
        return rect

    def draw_button(label, center):
        button_rect = create_button_rect(center)
        pygame.draw.rect(world_surface, "black", button_rect)
        pygame.draw.rect(world_surface, "white", button_rect, 3)
        button_text = font.render(label, True, "white")
        world_surface.blit(button_text, button_text.get_rect(center=button_rect.center))
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
    paused = False
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    player = None
    asteroidField = None

    play_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
    exit_menu_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200))
    replay_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
    exit_game_over_button_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200))
    pause_restart_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20), width=260, height=70)
    pause_close_rect = create_button_rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70), width=260, height=70)

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "playing":
                        paused = True
                        state = "paused"
                    elif state == "paused":
                        paused = False
                        state = "playing"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                world_pos = to_world_pos(event.pos)
                if state == "menu":
                    if play_button_rect.collidepoint(world_pos):
                        reset_game()
                    elif exit_menu_button_rect.collidepoint(world_pos):
                        return
                elif state == "game_over":
                    if replay_button_rect.collidepoint(world_pos):
                        reset_game()
                    elif exit_game_over_button_rect.collidepoint(world_pos):
                        return
                elif state == "paused":
                    if pause_restart_rect.collidepoint(world_pos):
                        reset_game()
                    elif pause_close_rect.collidepoint(world_pos):
                        return

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
                            explosion = Explosion(asteroid.position.x, asteroid.position.y, ASTEROID_MAX_RADIUS)
                            for nearby_asteroid in list(asteroids):
                                if nearby_asteroid.alive() and nearby_asteroid.position.distance_to(asteroid.position) <= ASTEROID_MAX_RADIUS:
                                    nearby_asteroid.kill()
                            if player and player.position.distance_to(explosion.position) <= explosion.radius and not player.invulnerable:
                                player.take_hit()
                                if player.lives <= 0:
                                    state = "game_over"
                        else:
                            log_event("asteroid_shot")
                            score += asteroid.split()
                            shot.kill()
                        break

        world_surface.fill((0, 0, 0))
        world_surface.blit(bg_image, (0, 0))

        if state == "menu":
            title_surface = font.render("Asteroids", True, "white")
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
            world_surface.blit(title_surface, title_rect)
            play_button_rect = draw_button("Play", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
            exit_menu_button_rect = draw_button("Exit", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140))
        elif state == "paused":
            for element in drawable:
                element.draw(world_surface)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            world_surface.blit(overlay, (0, 0))
            pause_title = font.render("Paused", True, "white")
            world_surface.blit(pause_title, pause_title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90)))
            pause_restart_rect = draw_button("Restart", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20))
            pause_close_rect = draw_button("Exit", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70))
        elif state == "game_over":
            for element in drawable:
                element.draw(world_surface)
            game_over_surface = font.render("GAME OVER", True, "red")
            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
            world_surface.blit(game_over_surface, game_over_rect)
            replay_button_rect = draw_button("Restart", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
            exit_game_over_button_rect = draw_button("Exit", (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140))
        else:
            for element in drawable:
                element.draw(world_surface)
            score_surface = small_font.render(f"Score: {score}", True, "white")
            world_surface.blit(score_surface, (10, 10))
            lives_surface = small_font.render(
                f"Lives: {'♥' * player.lives}", True, "white"
            )
            world_surface.blit(lives_surface, (10, 40))

        scaled_surface = pygame.transform.smoothscale(world_surface, (scaled_width, scaled_height))
        screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()

        game_time = clock.tick(60)
        dt = game_time / 1000

    # print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    # print(f"Screen width: {SCREEN_WIDTH}")
    # print(f"Screen height: {SCREEN_HEIGHT}")


if __name__ == "__main__":
    main()
