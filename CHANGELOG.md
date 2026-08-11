# Changelog

All notable changes to Cubulus are documented in this file.

## [0.3.0] - 2026-08-11

### Added

- Added the new Territory game mode. Players can take over territory that has
  already been claimed by an opponent.
- Added difficulty-dependent territory goals: 2.5% for Beginner, 5% for Easy,
  10% for Normal, 20% for Hard, 50% for Expert, and 75% for God.
- Added Beginner, Expert, and God difficulty levels.
- Added infinite lives in Territory mode. A defeated player returns to their
  starting position instead of being eliminated.
- Added a God-mode alliance in which all AI opponents cooperate against the
  human player and cannot damage one another.
- Added 147 possible AI names. Every opponent receives a random name when a
  match begins, with no duplicate names within the same match.
- Added random names for every new round of the decorative AI arena in the
  main menu.
- Added six selectable player colors: purple, orange, cyan, pink, lime, and
  teal, bringing the total number of choices to ten.
- Added German and English labels for all new modes, difficulty levels, status
  messages, and colors.

### Changed

- Territory victory now requires reaching the selected map share while holding
  the unique lead; obstacles do not count toward the required territory.
- The match HUD and pause menu now show the Territory target and infinite-life
  state.
- Difficulty settings now store the level name as well as its index while
  preserving selections saved by older Cubulus versions.

[0.3.0]: https://github.com/Nova91MN/Cubulus/compare/0.2.0...main
