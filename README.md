# Asteroids

This project is intended to run with `uv`.

## Run

Use:

```bash
uv run main.py
```

## Modules

### `main.py`

Application entry point. It:

- Initializes `pygame`, the window, font, clock, and score state.
- Creates sprite groups for updating, drawing, asteroids, and shots.
- Wires sprite container groups onto `Player`, `Asteroid`, `Shot`, and `AsteroidField`.
- Runs the main loop, updates sprites, checks collisions, updates score, renders the scene, and exits on player death or window close.
- Calls `logger.log_state()` every frame and emits gameplay events through `logger.log_event()`.

### `player.py`

Defines the `Player` sprite, which inherits from `CircleShape`. It:

- Tracks ship rotation and a shooting cooldown.
- Draws the player as a triangle.
- Handles keyboard input in `update()`.
- Rotates with `A` and `D`.
- Moves forward and backward with `W` and `S`.
- Fires shots with `Space`.

### `asteroid.py`

Defines the `Asteroid` sprite. It:

- Draws an asteroid as a circle outline.
- Moves based on its velocity.
- Splits large asteroids into two smaller asteroids when hit.
- Awards `100` points when the asteroid is already at the minimum radius.
- Logs the `asteroid_split` event when a split happens.

### `asteroidfield.py`

Defines the `AsteroidField` spawner. It:

- Tracks time between spawns.
- Chooses a random screen edge for each new asteroid.
- Generates asteroid size, position, and velocity with random variation.
- Spawns asteroids at the configured interval from `constants.py`.

### `circleshape.py`

Defines the base `CircleShape` sprite class shared by round game objects. It:

- Stores `position`, `velocity`, and `radius`.
- Auto-registers sprites into configured `pygame` groups through `containers`.
- Provides `draw()` and `update()` placeholders for subclasses.
- Implements circle-based collision detection with `collides_with()`.

### `shot.py`

Defines the projectile fired by the player. It:

- Inherits from `CircleShape`.
- Draws the shot as a small circle outline.
- Moves according to its velocity each update tick.

### `constants.py`

Stores gameplay and rendering constants, including:

- Screen width and height.
- Player radius, move speed, turn speed, and shoot cooldown.
- Asteroid sizing, number of size variants, and spawn rate.
- Shot radius and projectile speed.
- Shared line width for outlined shapes.

### `logger.py`

Provides lightweight runtime logging helpers:

- `log_state()` captures periodic snapshots of the caller's local game state and writes them to `game_state.jsonl`.
- `log_event()` writes timestamped gameplay events to `game_events.jsonl`.
- Logging is capped to roughly the first 16 seconds for state snapshots.
- Sprite groups are summarized with counts and sampled sprite metadata such as position, velocity, radius, and rotation.
