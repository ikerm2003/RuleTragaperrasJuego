# 🎰 RuleTragaperrasJuego - Casino Game Collection

Una colección completa de juegos de casino implementada en Python con PyQt6, que incluye Poker Texas Hold'em, Blackjack, Ruleta y Tragaperras con una interfaz moderna y profesional.

## 📋 Descripción General

RuleTragaperrasJuego es un proyecto de casino virtual que presenta múltiples juegos de cartas y casino. Actualmente ofrece un módulo completo de Poker Texas Hold'em y una tragaperras 3x3 de última generación, ambos con interfaces PyQt6 profesionales y listas para jugar.

### 🎮 Módulos Principales

- **🃏 Poker** (Completo): Implementación completa de Texas Hold'em

  - Soporte para 2-9 jugadores con posicionamiento automático
  - Sistema de IA para bots con estrategias básicas
  - Interfaz profesional con mesa de poker y animaciones
  - Evaluación completa de manos y manejo de apuestas lateral
- **🔥 Blackjack** (Básico): Implementación básica de Blackjack

  - Lógica fundamental del juego
  - Interfaz básica de PyQt6
- **🎯 Ruleta** (Stub): Preparado para implementación
- **🎰 Tragaperras** (Completa): Máquina de 3x3 con animación de rodillos y líneas de pago configurables
  - Nueve líneas de pago clásicas y diagonales
  - Animación de carretes con modo autoplay y resaltado de premios
  - Gestión avanzada de apuestas, RTP ajustable y estadísticas en vivo
  - Interfaz PyQt6 responsiva con historial y controles dinámicos
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

#### Tragaperras (Máquina 3x3 completa)

```bash
python Tragaperras/tragaperras_main.py
```

Incluye animación de rodillos, historial de tiradas, estadísticas en vivo, autoplay y controles para líneas/ apuesta por línea.

#### Ruleta (En desarrollo)

```bash
python Ruleta/ruleta.py
```

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
├── Blackjack/             # Módulo básico de Blackjack
│   └── blackjack.py       # Implementación básica
├── Ruleta/                # Módulo de Ruleta (stub)
│   └── ruleta.py          # Preparado para implementación
├── Tragaperras/           # Módulo de Tragaperras (completo)
│   ├── tragaperras_main.py   # Punto de entrada y gestión de QApplication
│   ├── tragaperras_logic.py  # Lógica de máquina 3x3 con RTP configurable
│   ├── tragaperras_table.py  # Controlador con historial, estadísticas y autoplay
│   └── tragaperras_ui.py     # UI PyQt6 con animaciones de rodillos
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

### 🎰 Tragaperras 3x3 (Completa)

- **Líneas de pago múltiples**: Nueve patrones clásicos con comodines y scatter
- **Animación de rodillos**: Giro con velocidad configurable y resaltado de premios
- **Autoplay inteligente**: Reproducción automática con control de intervalo
- **Estadísticas en vivo**: Balance, RTP acumulado y conteo de símbolos especiales
- **Historial detallado**: Registro de las últimas tiradas con resultados resumidos
- **Gestión avanzada de apuestas**: RTP dinámico, apuestas por línea y premio consolación opcional

### ⚙️ Sistema de Configuración Avanzado

- **Configuración de pantalla**: Pantalla completa, resolución, VSync
- **Idiomas**: Soporte para Español e Inglés
- **Animaciones**: Velocidad configurable o desactivación
- **Configuración de juego**: Timeouts, confirmaciones, hints de probabilidad

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

## 🔮 Roadmap y Futuras Mejoras

### 📋 Estado Actual

- [X] **Poker**: Completo con todas las características
- [X] **Sistema de Configuración**: Completo
- [X] **MainUI**: Menú principal funcional
- [ ] **Blackjack**: Implementación básica (en progreso)
- [ ] **Ruleta**: Preparado para implementación
- [X] **Tragaperras**: Módulo operativo con UI animada y estadísticas

### 🚀 Características Planeadas

- [ ] **Multiplayer online**: Soporte para juego en red
- [ ] **Misiones diarias**: Sistema de misiones y recompensas
- [ ] **Auto-refill**: Recarga automática diaria de dinero
- [ ] **Atajos de teclado**: Controles de teclado completos
- [ ] **Estadísticas avanzadas**: Tracking de manos y estadísticas
- [ ] **Modo torneo**: Soporte para torneos multi-mesa
- [ ] **Temas personalizables**: Múltiples temas visuales
- [ ] **Efectos de sonido**: Sistema de audio completo

### 🎯 Mejoras Técnicas Planeadas

- [ ] IA de bots más avanzada con múltiples personalidades
- [ ] Sistema de hand history y replay
- [ ] Soporte para variantes de poker (Omaha, Seven-Card Stud)
- [ ] Optimizaciones de rendimiento y memoria
- [ ] Soporte para más idiomas

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
