title = get_text('casino_title')  # "Casino de tu mama" or "Your Mom's Casino"
poker = get_text('poker')         # "Póker" or "Poker"
demo_features.py    - Feature demonstration script
# Feature Highlights

Resumen actualizado de las funcionalidades más relevantes del proyecto.

## 🎨 Poker Gameplay Animations

Las animaciones del módulo de póker se apoyan en `QPropertyAnimation` para ofrecer una experiencia fluida.

- Reparto de cartas con retardos configurables.
- Resaltado del jugador activo con transiciones suaves.
- Retroalimentación visual para cambios de apuesta y bote.
- Velocidad de animación ligada a la configuración global del usuario.

```python
# poker_ui.py
def animate_card_deal(self, card_label: QLabel, delay: int = 0) -> None:
    animation = QPropertyAnimation(card_label, b"pos")
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.setDuration(int(250 * self.current_scale))
    animation.setStartValue(start_point)
    animation.setEndValue(end_point)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
```

## 💰 Poker Bet Display

El panel de apuestas del póker diferencia claramente entre la apuesta actual y el acumulado, animando los cambios de valor con colores dorados y bordes suaves.

- Seguimiento preciso de apuestas en cada ronda.
- Etiquetas con sombreado y tipografía consistente.
- Animaciones de rebote al actualizar cantidades.

## 🎰 Slot Machine Module

La tragaperras 3x3 replica los estándares arquitectónicos del póker: lógica pura, controlador de mesa y UI desacoplada.

### Highlights

- **Líneas de pago avanzadas**: Nueve patrones, comodines y símbolos scatter con multiplicadores.
- **RTP configurable**: Multiplicadores dinámicos y premio de consolación en giros perdidos.
- **Historial y estadísticas**: Balance, RTP acumulado, premio mayor y conteo de comodines.
- **Autoplay**: Intervalo ajustable, activación/desactivación inmediata y reenganche tras cada giro.
- **Animación de rodillos**: Mezcla pseudoaleatoria mientras gira y revelado sincronizado del resultado.

```text
Tragaperras/
├── tragaperras_logic.py   # Lógica y evaluación de líneas
├── tragaperras_table.py   # Callbacks de UI, historial y estadísticas
├── tragaperras_ui.py      # Ventana PyQt6 con animación y controles
└── tragaperras_main.py    # Punto de entrada reutilizable desde main.py
```

### Callbacks disponibles

- `balance_changed`
- `bet_changed`
- `lines_changed`
- `spin_started` / `spin_completed`
- `statistics_changed`
- `autoplay_changed`

## ⚙️ Configuration System

El `ConfigManager` centraliza preferencias de pantalla, interfaz y jugabilidad, persistidas en `casino_config.json`.

- Ajustes de pantalla: fullscreen y resoluciones predefinidas.
- Preferencias de interfaz: idioma, velocidad de animación, tooltips, sonido.
- Parámetros de juego: tiempo de auto-fold, confirmaciones y hints.
- Sistema de recarga diaria: auto-refill de balance configurable.
- API de acceso sencillo (`config_manager.get(...)`, `set(...)`, `save_config()`).

## ⌨️ Keyboard Shortcuts

Sistema completo de atajos de teclado para navegación rápida:

- **Menú principal**: Teclas 1-4 para lanzar juegos, F11 para fullscreen, ESC para salir.
- **Integración global**: Los atajos están disponibles en toda la aplicación.
- **Configuración rápida**: Ctrl+S para acceder a configuración.
- **Indicadores visuales**: Los botones muestran los atajos asociados.

## 💰 Daily Auto-Refill System

Sistema automático de recarga de balance diario:

- **Auto-refill inteligente**: Detecta nuevo día y recarga si el balance está bajo.
- **Balance configurable**: Starting balance de 1000 créditos por defecto.
- **Notificaciones**: Mensajes informativos cuando ocurre la recarga.
- **Persistencia**: El sistema guarda último login y balance en `casino_config.json`.

## � Internationalization

Todo el contenido visible pasa por `get_text`, con diccionarios completos en español e inglés.

- Nuevas claves para la tragaperras: balance, autoplay, mensajes de victoria y estadísticas.
- Ventanas y menús (póker, tragaperras, menú principal) responden al cambio de idioma sin reiniciar.

## 🎮 Casino UI & Main Menu

`main.py` ofrece un lanzador central con estilo de casino, integrando póker y la nueva tragaperras.

- Botones estilizados con gradientes y sombras.
- Acceso directo a diálogo de configuración.
- Gestión de ventanas hija: al cerrar un juego se restaura el menú principal.

## 🛠️ Technical Overview

- Arquitectura modular: `*_logic.py`, `*_table.py`, `*_ui.py`, `*_main.py`.
- Uso extensivo de PyQt6 con escalado responsivo (`get_scaled_size`).
- Callbacks entre lógica y UI para evitar dependencias circulares.
- Tests organizados en `Test/` y scripts de entorno (`setup_env.bat`).

## 🚀 Usage Snippets

```bash
# Menú principal del casino
python main.py

# Póker Texas Hold'em
python Poker/poker_main.py

# Tragaperras 3x3 con animación
python Tragaperras/tragaperras_main.py
```

## 🧪 Testing

```bash
python -m unittest Poker/test_poker.py -v
python -m unittest test_tragaperras_logic -v
python -m unittest Test.test_tragaperras -v
python -m unittest Test.test_tragaperras_table -v
```

## � Future Enhancements

- Sonido ambiente y efectos sincronizados.
- Implementación completa de Blackjack y Ruleta.
- Misiones diarias, estadísticas globales y soporte multijugador.
- Más idiomas y temas visuales customizables.

## 🔧 Development Notes

- Mantener la separación lógica/UI y reutilizar callbacks existentes.
- Añadir nuevas claves de traducción en `config.py` y usar `get_text`.
- Incluir tests unitarios cuando se amplíe la lógica de juego.
- Ajustar animaciones respetando las preferencias definidas en `ConfigManager`.