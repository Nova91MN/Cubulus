# Cubulus

Cubulus is a small territory game built with Python and Pygame.

## Controls

- `WASD` or arrow keys: move
- Mouse wheel or `+` / `-`: smoothly zoom the camera
- `0`: reset the zoom
- `Esc`: quit

The camera follows the human player smoothly. Its zoom range, speed, HUD sizes,
colors, and initial scale can be adjusted in `config.py`.

A collision with a stronger opponent costs one life. After taking damage, the
player briefly becomes invulnerable and returns to the spawn point. Losing all
three lives opens the Game Over screen; press `Enter` there to start again.
