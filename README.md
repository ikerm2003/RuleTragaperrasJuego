# 🎰 RuleTragaperrasJuego - Casino Game Collection

Una colección completa de juegos de casino implementada en Python con PyQt6, que incluye Poker Texas Hold'em, Blackjack, Ruleta y Tragaperras con una interfaz moderna y profesional.

## 📋 Descripción General

RuleTragaperrasJuego es un proyecto de casino virtual que presenta múltiples juegos de cartas y casino. Actualmente ofrece un módulo completo de Poker Texas Hold'em y una tragaperras 3x3 de última generación, ambos con interfaces PyQt6 profesionales y listas para jugar.

## 🔄 Estado de Continuidad (2026-03-13)

- Se ha definido una ruta formal de migración desde PyQt6 a Arcade en `roadmap_nuevomotor.md`, manteniendo la lógica desacoplada y planificando convivencia temporal entre ambos runtimes.
- El orden recomendado de migración es: runtime Arcade común, contratos vista-lógica, Tragaperras, Ruleta, Blackjack, Poker y retirada final de PyQt6.
- Fase B iniciada por roadmap: audio de gameplay ya integrado como primer bloque de pulido premium.
- `sound_manager.py` actualizado a reproducción funcional con categorías (`SFX`/`MUSIC`), volumen maestro y volumen/mute por categoría.
- SFX conectados en Blackjack, Poker, Ruleta y Tragaperras para acciones y resolución de ronda.
- Audio contextual básico conectado en `main.py` (tema de menú, transición a tema por juego y restauración al volver).
- Mapeo musical por contexto reforzado en `sound_manager.py` con `MusicContext`, fallback ordenado de pistas y anti-reinicio de la pista ya activa.
- Overrides por configuración para pistas contextuales disponibles vía `interface.music_track_<contexto>` (valor simple o CSV).
- Sonidos de progresión conectados en `game_events.py` para logros y misiones completadas.
- `config_dialog.py` incluye controles de audio por categorías (maestro, SFX y música con mute).
- Tests de audio añadidos en `Test/test_sound_manager.py` y validación de regresión en verde (92 tests en suite focalizada).
- Métricas de rendimiento de `main.py` extraídas a `performance_debug.py` para reducir complejidad de UI principal.
- Instrumentación y vista de `Rendimiento UI` ahora se activan solo en debug (`interface.debug_mode` o `CASINO_DEBUG_PERF=1`).
- Exportación de snapshots de rendimiento en `main` ahora es asíncrona en background para no bloquear el flujo normal.
- Fase A del `roadmap.md` completada (reglas avanzadas, contratos de eventos/estadísticas, checklist UX y refuerzo de cobertura core).
- Contrato unificado de fin de ronda implementado en `game_events.py` e integrado en Blackjack, Poker, Ruleta y Tragaperras.
- Corrección de consistencia de estadísticas por juego en logros: ruleta y tragaperras actualizan `roulette_spins` y `slots_spins`.
- Checklist UX transversal definido y aplicado en `ux_checklist_fase_a.md`.
- Nueva cobertura core añadida en `Test/test_game_events.py` para normalización de eventos, flujo win/loss y mapeo de estadísticas.
- Rendimiento UI del menú principal reforzado con alertas visuales por severidad (`OK`, `ALTO`, `CRITICO`, `REGRESION`) en estado y delta de métricas.
- Exportación histórica de snapshots a `performance_baseline_history.csv` desde `Juego > Rendimiento UI`.
- Filtros interactivos por fuente/métrica y rango temporal ISO (`Desde/Hasta`) ya disponibles en `Juego > Rendimiento UI`.
- La exportación CSV ahora respeta filtros activos para análisis incremental por ventana temporal.
- Presets rápidos de rango temporal ya disponibles en `Juego > Rendimiento UI`: `Todo`, `Ultima hora`, `Ultimas 24h`, `Ultimos 7 dias`.
- Nueva vista agregada de tendencia por métrica en `Juego > Rendimiento UI` para el periodo filtrado (avg agregado, delta, min/max y brechas de umbral).
- Nueva comparativa agregada por fuente en `Juego > Rendimiento UI` para el periodo filtrado (avg agregado, delta, métricas incluidas y brechas de umbral).
- Ordenación interactiva ya disponible en `Juego > Rendimiento UI` para tablas agregadas y detalle por snapshot.
- Instrumentación de `main.py` ya disponible para tiempos de arranque del menú principal y transiciones de apertura/retorno entre ventanas, exportadas al baseline al cerrar la app.
- Instrumentación fina por fase añadida en `main.py` para cada juego: `import`, `open` y transición de entrada (`ui.main.import_*_ms`, `ui.main.open_*_ms`, `ui.main.transition_to_*_ms`).
- Instrumentación fina de retorno al menú añadida con `ui.main.restore_transition_*_ms` para separar coste de transición respecto al restore total.
- Instrumentación de bootstrap añadida en `main.py` para import de auth/login, inicialización DB, carga de config por usuario y creación de `MainUI` (`ui.main.bootstrap.*`).
- Las métricas de bootstrap se integran en el baseline de fuente `main` para análisis unificado en `performance_baseline.json`.
- Nueva vista dedicada de desglose por fases en `Juego > Rendimiento UI` para métricas de `main` (`bootstrap`, `import`, `open`, `transition`) en el periodo filtrado.
- Alertado agregado por fase ya disponible con severidad visual (`OK`, `ALTO`, `CRITICO`, `REGRESION`) combinando brechas de umbral y delta del periodo.
- `roadmap_optimizaciones.md` ya usa checklist real de ejecución con estado consolidado: 19 tareas completadas y 23 pendientes sobre 42.
- Corregido crash de arranque en Poker causado por `resizeEvent` durante la construcción temprana de la ventana.
- Baseline consolidado sigue en `performance_baseline.json` y ahora puede incluir fuente `main` además de Blackjack y Tragaperras.
- Validación de regresión ejecutada en esta sesión: `Test.test_main.TestMainUIPerformanceHelpers` en verde (15 tests).
- Nota de entorno: `python -m unittest Test.test_main -v` mantiene un fallo GUI preexistente local (`QWidget: Must construct a QApplication before a QWidget`).
- Siguiente foco recomendado: completar assets reales en `sounds/music` y cerrar pipeline de mezcla/ganancias por contexto para finalizar el bloque de audio de Fase B.

### 🎮 Módulos Principales

- **🃏 Poker** (Completo): Implementación completa de Texas Hold'em

  - Soporte para 2-9 jugadores con posicionamiento automático
  - Sistema de IA para bots con estrategias básicas
  - Interfaz profesional con mesa de poker y animaciones
  - Evaluación completa de manos y manejo de apuestas lateral
  
- **🎰 Tragaperras** (Completo): Máquina tragaperras completa
  - 5 rodillos con sistema de líneas de pago configurables
  - Sistema dinámico de RTP con ajuste automático
  - Animaciones de giro y resaltado de victorias
  - Estadísticas en tiempo real y sistema de recuperación
  
- **🔥 Blackjack** (Completo): Implementación completa de Blackjack

  - Lógica completa del juego con dealer AI inteligente
  - Clases propias heredando de cardCommon
  - Interfaz profesional con PyQt6
  - Acciones completas: Hit, Stand, Double Down
  - Manejo correcto de Ases y detección de Blackjack
  - Sistema de apuestas y balance integrado
  
- **🎯 Ruleta** (Completo): Ruleta europea completa
  
  - 37 números (0-36) con colores correctos
  - Todos los tipos de apuestas estándar
  - Animación de ruleta giratoria
  - Mesa de apuestas profesional e intuitiva
  - Historial y estadísticas de juego
  
- **🎛️ MainUI**: Menú principal con lanzador de juegos
- **⚙️ Sistema de Configuración**: Configuración completa de la aplicación

## 🚀 Instalación Rápida

### Prerequisitos

- Python 3.8 o superior
- Sistema operativo Windows (para el script .bat)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/ikerm2003/RuleTragaperrasJuego.git
cd RuleTragaperrasJuego
```

### 2. Setup Automático con Script

**Para usuarios de Windows:**

```cmd
setup_env.bat
```

Este script automáticamente:

- Verifica la existencia del entorno virtual `.venv`
- Activa el entorno virtual
- Instala todas las dependencias desde `requirements.txt`
- Muestra instrucciones de uso

### 3. Setup Manual (Alternativo)

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🎯 Uso de la Aplicación

### Lanzar Aplicación Principal

```bash
python main.py
```

### Lanzar Módulos Específicos

#### Poker Texas Hold'em

```bash
python Poker/poker_main.py
```

#### Blackjack

```bash
python Blackjack/blackjack.py
```

#### Ruleta

```bash
python Ruleta/ruleta_main.py
```

#### Tragaperras
```bash
python Tragaperras/tragaperras_main.py
```

Incluye animación de rodillos, historial de tiradas, estadísticas en vivo, autoplay y controles para líneas/ apuesta por línea.

## 📁 Estructura del Proyecto

```text
RuleTragaperrasJuego/
├── .venv/                  # Entorno virtual de Python
├── Poker/                  # Módulo completo de Poker Texas Hold'em
│   ├── poker_main.py      # Punto de entrada del poker
│   ├── poker_logic.py     # Lógica central del juego
│   ├── poker_table.py     # Gestión de mesa (soporte 9 jugadores)
│   ├── poker_ui.py        # Componentes UI de PyQt6
│   └── test_poker.py      # Tests unitarios completos
├── Blackjack/             # Módulo completo de Blackjack
│   └── blackjack.py       # Implementación completa con lógica y UI
├── Ruleta/                # Módulo completo de Ruleta
│   ├── ruleta.py          # Punto de entrada legacy
│   ├── ruleta_main.py     # Punto de entrada principal
│   ├── ruleta_logic.py    # Lógica del juego de ruleta
│   └── ruleta_ui.py       # Interfaz de usuario
├── Tragaperras/           # Módulo completo de Tragaperras
│   ├── tragaperras_main.py
│   ├── tragaperras_logic.py
│   ├── tragaperras_table.py
│   └── tragaperras_ui.py
├── main.py                # Aplicación principal y menú
├── cardCommon.py          # Clases base abstractas para cartas
├── config.py              # Sistema de configuración
├── config_dialog.py       # Diálogo de configuración
├── Test/                  # Suite de tests de integración
│   ├── test_tragaperras.py      # Cobertura integral de tragaperras
│   ├── test_tragaperras_table.py# Tests de callbacks e historial
│   └── ...
├── requirements.txt       # Dependencias de Python
├── setup_env.bat         # Script de setup automático
└── README.md             # Este archivo
```

## 🎮 Características Principales

### ✅ Poker Texas Hold'em (Completo)

- **Reglas completas**: Implementación completa de Texas Hold'em
- **Multijugador**: Soporte para 2-9 jugadores con posicionamiento correcto
- **IA de Bots**: Jugadores automáticos con estrategias básicas
- **Interfaz profesional**: Mesa de poker con diseño profesional y escalado responsivo
- **Evaluación de manos**: Sistema completo incluyendo casos edge
- **Sistema de apuestas**: Todas las acciones (fold, check, call, raise, all-in)
- **Manejo de errores**: Validación robusta y manejo de errores
- **Tests completos**: 30 tests unitarios con 100% de cobertura

### ✅ Tragaperras (Completo)
- **5 Rodillos**: Sistema de slot machine profesional con múltiples líneas
- **Sistema RTP dinámico**: Return to Player ajustable con rangos configurables
- **Sistema de pagos**: Tabla de pagos completa con símbolos Wild y Scatter
- **Animaciones profesionales**: Giro de rodillos con efectos visuales
- **Estadísticas en tiempo real**: Tracking de ganancias/pérdidas y RTP actual
- **Recuperación de pérdidas**: Sistema opcional de compensación de pérdidas
- **Líneas configurables**: 1-9 líneas de pago activas
- **Tests completos**: Cobertura completa de lógica y UI

### ⚙️ Sistema de Configuración Avanzado

- **Configuración de pantalla**: Pantalla completa, resolución, VSync
- **Idiomas**: Soporte para Español e Inglés
- **Animaciones**: Velocidad configurable o desactivación
- **Configuración de juego**: Timeouts, confirmaciones, hints de probabilidad
- **Recarga diaria automática**: Sistema de auto-refill de balance diario
- **Atajos de teclado**: Controles rápidos para navegación

### ⌨️ Atajos de Teclado

El sistema incluye atajos de teclado completos para una experiencia más fluida:

**Menú Principal:**
- `1` - Lanzar Póker
- `2` - Lanzar Blackjack
- `3` - Lanzar Ruleta
- `4` - Lanzar Tragaperras
- `F11` - Alternar pantalla completa
- `Ctrl+S` - Abrir configuración
- `ESC` o `Ctrl+Q` - Salir de la aplicación

### 💰 Sistema de Recarga Diaria

El juego incluye un sistema automático de recarga de balance:

- **Recarga automática**: Si tu balance está por debajo del inicial, se recargará automáticamente al día siguiente
- **Balance inicial**: 1000 créditos (configurable)
- **Notificación**: Recibirás un mensaje cuando se realice la recarga
- **Configurable**: Puedes activar/desactivar esta función en la configuración

### 🎨 Características de UI

- **Diseño responsive**: Se adapta a diferentes tamaños de ventana
- **Animaciones suaves**: Efectos visuales configurables
- **Tema profesional**: Apariencia de casino con gradientes y sombras
- **Gestión de estado**: Actualizaciones en tiempo real del estado del juego

## 🔧 Dependencias

### Principales

- **PyQt6**: Framework de GUI principal
- **PyQt6-Qt6**: Bindings de Qt6
- **PyQt6-sip**: Sistema de integración Python-C++

### Biblioteca Estándar de Python

- `json`, `os`, `sys`, `random`, `logging`
- `typing`, `pathlib`, `enum`, `abc`
- `collections`, `dataclasses`

Todas las dependencias están listadas en `requirements.txt` y se instalan automáticamente con el script `setup_env.bat`.

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Activar entorno virtual primero
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Ejecutar tests del poker (30 tests)
python -m unittest Poker/test_poker.py -v

# Suite de tragaperras (lógica y UI/controller)
python -m unittest test_tragaperras_logic -v
python -m unittest Test.test_tragaperras -v
python -m unittest Test.test_tragaperras_table -v
```

### Cobertura de Tests

- **30 tests unitarios** para el módulo de Poker
- **Cobertura integral** para la tragaperras (lógica, UI/controller e integración)
- Tests organizados por componentes (TestPokerCards, TestPokerTable, TestSlotMachine, etc.)

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. PyQt6 no encontrado

```bash
# Solución
pip install PyQt6
```

#### 2. Error al activar entorno virtual

```bash
# Verificar que existe
ls .venv/Scripts/  # Windows
ls .venv/bin/      # Linux/Mac

# Recrear si no existe
python -m venv .venv
```

#### 3. Problemas de dependencias

```bash
# Reinstalar todas las dependencias
pip install --upgrade --force-reinstall -r requirements.txt
```

#### 4. Error de importación con módulos relativos

```bash
# Ejecutar desde la raíz del proyecto
cd RuleTragaperrasJuego
python main.py  # ✅ Correcto
# python Poker/poker_main.py  # ✅ También correcto
```

### Modo Debug

Para habilitar logging detallado:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# El juego mostrará información detallada del estado
```

## 🔮 Roadmap Maestro (2026-2027)

### 🌍 Visión: “El mejor juego de casino del mundo”

Construir la mejor experiencia de casino de escritorio por **calidad de juego, sensación visual, profundidad de sistemas y fiabilidad técnica**.

Esto significa:

- Reglas impecables y auditables en todos los juegos
- UX premium (fluidez, feedback visual/sonoro y claridad)
- Progresión motivadora (misiones, logros, eventos)
- Escalabilidad real para multijugador, torneos y contenido nuevo
- Estabilidad de nivel producto (tests, métricas, rendimiento, cero regresiones críticas)

### 📌 Estado real actual (base sólida)

- ✅ Poker, Blackjack, Ruleta y Tragaperras funcionales con UI PyQt6
- ✅ MainUI integrado con navegación y atajos
- ✅ Sistema de configuración, idiomas y persistencia JSON
- ✅ Misiones, logros, estadísticas y recarga diaria implementados
- ✅ Temas visuales disponibles
- ⚠️ Audio aún en modo base/placeholder (sin biblioteca de assets final)
- ⚠️ Multijugador con servidor WebSocket disponible, pendiente de integración completa en gameplay

### 🎯 North Star y KPIs de producto

- **Retención diaria (D1)**: objetivo ≥ 45%
- **Retención semanal (D7)**: objetivo ≥ 20%
- **Duración media de sesión**: objetivo 18-30 minutos
- **Crash-free sessions**: objetivo ≥ 99.5%
- **Regresiones críticas en release**: objetivo 0
- **Cobertura de tests en lógica core**: objetivo ≥ 90%

### 🗺️ Fases del roadmap

#### Fase 1 — Excelencia del Core (Q2 2026)

Objetivo: convertir la base actual en un producto ultra estable y pulido.

- [ ] Cerrar brechas de reglas avanzadas (Blackjack: split, seguro; validaciones edge adicionales)
- [ ] Unificar métricas y telemetría local de todos los juegos
- [ ] Completar sistema de audio real (SFX + música + controles finos)
- [ ] Mejorar feedback UX (microanimaciones, estados de botones, mensajes contextuales)
- [ ] Harden de estabilidad (manejo de errores, recuperación, guardado robusto)
- [ ] Ampliar tests en módulos con menor cobertura

#### Fase 2 — Profundidad de Producto (Q3 2026)

Objetivo: aumentar engagement y sensación de progresión diaria.

- [ ] Temporadas de misiones (rotación semanal + objetivos especiales)
- [ ] Revisión del sistema de logros (raridad, cadenas, hitos por juego)
- [ ] Sistema de economía balanceada (recompensas, sinks, anti-exploit)
- [ ] Historial de partidas/manos con pantalla de resumen
- [ ] Mejoras de accesibilidad (tamaño UI, contraste, opciones de animación)

#### Fase 3 — Competitivo y Social (Q4 2026)

Objetivo: pasar de experiencia individual a ecosistema social.

- [ ] Integración completa del multijugador en al menos 1 modo principal
- [ ] Salas privadas/públicas con reconexión fiable
- [ ] Chat y presencia de jugadores robustos
- [ ] Modo torneo inicial (eliminación simple + tabla de posiciones)
- [ ] Anti-cheat básico y validación server-authoritative para acciones críticas

#### Fase 4 — Escala y Contenido Premium (Q1-Q2 2027)

Objetivo: consolidar estatus “world-class”.

- [ ] Variantes avanzadas de Poker (Omaha como primera expansión)
- [ ] Eventos globales de tiempo limitado
- [ ] Sistema de perfiles y progresión de largo plazo
- [ ] Replay/hand history avanzado con filtros
- [ ] Internacionalización ampliada (mínimo 4 idiomas activos)
- [ ] Pipeline de releases con quality gates automáticos

### 🧱 Pilar técnico transversal (aplica a todas las fases)

- [ ] Arquitectura: mantener separación lógica/UI/estado y contratos claros
- [ ] Rendimiento: profiling periódico de UI y lógica
- [ ] Calidad: CI con tests, lint, checks de regresión
- [ ] Observabilidad: logging estructurado y trazas de errores accionables
- [ ] Compatibilidad: preservar APIs y migraciones sin romper datos de usuario

### ⚠️ Riesgos clave y mitigación

- **Complejidad multijugador** → priorizar diseño server-authoritative y pruebas de carga tempranas
- **Regresiones al añadir features** → quality gates obligatorios por release
- **Deuda UX entre juegos** → design system unificado y checklist de consistencia
- **Desbalance económico** → telemetría y reajuste iterativo por temporada

### ✅ Definición de “release excelente”

Una versión se considera excelente cuando cumple todo lo siguiente:

- 0 bugs críticos abiertos
- crash-free sessions ≥ 99.5%
- sin pérdida de progreso/configuración del usuario
- rendimiento fluido en hardware objetivo
- cobertura de tests del core mantenida o mejorada

### 🚀 Prioridad inmediata recomendada (próximos sprints)

1. Audio real + pulido UX transversal
2. Cierre de reglas avanzadas (Blackjack split/seguro) y edge cases
3. Integración progresiva del multijugador en un modo acotado
4. CI de calidad con tests automáticos y checklist de release

### 🔁 Continuidad entre sesiones (obligatorio)

- La fuente de verdad del plan es `roadmap.md`.
- Al cerrar cada sesión de implementación se actualizan: `roadmap.md`, `.github/copilot-instructions.md` y este `README.md`.
- Estado actual de Fase A:
  - ✅ Seguro (`insurance`) implementado en Blackjack (lógica + UI + tests).
  - ✅ Split implementado en Blackjack (lógica + UI + tests).
  - ✅ Corregida resolución duplicada de mano en Blackjack.
  - ✅ Refactor en `main.py` para unificar lanzadores de juegos y evitar lógica repetida.
  - ✅ `multiplayer_server.py` raíz convertido en wrapper para evitar código duplicado con `Server/multiplayer_server.py`.
  - ✅ Optimización P0 de persistencia: `ConfigManager.batch_update()` para consolidar `save_config()` repetidos.
  - ✅ Integración de batch en logros y misiones para reducir I/O por evento (`achievements.py`, `missions.py`).
  - ✅ Caché de pixmaps de cartas implementada en Poker y Blackjack para reducir coste de render.
  - ✅ Actualizaciones diferenciales de UI implementadas en Poker y Blackjack para evitar refrescos redundantes (`setPixmap`/`setText`/`setStyleSheet`).
  - ✅ Refresco de cartas en Blackjack optimizado para actualizar solo slots modificados (sin limpieza completa en cada `update_display`).
  - ✅ Patrón de actualización diferencial extendido a Tragaperras (`Tragaperras/tragaperras_ui.py`) en símbolos, resaltados y labels informativos.
  - ✅ Instrumentación baseline en UI para latencias de acciones críticas en Blackjack y Tragaperras.
  - ✅ Exportación consolidada de baseline a `performance_baseline.json` con resumen por métrica (`avg/min/max/p95`) y chequeo contra umbrales.
  - ✅ Visualización de snapshots baseline desde MainUI (`Juego` > `Rendimiento UI`).
  - ✅ Comparativa automática `Δ avg` entre snapshots consecutivos en la vista `Rendimiento UI`.
  - ✅ Workflow CI inicial en `.github/workflows/tests.yml` para tests críticos de regresión.
  - ✅ Validación parcial de regresión: `Test/test_main.py` + `Test/test_blackjack_logic.py` en verde.
  - ✅ Validación rápida de regresión: `Test/test_main.py` en verde.
  - ✅ Validación de regresión tras UI diferencial: `Test/test_blackjack_logic.py` + `Test/test_main.py` en verde (31 tests).
  - ✅ Validación de regresión en Tragaperras: `Test/test_tragaperras_table.py` + `Test/test_tragaperras.py` + `Test/test_main.py` en verde (5 tests en esta ejecución).
  - ⏳ Siguiente foco recomendado: alertas visuales reforzadas y exportación CSV de métricas históricas.

## 👨‍💻 Desarrollo y Contribución

### Patrones de Diseño Utilizados

- **Abstract Base Classes**: Patrón ABC para todos los juegos de cartas
- **Factory Pattern**: `PokerTableFactory` para diferentes configuraciones de mesa
- **Separation of Concerns**: Separación clara entre UI y lógica de juego
- **Responsive Design**: UI que escala dinámicamente con el tamaño de ventana

### Agregando Nuevos Juegos

1. Heredar de las clases ABC apropiadas en `cardCommon.py`
2. Seguir la estructura del módulo de poker (separación logic/ui/table)
3. Agregar tests unitarios completos
4. Actualizar la integración del MainUI

### Estándares de Código

- **Lenguaje**: Python 3.x con type hints
- **GUI Framework**: PyQt6 para todos los componentes UI
- **Testing**: Framework unittest (no pytest)
- **Documentación**: Docstrings completos con ejemplos

## 📄 Licencia

Este proyecto sigue los términos de licencia del repositorio principal RuleTragaperrasJuego.

## 📞 Soporte

Para problemas, sugerencias o contribuciones, por favor:

1. Revisa la sección de Troubleshooting
2. Ejecuta los tests unitarios para identificar problemas específicos
3. Abre un issue en el repositorio de GitHub

---

**¡Disfruta jugando en el casino virtual!** 🎰🃏🎮
