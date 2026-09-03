# Cubulus 1.1

Cubulus is a small territory game built with Python and Pygame.

## Play Cubulus

### In the browser

[Play Cubulus online](https://nova91mn.github.io/Cubulus/). The first start can
take a moment while the Python/WebAssembly runtime is loaded. The game itself
then runs locally in the browser and needs no installation.

The bundled maps, game modes, controls, pause menu, and level editor work in
the browser. The native **Load custom map** file dialog is desktop-only; maps
created in the browser's level editor remain available for the current browser
session.

Every push to `main` is tested, built with Pygbag, and deployed by the
`Test and deploy browser game` GitHub Actions workflow. For the first
deployment, select **GitHub Actions** as the source under
**Settings → Pages** in the repository.

### On the desktop

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Build the browser version locally

```bash
python -m pip install -r requirements-web.txt
python -X utf8 -m pygbag --build --ume_block 0 --can_close 0 --title Cubulus .
python -m http.server 8000 --directory build/web
```

Then open `http://localhost:8000`. Do not open `build/web/index.html` directly;
WebAssembly assets need to be served over HTTP.

## What's new in 1.1

Version 1.1 makes AI opponents more aware of their territory score. Bots that
fall behind now prioritize claimable tiles and use a shortest-path search to
reach the nearest available territory before resuming normal pursuit. The
release also adds separate Debug controls for infinite lives and player speed.
See the [changelog](CHANGELOG.md) for the full release notes.

## Controls

- Main menu: use the mouse or `WASD` / arrow keys to select options
- Main menu: `Enter` confirms, `M` changes the mode, `C` changes the color
- `WASD` or arrow keys: choose a direction; with automatic movement enabled,
  the player keeps moving until another direction is chosen
- Mouse wheel or `+` / `-`: smoothly zoom the camera
- `0`: reset the zoom
- `Esc`: open or close the pause menu during a match
- Victory / Game Over screen: `Enter` starts a new match; `Esc` returns to the
  main menu without closing the game

## Player name and difficulty

Use **Player name / Spielername** in the main menu to enter a name of up to
16 characters. The name is shown in the match HUD and saved with the other
settings, so it is restored on the next launch.

The **Difficulty / Schwierigkeit** row offers Beginner, Easy, Normal, Hard,
Expert, and God. Higher levels make the bots move more frequently and pursue
the human player more consistently. God uses the Expert AI profile, but all
bots form an alliance against the human player and do not damage one another.
The selected difficulty is also saved automatically.

Every AI opponent receives a randomly selected name at the beginning of each
match. Names are unique within a match and are also refreshed for every round
of the decorative AI arena in the main menu.

The player color menu offers red, yellow, green, blue, purple, orange, cyan,
pink, lime, and teal. The selected color is saved with the other settings.

## Territory mode

Territory mode lets every player conquer tiles that another color has already
marked. Lives are infinite: losing a collision still returns the weaker player
to the spawn point, but never eliminates them. The first color that reaches the
selected map share while holding the unique lead wins:

- Beginner: 2.5%
- Easy: 5%
- Normal: 10%
- Hard: 20%
- Expert: 50%
- God: 75%

Obstacles are excluded when the required tile count is calculated. A bot that
falls well behind prioritizes expansion: it claims an adjacent available tile
or takes a shortest route toward the nearest one before resuming pursuit.

## Language

Open **Options** and change **Language / Sprache** with the left and right
arrow keys (or by clicking the row). The complete interface can be switched
between German and English. The selection is saved automatically.

## Custom maps

Choose **Load custom map / Eigene Map laden** in the main menu and select a
JSON file. Cubulus validates the file before activating it, so a malformed map
does not interrupt the game. The selected file is remembered for the next
start. The **Map / Karte** row can be used to switch between all valid JSON maps
in the bundled `maps` folder and previously loaded custom maps.

A map uses this format:

```json
{
  "name": "My arena",
  "width": 80,
  "height": 60,
  "player_starts": [
    [2, 2],
    [77, 2],
    [2, 57],
    [77, 57]
  ],
  "obstacles": [
    [20, 12],
    [21, 12],
    [22, 12]
  ]
}
```

- `name` is optional; the file name is used when it is omitted.
- `width` and `height` are required integers from 4 through 500.
- `player_starts` is optional. It must contain four unique `[x, y]` positions
  inside the map. If omitted, the four corners are used.
- `obstacles` is optional. Every `[x, y]` entry creates a solid field that
  players and bots cannot enter. Obstacles may not overlap player starts.

## Level editor

Choose **Level editor / Level-Editor** in the main menu to create a map without
editing JSON by hand. Left-click fields to add or remove obstacles; right-click
to erase one. Press `1` through `4`, then click a field, to place the four player
starts. The sidebar changes the level name, width, and height and can clear,
save, or close the editor. Keyboard shortcuts are shown at the bottom.

Saved levels are placed in the `maps` folder next to the Cubulus settings file,
selected immediately, and discovered automatically on future launches.

See `maps/example_custom.json` for a ready-to-edit example.

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
three lives opens the Game Over screen; press `Enter` there to start again or
`Esc` to return to the main menu.

Automatic movement is enabled by default and can be switched on or off from
the Options screen in either the main menu or pause menu. When it is disabled,
each movement key press advances the player by one tile.

The Options screen also provides a selection of common window resolutions.
All options, as well as the selected game mode and player color, are saved
automatically and restored the next time the game starts. On Windows the file
is stored at `%APPDATA%\Cubulus\settings.json`; on Linux and macOS it is stored
below `$XDG_CONFIG_HOME/cubulus` (or `~/.config/cubulus`).

Debug mode unlocks three additional controls:

- **Infinite lives** protects the human player from losing lives. A lost
  collision still triggers the damage feedback, cooldown, and return to the
  spawn point. Bots keep their normal lives.
- **Player speed** offers `0.25x`, `0.5x`, `1x`, `2x`, and `4x` rates for the
  human player's automatic movement without changing bot or timer speed.
- **Game speed** offers the same rates for the complete simulation, affecting
  movement, bots, match timers, camera updates, and damage cooldowns.

The top-right debug badge shows all active values. The decorative AI arena in
the main menu remains at normal speed. Debug preferences are saved, but only
take effect while Debug mode is enabled.

The redesigned pause menu keeps the frozen arena visible behind a dark glass
overlay. It freezes the match timer and damage cooldowns, shows a compact match
summary, and can resume the match, open the shared options, return to the main
menu, or quit the game.
