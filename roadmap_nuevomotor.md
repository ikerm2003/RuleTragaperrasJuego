# Roadmap de Migracion a Arcade

Plan tecnico completo para migrar RuleTragaperrasJuego desde PyQt6 a un motor 2D basado en Arcade, manteniendo la separacion actual entre logica, UI y estado compartido.

## 1) Objetivo

Completar una transicion total de la capa visual y de interaccion desde PyQt6 hacia Arcade, sin reescribir la logica principal de los juegos ni romper los contratos existentes de configuracion, estadisticas, logros, misiones y audio.

El objetivo final es que:

- La experiencia se ejecute sobre una ventana Arcade unica.
- Cada juego use escenas, render y entrada propios de un motor 2D.
- La logica de negocio permanezca separada y testeable, como hoy.
- La base PyQt6 pueda retirarse completamente al final de la migracion.

## 2) Principios de migracion

- Mantener la logica fuera de la capa visual.
- Evitar una reescritura total simultanea.
- Migrar primero la arquitectura de runtime y despues cada juego.
- Mantener compatibilidad temporal mientras conviva PyQt6 con Arcade.
- No mover reglas de negocio al render loop.
- No acoplar `config_manager`, `AchievementManager`, `MissionManager` ni `game_events.py` a Arcade.

## 3) Alcance de la migracion completa

La migracion completa incluye:

- `main.py` y el lanzador principal.
- Navegacion entre menu y juegos.
- UI y render de Poker, Blackjack, Ruleta y Tragaperras.
- Dialogos y pantallas de configuracion relevantes.
- Sistema de input, audio, feedback y animaciones dentro del runtime Arcade.
- Empaquetado y arranque principal sobre Arcade.

La migracion no debe implicar reescribir estas capas salvo adaptaciones puntuales:

- Logica de cartas y reglas en `cardCommon.py`.
- Logica de juegos en `Poker/poker_logic.py`, `Ruleta/ruleta_logic.py`, `Tragaperras/tragaperras_logic.py` y logica equivalente de Blackjack.
- Persistencia y configuracion en `config.py`.
- Progresion y eventos globales en `achievements.py`, `missions.py` y `game_events.py`.

## 4) Arquitectura objetivo

## 4.1 Capas

### Capa 1: Core de dominio

Se conserva casi intacta:

- reglas
- estado de partida
- calculos de pagos
- resolucion de rondas
- integracion con estadisticas y misiones

### Capa 2: Adaptadores de escena

Nueva capa para traducir el dominio al motor:

- presentadores o controladores de escena
- mapeo de input a comandos de juego
- coordinacion entre logica y sprites/texto
- gestion de estados visuales temporales

### Capa 3: Runtime Arcade

Nueva capa visual:

- ventana principal Arcade
- sistema de vistas o escenas
- render de texto, botones, cartas, fichas, ruleta y rodillos
- animaciones y transiciones
- despacho de eventos de raton y teclado

## 4.2 Estructura de carpetas objetivo

Se propone introducir una estructura paralela sin romper la actual:

```text
arcade_app/
  app.py
  scene_manager.py
  assets.py
  ui/
    widgets.py
    buttons.py
    panels.py
    overlays.py
  scenes/
    main_menu_scene.py
    settings_scene.py
    poker_scene.py
    blackjack_scene.py
    ruleta_scene.py
    tragaperras_scene.py
  presenters/
    poker_presenter.py
    blackjack_presenter.py
    ruleta_presenter.py
    tragaperras_presenter.py
  renderers/
    cards.py
    chips.py
    reels.py
    wheel.py
    text.py
```

La estructura existente de logica puede mantenerse donde esta.

## 5) Mapeo de responsabilidades

## 5.1 Lo que sale de PyQt6

- `QMainWindow`, `QWidget`, `QDialog`, `QLabel`, `QPushButton`, `QTimer`, layouts y stylesheets.
- Eventos Qt como `resizeEvent`, señales y slots en la UI.

## 5.2 Su equivalente en Arcade

- `arcade.Window` como runtime principal.
- `arcade.View` para menu, configuracion y juegos.
- `on_draw`, `on_update`, `on_key_press`, `on_mouse_press` como ciclo base.
- Botones y paneles propios del proyecto o `arcade.gui` donde simplifique.
- Scheduler propio basado en `delta_time` para animaciones y callbacks.

## 5.3 Lo que no debe cambiar

- Los modelos de datos de juego.
- Las APIs publicas de logica, salvo cuando hoy dependan de callbacks de UI.
- Los contratos con `config_manager`.
- El contrato unificado de `game_events.py`.

## 6) Cambios tecnicos necesarios antes de migrar vistas

Antes de mover juegos hay que reducir dependencia implícita de UI dentro de algunos modulos.

### 6.1 Extraer controladores por juego

Cada juego debe tener un controlador no visual que haga de puente entre logica y escena. Por ejemplo:

- `PokerController`
- `BlackjackController`
- `RuletaController`
- `TragaperrasController`

Responsabilidades:

- iniciar partida
- exponer estado serializable o consumible por la vista
- ejecutar acciones del usuario
- devolver resultados, mensajes y flags visuales

### 6.2 Formalizar snapshots de estado

Cada juego debe poder producir un snapshot limpio para la UI, por ejemplo:

- cartas visibles
- turno actual
- botones habilitados
- saldo y apuesta
- mensajes de resultado
- indicadores de animacion pendientes

Esto evita que la escena Arcade inspeccione objetos internos arbitrariamente.

### 6.3 Unificar recursos y rutas

Hay que centralizar:

- carga de imagenes
- spritesheets
- fuentes
- audio
- escalado de assets

Conviene introducir un catalogo de recursos unico antes de migrar escenas.

## 7) Plan por fases

## Fase 0 - Decision y preparacion

Objetivo: dejar aprobado el enfoque y preparar el terreno sin romper PyQt6.

Entregables:

- Crear `roadmap_nuevomotor.md`.
- Confirmar Arcade como motor objetivo.
- Añadir dependencia `arcade` y validar ventana minima local.
- Definir layout objetivo de `arcade_app/`.
- Identificar modulos que aun mezclan logica con callbacks visuales.

Criterio de salida:

- Se puede abrir una ventana Arcade vacia desde el repositorio.
- La estructura base de migracion queda creada.

## Fase 1 - Runtime comun Arcade

Objetivo: construir la base del nuevo runtime antes de tocar un juego real.

Entregables:

- `arcade_app/app.py` con ventana principal.
- `scene_manager.py` para navegar entre vistas.
- escena de menu principal funcional.
- escena de configuracion minima funcional.
- sistema base de botones, paneles y texto.
- integracion inicial con `sound_manager.py` y `config_manager`.

Criterio de salida:

- El proyecto arranca en Arcade.
- Menu y navegacion existen sin PyQt6 en la ruta principal experimental.

## Fase 2 - Contratos vista-logica

Objetivo: desacoplar por completo la UI existente de la logica para que Arcade consuma contratos claros.

Entregables:

- controladores por juego
- snapshots de estado por juego
- comandos de entrada normalizados por juego
- tests de controladores sin dependencia visual

Criterio de salida:

- Un controlador puede ser testeado sin PyQt6 ni Arcade.
- Las escenas futuras consumen solo el controlador y su snapshot.

## Fase 3 - Migracion piloto de Tragaperras

Objetivo: validar la arquitectura con el juego mas agradecido visualmente.

Razones:

- Tiene una fantasia visual clara.
- Se beneficia mucho de animaciones y render 2D.
- Su flujo es mas controlado que Poker multijugador.

Entregables:

- `tragaperras_scene.py`
- renderer de rodillos y simbolos
- animaciones de spin en Arcade
- integracion con estadisticas, logros, misiones y audio
- paridad funcional con la version PyQt6

Criterio de salida:

- La tragaperras en Arcade permite jugar end to end.
- La UI PyQt6 de tragaperras puede marcarse como legacy.

## Fase 4 - Migracion de Ruleta

Objetivo: migrar un juego con tablero y animacion circular.

Entregables:

- `ruleta_scene.py`
- renderer de mesa y fichas
- animacion de giro y resultado
- historial y estado visual equivalentes

Criterio de salida:

- Ruleta funcional en Arcade con paridad suficiente de UX y reglas.

## Fase 5 - Migracion de Blackjack

Objetivo: migrar un juego de cartas con flujo de decisiones mas denso.

Entregables:

- `blackjack_scene.py`
- renderer reutilizable de cartas y fichas
- soporte de acciones: hit, stand, double, split, insurance
- overlays de estado y resolucion

Criterio de salida:

- Blackjack completo jugable en Arcade con todos los flujos actuales.

## Fase 6 - Migracion de Poker

Objetivo: migrar el modulo mas complejo al final, con la arquitectura ya estabilizada.

Entregables:

- `poker_scene.py`
- renderer de mesa, jugadores, cartas comunes y bote
- soporte para 2-9 jugadores
- estados de ronda y acciones equivalentes
- preparacion para multiplayer futuro sobre el nuevo runtime

Criterio de salida:

- Poker jugable en Arcade en el alcance hoy soportado por la version PyQt6.

## Fase 7 - Configuracion, overlays y utilidades restantes

Objetivo: retirar dependencias residuales de PyQt6 fuera de los juegos.

Entregables:

- escena completa de configuracion
- dialogs convertidos a overlays o paneles Arcade
- pantallas auxiliares: historial, rendimiento debug si se conserva, creditos u otras vistas secundarias

Criterio de salida:

- No queda ningun flujo de usuario que requiera PyQt6 para uso normal.

## Fase 8 - Corte final y retirada de PyQt6

Objetivo: completar la transicion total.

Entregables:

- `main.py` o nuevo entrypoint apuntando a Arcade como ruta principal
- desactivacion o eliminacion progresiva de entrypoints PyQt6
- limpieza de dependencias y assets no usados
- actualizacion de tests, README y documentacion

Criterio de salida:

- El producto arranca y opera completamente sobre Arcade.
- PyQt6 deja de ser dependencia requerida.

## 8) Orden de migracion recomendado

Orden realista:

1. Runtime base Arcade.
2. Contratos vista-logica.
3. Tragaperras.
4. Ruleta.
5. Blackjack.
6. Poker.
7. Configuracion y remates.
8. Corte final.

Este orden reduce riesgo porque valida primero el motor con el juego mas visual y deja el mas complejo para cuando ya existan patrones reutilizables.

## 9) Estrategia de convivencia temporal

Durante gran parte del proceso coexistiran PyQt6 y Arcade.

Reglas de convivencia:

- PyQt6 sigue siendo la ruta estable hasta que haya paridad suficiente en Arcade.
- Cada juego se migra y valida por separado.
- El launcher puede ofrecer un flag temporal de runtime o entrypoint experimental.
- No se eliminan modulos PyQt6 hasta pasar criterios de salida por juego.

## 10) Adaptaciones de testing

Hay que preservar la ventaja actual de la logica testeable.

### 10.1 Tests que deben seguir iguales

- Tests de reglas.
- Tests de config.
- Tests de logros, misiones y eventos.

### 10.2 Tests nuevos a introducir

- Tests de controladores por juego.
- Tests de snapshots y comandos.
- Tests de integracion minima del runtime Arcade.
- Tests de paridad funcional entre PyQt6 legacy y escena Arcade cuando aplique.

### 10.3 Lo que no conviene probar de forma fragil

- Coordenadas pixel perfect salvo donde sea critico.
- Animaciones frame a frame sin necesidad.

## 11) Riesgos principales y mitigaciones

### Riesgo 1: mezclar logica con render loop

Mitigacion:

- introducir controladores y snapshots antes de migrar vistas

### Riesgo 2: reescritura demasiado grande

Mitigacion:

- migracion por juego con convivencia temporal

### Riesgo 3: perder productividad en UI utilitaria

Mitigacion:

- usar overlays y widgets simples, sin intentar replicar todo Qt de forma literal

### Riesgo 4: degradar accesos a configuracion y dialogs

Mitigacion:

- migrar pronto menu y settings base para validar ergonomia de Arcade

### Riesgo 5: romper tests por acoplamiento visual

Mitigacion:

- desplazar la logica visual a presentadores/controladores con contratos estables

## 12) Estimacion realista

Si la migracion la haces en ratos de desarrollo individual y manteniendo el proyecto vivo, una estimacion razonable es:

- Fase 0-1: 1 a 2 semanas
- Fase 2: 1 a 2 semanas
- Fase 3: 1 a 2 semanas
- Fase 4: 1 semana
- Fase 5: 1 a 2 semanas
- Fase 6: 2 a 4 semanas
- Fase 7-8: 1 a 2 semanas

Rango total realista: 8 a 15 semanas.

Si el objetivo es alta calidad visual y buena paridad UX, conviene asumir el tramo alto del rango.

## 13) Criterios de aceptacion para la migracion completa

La migracion se considera completada cuando:

- Los cuatro juegos se pueden lanzar y jugar en Arcade.
- Menu, configuracion y navegacion principal ya no dependen de PyQt6.
- Tests de logica siguen en verde.
- Existe cobertura minima de controladores y contratos de escena.
- Audio, configuracion y progresion siguen funcionando.
- PyQt6 deja de ser dependencia operativa del flujo principal.

## 14) Primer sprint recomendado

Sprint 1 propuesto:

1. Crear `arcade_app/` y ventana base.
2. Implementar `scene_manager.py`.
3. Crear menu principal Arcade funcional.
4. Introducir el primer controlador desacoplado, empezando por Tragaperras.
5. Definir snapshot de Tragaperras.
6. Dejar una escena minima de Tragaperras que renderice estado sin animaciones complejas.

Ese sprint no completa la migracion, pero elimina la mayor incertidumbre tecnica.

## 15) Recomendacion final

La migracion a Arcade es razonable para este proyecto si el objetivo es que deje de sentirse como una app de escritorio y pase a sentirse como un juego 2D. La decision correcta no es reescribir todo de golpe, sino migrar por capas, dejando Poker para el final y usando Tragaperras como validacion arquitectonica.

La clave para asegurar la transicion completa no es Arcade en si, sino imponer una capa de controladores y snapshots entre la logica actual y la futura UI del motor.
