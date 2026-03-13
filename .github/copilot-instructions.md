# Copilot Instructions for RuleTragaperrasJuego

## Big Picture
- This is a **PyQt6 desktop casino app** with a central launcher in `main.py` and game modules in `Poker/`, `Blackjack/`, `Ruleta/`, `Tragaperras/`.
- Architecture is intentionally split into **UI vs logic** per game (e.g., `Poker/poker_ui.py` + `Poker/poker_logic.py` + `Poker/poker_table.py`).
- Cross-cutting state is centralized in `config.py` via `config_manager` (persistent `casino_config.json`, language, balances, stats, missions, achievements).
- Card games follow shared abstractions in `cardCommon.py` (`BaseCard`, `BaseDeck`). Keep new card logic aligned with this ABC pattern.

## Runtime & Module Boundaries
- `main.py` dynamically imports each game and uses a common launch contract: each `open_*_window(...)` returns `(window, owns_app, app)`.
- Keep embedded-launch behavior intact: only call `app.exec()` when `owns_app` is `True`.
- Entry points often inject project paths into `sys.path` (see `Poker/poker_main.py`, `Ruleta/ruleta_main.py`, `Tragaperras/tragaperras_main.py`). Do not break this unless refactoring all entry points consistently.
- Multiplayer has a **single source of truth** in `Server/multiplayer_server.py`; root `multiplayer_server.py` is a compatibility wrapper.

## Developer Workflows (actual project)
- Environment setup (Windows): `setup_env.bat`.
- Run app: `python main.py`.
- Run modules directly:
  - `python Poker/poker_main.py`
  - `python Blackjack/blackjack.py`
  - `python Ruleta/ruleta_main.py`
  - `python Tragaperras/tragaperras_main.py`
- Tests use `unittest` (not pytest). Typical commands:
  - `python -m unittest Test.test_all -v`
  - `python -m unittest Test.test_main -v`
  - `python -m unittest Test.test_blackjack_logic -v`

## Project-Specific Conventions
- Preserve Spanish UX strings where already used; internationalized text is accessed through `get_text(...)` from `config.py`.
- Prefer minimal, surgical edits in existing modules rather than introducing new framework layers.
- Keep persistence semantics stable: many config operations call `save_config()` immediately.
- Main UI shortcuts and game-launch flow in `main.py` are part of user-facing behavior; avoid changing keybindings/launch semantics unless requested.

## Integration Points
- `main.py` integrates `AchievementManager` and `MissionManager` and relies on config-backed stats/balance updates.
- Game UIs should update shared player state through `config_manager` APIs, not ad-hoc file writes.
- Multiplayer HTTP/WebSocket behavior is implemented in `Server/multiplayer_server.py` (token/session rules + simple web client page).

## Session Continuity (required in this repo)
- Before finishing an implementation session, update:
  - `roadmap.md` (completed, in-progress, next step)
  - `README.md` (short continuity status block)
  - `.github/copilot-instructions.md` (if reality changed)
- At session start, read `roadmap.md` first and continue from latest log entry.

## Recent Optimization Reality
- P0 optimization started: `config.py` includes `ConfigManager.batch_update()` to coalesce repeated `save_config()` calls into a single write.
- Batch persistence already applied to hot paths in `achievements.py` (`update_game_stat`, `update_win`) and `missions.py` (`_load_missions`, `update_on_hand_played`, `update_on_win`).
- Pixmap/card render caching is now applied in Poker (`Poker/poker_ui.py`) and Blackjack (`Blackjack/blackjack.py`).
- Differential UI updates are now applied in Poker (`update_community_cards`, `update_player_displays`) and Blackjack (`update_display`) to avoid redundant `setPixmap`/`setStyleSheet`/`setText` calls.
- Differential UI updates are now also applied in Tragaperras (`Tragaperras/tragaperras_ui.py`) for reel symbols, highlights and info labels to avoid redundant `setText`/`setStyleSheet` calls.
- UI baseline instrumentation is now available for critical actions in Blackjack and Tragaperras (local latency samples in UI layer).
- Consolidated baseline snapshots are now exported to `performance_baseline.json` with summaries (`avg/min/max/p95`) and threshold checks for critical actions.
- Baseline snapshots are now surfaced in main UI (`Juego` > `Rendimiento UI`) for session inspection.
- Initial CI workflow is available at `.github/workflows/tests.yml` for critical regression tests.
- Automatic snapshot-to-snapshot comparison (`Δ avg`) is now available in performance view.
- Stronger visual alerts are now available in performance view (severity levels + color emphasis for status and deltas).
- Historical CSV export is now available from `Juego` > `Rendimiento UI` (`performance_baseline_history.csv`).
- Source/metric filters and ISO time-range filtering are now available in performance view.
- CSV export in performance view now respects active filters for incremental historical analysis.
- Quick time-range presets are now available in performance view (`Todo`, `Ultima hora`, `Ultimas 24h`, `Ultimos 7 dias`).
- Aggregated trend view per metric is now available in performance view for filtered snapshots.
- Aggregated comparison view per source is now available in performance view for filtered snapshots.
- Interactive sorting is now available in performance tables for aggregated views and per-snapshot detail.
- Main UI startup and window transition timings are now instrumented and exported to `performance_baseline.json` under source `main` when the app closes.
- Main UI now includes deeper per-phase timings for each game launch (`ui.main.import_*_ms`, `ui.main.open_*_ms`, `ui.main.transition_to_*_ms`) and restore transition timings (`ui.main.restore_transition_*_ms`).
- Main bootstrap timings are now instrumented before `MainUI` creation (`ui.main.bootstrap.*`: auth/login imports, DB init, user config load, window init) and merged into source `main` baseline exports.
- Performance view now includes a dedicated phase-level breakdown for `main` (`bootstrap`, `import`, `open`, `transition`) with aggregated period comparison.
- Performance view now includes phase-level alerting (`OK`, `ALTO`, `CRITICO`, `REGRESION`) combining threshold breach ratio and period delta.
- Unified game progression contract is now implemented in `game_events.py` and integrated at round-end in Blackjack, Poker, Ruleta and Tragaperras.
- Achievement stat mapping now keeps roulette/slots consistency (`roulette_spins`, `slots_spins`) instead of mixed hand/spin semantics.
- Cross-game UX checklist for base consistency is documented in `ux_checklist_fase_a.md` and applied as Fase A baseline.
- Fase A in `roadmap.md` is now completed.
- Fase B has started with real gameplay-audio integration: `sound_manager.py` now supports category volumes/mutes and event-driven playback hooks.
- SFX hooks are now connected in Blackjack, Poker, Ruleta and Tragaperras for key gameplay actions and round results.
- Main UI now performs contextual music transitions (menu/game/restore) and progression audio is emitted from `game_events.py` for achievements/missions.
- Contextual music routing is now centralized in `sound_manager.py` through `MusicContext` with ordered fallback candidates and config overrides (`interface.music_track_<context>`).
- Main UI performance instrumentation has been refactored out of `main.py` into `performance_debug.py` to keep production UI code lean.
- Main performance metrics/export/view are now debug-only (`interface.debug_mode` or `CASINO_DEBUG_PERF=1`) instead of always-on in normal UX.
- Main baseline snapshot export now runs asynchronously in background to avoid blocking UI transitions/close path.
- Poker startup is now protected against early Qt `resizeEvent` emissions by initializing `_card_pixmap_cache` before potential resize-triggering calls and guarding the resize handler.
- Next delivery target (roadmap-only): complete Fase B audio with real music assets/pipeline in `sounds/music` and tune per-context gain/mix.
