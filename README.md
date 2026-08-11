# Cubulus

Cubulus is a small territory game built with Python and Pygame.

## Controls

- Main menu: use the mouse or `WASD` / arrow keys to select options
- Main menu: `Enter` confirms, `M` changes the mode, `C` changes the color
- `WASD` or arrow keys: choose a direction; with automatic movement enabled,
  the player keeps moving until another direction is chosen
- Mouse wheel or `+` / `-`: smoothly zoom the camera
- `0`: reset the zoom
- `Esc`: open or close the pause menu during a match

The main menu includes a separate AI-vs-AI arena. Four bots pursue one another,
claim territory, fight on contact, and automatically begin a new round when a
winner remains. This simulation is decorative and does not change the player's
match state.

The camera follows the human player smoothly. Its zoom range, speed, colors,
and initial scale can be adjusted in `config.py`. The match uses the same dark
tactical arena, translucent cards, blue accents, and compact live scores as the
main menu, with the board continuing behind the floating HUD.

A collision with a stronger opponent costs one life. After taking damage, the
player briefly becomes invulnerable and returns to the spawn point. Losing all
three lives opens the Game Over screen; press `Enter` there to start again.

Automatic movement is enabled by default and can be switched on or off from
the Options screen in either the main menu or pause menu. When it is disabled,
each movement key press advances the player by one tile.

The Options screen also provides a selection of common window resolutions.
All options, as well as the selected game mode and player color, are saved
automatically and restored the next time the game starts. On Windows the file
is stored at `%APPDATA%\Cubulus\settings.json`; on Linux and macOS it is stored
below `$XDG_CONFIG_HOME/cubulus` (or `~/.config/cubulus`).

Debug mode unlocks a gameplay speed control with `0.25x`, `0.5x`, `1x`, `2x`,
and `4x` simulation rates. The multiplier affects movement, bots, match timers,
camera updates, and damage cooldowns. A badge in the top-right corner shows
when debug mode is active. The decorative AI arena in the main menu remains at
normal speed.

The redesigned pause menu keeps the frozen arena visible behind a dark glass
overlay. It freezes the match timer and damage cooldowns, shows a compact match
summary, and can resume the match, open the shared options, return to the main
menu, or quit the game.
