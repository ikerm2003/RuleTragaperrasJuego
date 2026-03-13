# 🎯 Roadmap de RuleTragaperrasJuego

Roadmap oficial del proyecto para evolucionar RuleTragaperrasJuego hacia una experiencia de casino de referencia.

## 1) Objetivo de producto

Convertir RuleTragaperrasJuego en una experiencia de casino de escritorio **estable, divertida, profunda y social**, con calidad técnica alta y evolución constante.

## 2) Estado actual (Marzo 2026)

### ✅ Ya implementado

- **MainUI** con lanzador de juegos e integración central.
- **Poker Texas Hold'em** completo (2-9 jugadores, lógica sólida, UI dedicada, tests).
- **Blackjack** completo base (lógica + UI + apuestas).
- **Ruleta europea** completa base (apuestas estándar, UI, historial).
- **Tragaperras** completa operativa (lógica, UI, líneas, RTP, estadísticas).
- **Sistema de configuración** persistente (`casino_config.json`).
- **Misiones diarias**.
- **Sistema de logros**.
- **Estadísticas globales**.
- **Recarga diaria automática**.
- **Temas visuales**.
- **Atajos de teclado** en menú principal.
- **Sistema de autenticación PostgreSQL** (`auth/`): registro, login con PBKDF2-SHA256 (600k iter.), estadísticas por jugador, modo offline con fallback JSON. Migración Alembic v001 incluida.

### ⚠️ Parcial / por consolidar

- **Multiplayer**: servidor WebSocket disponible pero no integrado end-to-end en gameplay principal.
- **Audio**: infraestructura creada (`sound_manager.py`) en modo base (sin pipeline final de assets/mezcla).
- **Cobertura de tests** desigual entre módulos.

---

## 3) Principios de desarrollo

- Mantener arquitectura modular: **lógica**, **UI**, **estado/persistencia**.
- Priorizar robustez antes de features complejas.
- Cada mejora relevante debe incluir tests o validación automatizable.
- Mantener experiencia homogénea entre juegos (UX, feedback, controles).

---

## 4) Roadmap por fases

## Fase A — Base de calidad y coherencia (Q2 2026)

**Meta:** dejar el proyecto preparado para escalar sin deuda crítica.

### Entregables de Fase A

- [x] Cerrar reglas avanzadas pendientes en juegos base.
  - [x] Blackjack: **Split** (lógica + UI + tests).
  - [x] Blackjack: **Seguro** (lógica + UI + tests).
- [x] Unificar contratos de estadísticas y eventos entre todos los juegos.
- [x] Definir y aplicar checklist de UX transversal (mensajes, errores, botones, estados).
- [x] Fortalecer manejo de errores y recuperación de estado (fix de resolución duplicada en Blackjack).
- [x] Subir cobertura de tests del core de reglas.

**Estado Fase A:** ✅ **Completada**.

### Criterios de salida de Fase A

- 0 bugs críticos abiertos en juegos base.
- Flujo de juego completo estable en los 4 juegos.
- Cobertura mínima del core de lógica en nivel objetivo interno.

---

## Fase B — Pulido premium y retención (Q3 2026)

**Meta:** mejorar sensación de calidad y engagement diario.

### Entregables de Fase B

- [ ] Audio completo de producto:
  - [x] SFX por juego.
  - [ ] Música por contexto.
  - [x] Mapeo/fallback por contexto en motor de audio.
  - [ ] Assets finales por contexto en `sounds/music`.
  - [x] Control de volumen y mute por categorías.
- [ ] Revisión de animaciones y timings para feedback consistente.
- [ ] Evolución de misiones:
  - [ ] Rotación semanal.
  - [ ] Misiones especiales por juego.
- [ ] Evolución de logros:
  - [ ] Progresión por rareza.
  - [ ] Hitos largos de carrera.
- [ ] Pantalla de historial/resumen de sesión.

### Criterios de salida de Fase B

- Sensación de interacción uniforme entre juegos.
- Sistema de progresión diaria/semanal funcional y estable.

---

## Fase C — Multiplayer jugable real (Q4 2026)

**Meta:** pasar de prototipo de servidor a experiencia multijugador utilizable.

### Entregables de Fase C

- [ ] Integración multiplayer en un primer modo acotado (MVP social).
- [ ] Sistema de salas públicas/privadas.
- [ ] Reconexión robusta y gestión de sesión.
- [ ] Validación de acciones críticas en servidor (modelo authoritative en lo necesario).
- [ ] Chat y presencia de jugadores estabilizados.

### Criterios de salida de Fase C

- Flujo de partida multijugador funcional de punta a punta.
- Reconexión sin pérdida de sesión en escenarios comunes.

---

## Fase D — Competitivo y expansión de contenido (Q1–Q2 2027)

**Meta:** añadir profundidad de largo plazo y diferenciación.

### Entregables de Fase D

- [ ] Modo torneo inicial.
- [ ] Hand history/replay para Poker.
- [ ] Primera variante avanzada de Poker (Omaha).
- [ ] Eventos temporales (temporadas).
- [ ] Internacionalización ampliada.
- [ ] Pipeline de release con quality gates.

### Criterios de salida de Fase D

- Ciclo de contenido recurrente operativo.
- Releases predecibles con regresiones controladas.

---

## 5) Backlog técnico transversal

- [ ] Estandarizar logging estructurado por módulo.
- [ ] Definir métricas de rendimiento en UI (tiempo de respuesta percibido).
- [ ] CI para ejecución automatizada de tests prioritarios.
- [ ] Convenciones de errores y mensajes para todo el proyecto.
- [ ] Revisión de arquitectura de `main.py` para reducir acoplamiento progresivamente.

---

## 6) KPIs de referencia (producto)

- **Estabilidad:** sesiones sin crash por encima del objetivo interno.
- **Calidad:** cero regresiones críticas por release.
- **Engagement:** crecimiento sostenido de sesiones repetidas.
- **Progresión:** mayor porcentaje de usuarios completando misiones/logros.

---

## 7) Prioridad inmediata (siguientes sprints)

1. Completar reglas avanzadas de Blackjack (Split + Seguro).
2. Cerrar integración real del audio (assets + reproducción por eventos).
3. Definir MVP de multiplayer con alcance concreto en un juego.
4. Reforzar tests en módulos con más riesgo de regresión.
5. Evaluar y diseñar una ruta completa de migración de PyQt6 a Arcade manteniendo la lógica desacoplada.

### Estado actual de prioridades

- Blackjack (Split + Seguro): **Completado**.

- Audio real: **En progreso** (mapeo contextual y fallback listos; faltan assets finales de música).

- MVP de multiplayer: **Pendiente**.

- Reforzar tests en módulos de riesgo: **En progreso** (nuevos tests de seguro, split e idempotencia en Blackjack).
- Reforzar tests en módulos de riesgo: **Completado** (incluye cobertura del contrato unificado de eventos y mapeo de estadísticas por juego).

---

## 8) Definición de “versión excelente”

Una release se considera excelente cuando cumple:

- Sin bloqueos críticos de juego.
- Sin pérdida de progreso/configuración.
- UX consistente entre módulos.
- Rendimiento fluido en hardware objetivo.
- Validación técnica (tests/checks) en verde para el alcance de la release.

---

## 9) Bitácora de implementación (continuidad entre sesiones)

- **2026-03-05**
  - Implementado seguro en Blackjack (`insurance`) en lógica y UI.
  - Corregida resolución duplicada de mano en Blackjack (evita pagos duplicados).
  - Añadidos tests de lógica para seguro e idempotencia de `resolve_hand`.
  - Implementado **Split** en Blackjack (lógica + UI + tests).
  - Refactor de `main.py` para eliminar lógica duplicada en los lanzadores de juegos (`launch_*`) con helper común de apertura/cierre y manejo de errores.
  - Eliminada duplicación exacta del servidor multijugador: `multiplayer_server.py` raíz ahora delega en `Server/multiplayer_server.py` como única fuente de verdad.
  - Validación de regresión ejecutada: `Test/test_main.py` en verde.
  - Próximo paso recomendado: comenzar integración de **audio real** (SFX por eventos de juego).

- **2026-03-12**
  - Iniciada implementación de optimización P0 de I/O: `ConfigManager` ahora soporta actualizaciones por lote con `batch_update()` para coalescer múltiples `save_config()` en una sola escritura efectiva.
  - Aplicado `batch_update()` en rutas calientes de `AchievementManager` (`update_game_stat`, `update_win`) para reducir escrituras por evento de juego sin cambiar reglas ni recompensas.
  - Aplicado `batch_update()` en `MissionManager` (`_load_missions`, `update_on_hand_played`, `update_on_win`) para consolidar persistencia durante progresos encadenados.
  - Implementada caché de pixmaps de cartas en Poker (`Poker/poker_ui.py`) y Blackjack (`Blackjack/blackjack.py`) para reutilizar renders idénticos y reducir coste de `update_display`.
  - Implementadas actualizaciones diferenciales de UI en Poker y Blackjack para evitar llamadas redundantes de `setPixmap`, `setText` y `setStyleSheet` en ciclos de refresco frecuentes.
  - Refactor de `Blackjack/blackjack.py:update_display` para no limpiar/ocultar todas las cartas en cada frame y actualizar solo los slots de cartas que cambian de estado.
  - Refactor de `Poker/poker_ui.py:update_community_cards` y `update_player_displays` con helpers de actualización condicional para texto, estilos y cartas.
  - Aplicado patrón de actualización diferencial en `Tragaperras/tragaperras_ui.py` para reducir llamadas redundantes a `setText`/`setStyleSheet` en animación de rodillos, resaltado y panel informativo.
  - Refactor de `ReelColumn` (`set_symbols`, `set_highlights`, `clear_highlights`) y callbacks UI de tragaperras para actualizar etiquetas solo cuando cambian.
  - Añadida instrumentación de baseline en UI para acciones críticas: métricas locales de latencia en Blackjack (`deal`, `hit`, `stand`, `double`, `split`) y en Tragaperras (`spin_end_to_end_ms`, `render_result_ms`).
  - Implementada exportación consolidada de baseline en `performance_baseline.json` al cierre de ventanas de Blackjack y Tragaperras, incluyendo resumen (`avg/min/max/p95`) y evaluación contra umbrales objetivo.
  - Añadida visualización de snapshots baseline en `main.py` (menú `Juego` > `Rendimiento UI`) para consultar métricas por sesión.
  - Añadida comparación automática snapshot-a-snapshot (`Δ avg`) en `Rendimiento UI` para detectar regresiones entre sesiones de forma directa.
  - Reforzada la visualización de alertas en `Rendimiento UI` con severidad explícita por métrica (`OK`, `ALTO`, `CRITICO`, `REGRESION`) y resaltado de color para estado y delta.
  - Añadida exportación histórica a CSV desde `Rendimiento UI` (`performance_baseline_history.csv`) con filas por snapshot/métrica, incluyendo `Δ avg` y nivel de alerta para análisis externo.
  - Añadidos filtros interactivos en `Rendimiento UI` por fuente y métrica, junto con rango temporal (`Desde/Hasta` en formato ISO) para enfocar análisis de regresión.
  - Adaptada la exportación CSV para respetar filtros activos (fuente, métrica y ventana temporal), permitiendo exportes incrementales de snapshots relevantes.
  - Añadidos tests unitarios para parseo/filtrado de snapshots en `Test/test_main.py`.
  - Añadidos tests unitarios para helpers de severidad y transformación de snapshots a filas CSV en `Test/test_main.py`.
  - Corregido crash de arranque en Poker por `resizeEvent`: la caché `_card_pixmap_cache` ahora se inicializa antes de cualquier `resize` potencial y `resizeEvent` se protege frente a emisiones tempranas de Qt durante la construcción.
  - Añadido workflow de CI inicial en `.github/workflows/tests.yml` ejecutando suite crítica (`test_main`, `test_blackjack_logic`, `test_tragaperras_table`, `test_tragaperras`).
  - Validación de regresión: `Test/test_blackjack_logic.py` + `Test/test_main.py` en verde (31 tests).
  - Validación adicional del fix de Poker: `Test/test_poker.py` en verde (31 tests) y arranque manual de `main.py` sin reproducir el `AttributeError` previo.
  - Validación de tragaperras: `Test/test_tragaperras_table.py` + `Test/test_tragaperras.py` + `Test/test_main.py` en verde (5 tests en esta ejecución).
  - Validación: `Test/test_main.py` y `Test/test_blackjack_logic.py` en verde (31 tests). `Test/test_config.py` mantiene un fallo previo no relacionado (`test_language_count` espera 2 idiomas y el enum actual define 4).
  - Próximo paso recomendado: añadir presets rápidos de rango temporal (última hora/día/semana) y vista agregada por métrica para comparar tendencias sin salir del diálogo.

- **2026-03-13**
  - Definido roadmap específico de migración a nuevo motor 2D en `roadmap_nuevomotor.md`, usando Arcade como objetivo y preservando la separación actual entre lógica y UI.
  - Orden de migración fijado para minimizar riesgo: runtime común, contratos vista-lógica, Tragaperras, Ruleta, Blackjack, Poker y retirada final de PyQt6.
  - Próximo paso recomendado para esta línea: crear `arcade_app/` con ventana base, gestor de escenas y primer controlador desacoplado de Tragaperras.
  - Implementados presets rápidos de rango temporal en `main.py` para `Juego > Rendimiento UI` (`Todo`, `Ultima hora`, `Ultimas 24h`, `Ultimos 7 dias`) con aplicación directa sobre filtros ISO.
  - Añadida vista agregada de tendencia por métrica en `Juego > Rendimiento UI` con consolidación por periodo filtrado (`avg` agregado, delta de periodo, min/max, fuentes y brechas de umbral).
  - Añadida comparativa agregada por fuente en `Juego > Rendimiento UI` con resumen por periodo filtrado (`avg` agregado, delta de periodo, métricas incluidas y brechas de umbral).
  - Añadida ordenación interactiva en tablas de `Rendimiento UI` para agregados y detalle (`nombre`, `avg`, `delta`, `brechas`, `snapshots`, `severidad`).
  - Añadida instrumentación de tiempos en `main.py` para arranque del menú principal y transiciones de apertura/retorno de juegos, con exportación de baseline bajo fuente `main` al cierre de la app.
  - Añadidos tests unitarios en `Test/test_main.py` para los nuevos helpers (`_get_time_preset_bounds` y `_build_metric_trend_rows`).
  - Añadidos tests unitarios en `Test/test_main.py` para la nueva agregación por fuente y ordenación de filas (`_build_source_trend_rows`, `_sort_performance_rows`).
  - Extendida la instrumentación de `main.py` con tiempos finos por fase de lanzamiento de juegos: import dinámico (`ui.main.import_*_ms`), apertura de ventana (`ui.main.open_*_ms`) y transición completa al juego (`ui.main.transition_to_*_ms`).
  - Extendida la instrumentación de retorno al menú principal con métrica específica de transición (`ui.main.restore_transition_*_ms`) además de la métrica total existente de restore.
  - Añadida instrumentación de bootstrap de app en `main.py` antes de crear `MainUI`: import de módulos auth/login, inicialización de DB, carga de config por usuario y construcción de ventana (`ui.main.bootstrap.*`).
  - Integradas métricas de bootstrap en el baseline de fuente `main` mediante registro explícito en `MainUI` para exportación unificada en `performance_baseline.json`.
  - Añadidos tests unitarios en `Test/test_main.py` para nuevos helpers de registro de métricas (`_record_ui_metric_value`, `_record_bootstrap_metrics`) y para umbral de métrica bootstrap.
  - Añadida visualización dedicada por fases en `Juego > Rendimiento UI` para métricas de `main` (`bootstrap`, `import`, `open`, `transition`) con tabla agregada específica por periodo filtrado.
  - Añadidas alertas agregadas por fase con severidad visual (`OK`, `ALTO`, `CRITICO`, `REGRESION`) combinando brechas de umbral y delta del periodo.
  - Añadidos tests unitarios en `Test/test_main.py` para nuevos helpers de fases (`_classify_main_metric_phase`, `_compute_phase_alert_level`, `_build_phase_trend_rows`) y ordenación agregada por fase.
  - Validación ejecutada en verde: `Test.test_main.TestMainUIPerformanceHelpers` (15 tests).
  - Convertido `roadmap_optimizaciones.md` a checklist real de ejecución; estado consolidado actual: 19 tareas completadas y 23 pendientes sobre 42.
  - Validación ejecutada: tests nuevos de helpers en verde (`TestMainUIPerformanceHelpers.test_get_time_preset_bounds_last_hour`, `TestMainUIPerformanceHelpers.test_build_metric_trend_rows_aggregates_and_delta`, `TestMainUIPerformanceHelpers.test_build_source_trend_rows_aggregates_and_delta`, `TestMainUIPerformanceHelpers.test_sort_performance_rows_by_delta_desc`, `TestMainUIPerformanceHelpers.test_build_metric_summary_for_main_startup_metric`, `TestMainUIPerformanceHelpers.test_sort_source_rows_by_snapshots_desc`).
  - Nota de validación: `python -m unittest Test.test_main -v` mantiene un fallo de entorno GUI preexistente (`QWidget: Must construct a QApplication before a QWidget`) fuera del alcance funcional de esta entrega.
  - Implementado contrato unificado de eventos de ronda en `game_events.py` con normalización de juegos (`poker`, `blackjack`, `roulette`, `slots`) y actualización centralizada de estadísticas/misiones/logros.
  - Integrado el contrato unificado en cierre de ronda de Blackjack (`Blackjack/blackjack.py`), Poker (`Poker/poker_ui.py`), Ruleta (`Ruleta/ruleta_ui.py`) y Tragaperras (`Tragaperras/tragaperras_ui.py`).
  - Corregido mapeo de estadísticas de logros en `achievements.py`: ruleta y tragaperras ahora actualizan `roulette_spins` y `slots_spins` de forma consistente.
  - Definido y documentado checklist UX transversal de Fase A en `ux_checklist_fase_a.md`.
  - Añadidos tests de cobertura del core para el nuevo contrato en `Test/test_game_events.py` (normalización, flujo win/loss y mapeo de stats por juego).
  - Validación ejecutada en verde: `Test/test_game_events.py`, `Test/test_blackjack_logic.py`, `Test/test_ruleta_logic.py`, `Test/test_tragaperras.py` (88 tests).
  - Cierre de fase: **Fase A completada**.
  - Iniciada **Fase B** con integración de audio por eventos de gameplay.
  - `sound_manager.py` evolucionado a reproducción funcional con categorías `SFX`/`MUSIC`, volúmenes por categoría y mute por categoría, incluyendo fallback audible cuando faltan assets.
  - Integrados SFX en flujo de juego de Blackjack, Poker, Ruleta y Tragaperras (apuestas, acciones, giro/spin y resolución win/loss/jackpot).
  - Integrado audio contextual en `main.py` para menú principal (tema de menú, transición a tema de juego y restauración al volver).
  - Integrado disparo de sonido para logros/misiones completadas en `game_events.py`.
  - Añadidos controles de audio por categorías en `config_dialog.py` (maestro, SFX, música, mute).
  - Añadida cobertura de audio en `Test/test_sound_manager.py` y ajustados tests de `game_events` para compatibilidad con el nuevo flujo de sonido.
  - Validación ejecutada en verde: `Test/test_sound_manager.py`, `Test/test_game_events.py`, `Test/test_blackjack_logic.py`, `Test/test_ruleta_logic.py`, `Test/test_tragaperras.py` (92 tests).
  - Refactorizada la observabilidad de `main.py` a `performance_debug.py`, extrayendo captura, agregación, exportación y vista de métricas fuera de la UI principal.
  - Métricas de `main` ahora se ejecutan solo en modo debug (`interface.debug_mode` o `CASINO_DEBUG_PERF=1`) para no cargar el flujo normal de usuario.
  - Exportación de snapshots de rendimiento en `main` ahora se realiza de forma asíncrona en background (`ThreadPoolExecutor`) para evitar bloquear cierre/transiciones de UI.
  - Validación de compatibilidad de helpers de rendimiento en verde: `Test.test_main.TestMainUIPerformanceHelpers` (18 tests).
  - Implementado selector robusto de música por contexto en `sound_manager.py` con `MusicContext`, candidatos por escena y fallback ordenado de pistas.
  - Añadido soporte de override por configuración para pistas contextuales (`interface.music_track_<contexto>`) con lista CSV opcional.
  - Integrado `main.py` con reproducción contextual centralizada (`play_music_for_context`) para menú y cada juego.
  - Evitada recarga redundante de la misma pista musical activa para reducir cortes/reinicios innecesarios.
  - Añadidos tests de mapeo contextual en `Test/test_sound_manager.py` (candidatos por defecto y override por config).
  - Validación ejecutada en verde: `Test/test_sound_manager.py` (6 tests).
  - Próximo paso recomendado: completar pipeline de assets musicales reales en `sounds/music/*.mp3|*.ogg|*.wav` y ajustar mezcla/ganancias por contexto.

> Esta bitácora se debe actualizar al finalizar cada sesión de implementación.
