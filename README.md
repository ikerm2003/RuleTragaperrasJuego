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
- [x] **Poker**: Completo con todas las características
  - Texas Hold'em con soporte 2-9 jugadores
  - Sistema de IA para bots con estrategias básicas
  - Interfaz profesional con animaciones y efectos
  - 30 tests unitarios con 100% de cobertura
- [x] **Tragaperras**: Módulo operativo con UI animada y estadísticas
  - Sistema completo de slot machine con 5 rodillos
  - Cálculo dinámico de RTP (Return to Player)
  - Animaciones de giro y resaltado de líneas ganadoras
  - Sistema de recuperación de pérdidas y estadísticas
  - Tests completos de lógica y UI
- [x] **Sistema de Configuración**: Completo
  - Soporte multi-idioma (Español/Inglés)
  - Configuración de pantalla, animaciones y gameplay
  - Persistencia en archivo JSON
- [x] **MainUI**: Menú principal funcional
  - Lanzador integrado de juegos
  - Acceso a configuración desde menú
- [x] **Blackjack**: Implementación completa
  - Lógica completa del juego con dealer AI
  - Clases BlackjackCard y BlackjackDeck heredando de cardCommon
  - Manejo completo de apuestas y balance
  - Acciones: Hit, Stand, Double Down
  - Cálculo correcto de valores con manejo de Ases
  - Detección de Blackjack con pago 3:2
  - UI profesional con visualización de cartas y estado del juego
  - Integración completa con MainUI
- [x] **Ruleta**: Implementación completa
  - Ruleta europea con 37 números (0-36)
  - Todos los tipos de apuestas estándar:
    * Pleno (35:1), Caballo (17:1), Transversal (11:1)
    * Cuadro (8:1), Línea (5:1)
    * Docenas y Columnas (2:1)
    * Rojo/Negro, Par/Impar, Alto/Bajo (1:1)
  - Animación de ruleta giratoria
  - Mesa de apuestas profesional
  - Historial de números y estadísticas
  - Sistema de balance y gestión de fichas
  - Integración completa con MainUI

### 🚀 Características Planeadas

- [ ] **Multiplayer online**: Soporte para juego en red
- [ ] **Misiones diarias**: Sistema de misiones y recompensas
- [ ] **Auto-refill**: Recarga automática diaria de dinero
- [ ] **Atajos de teclado**: Controles de teclado completos
- [ ] **Estadísticas avanzadas**: Tracking de manos y estadísticas
- [ ] **Modo torneo**: Soporte para torneos multi-mesa
- [ ] **Temas personalizables**: Múltiples temas visuales
- [ ] **Efectos de sonido**: Sistema de audio completo
- [ ] **Sistema de achievements**: Logros y trofeos desbloqueables
- [ ] **Modo práctica**: Juego sin dinero para aprendizaje
- [ ] **Más animaciones**: Card flips, chip movements, efectos avanzados

### 🎯 Mejoras Técnicas Planeadas
- [ ] **IA avanzada**: Bots con múltiples personalidades y estrategias adaptativas
- [ ] **Hand history**: Sistema de historial y replay de manos
- [ ] **Variantes de poker**: Omaha, Seven-Card Stud, etc.
- [ ] **Optimizaciones**: Mejoras de rendimiento y uso de memoria
- [ ] **Más idiomas**: Soporte adicional más allá de Español/Inglés
- [ ] **Sistema de logs**: Logging mejorado para debugging y análisis
- [ ] **Testing automatizado**: CI/CD con tests automáticos
- [ ] **Persistencia de datos**: Sistema de guardado de progreso y perfil de usuario
- [ ] **Análisis de patrones**: Sistema de análisis de comportamiento de jugadores
- [ ] **Splits en Blackjack**: Implementar división de pares
- [ ] **Seguro en Blackjack**: Implementar apuesta de seguro contra Blackjack del dealer

### 📝 Guía de Implementación Óptima

Para implementar las características planeadas de manera eficiente:

#### 🏗️ Arquitectura y Diseño
- **Modularidad**: Mantener separación estricta entre lógica, UI y gestión de estado
- **Reutilización**: Aprovechar componentes existentes (ej: sistema de configuración)
- **Escalabilidad**: Diseñar para soportar extensiones futuras sin refactoring mayor
- **Testing First**: Escribir tests antes de implementar nuevas características

#### ⚡ Optimización y Rendimiento
- **Lazy Loading**: Cargar módulos y recursos solo cuando se necesiten
- **Caching**: Cachear resultados de cálculos costosos (ej: evaluación de manos)
- **Async Operations**: Usar operaciones asíncronas para UI responsiva
- **Memory Management**: Liberar recursos no utilizados, especialmente en cambios de juego

#### 🎯 Priorización Sugerida
1. **Alta prioridad**: Completar Blackjack y Ruleta (completar juegos base)
2. **Media prioridad**: Sistema de estadísticas, hand history, efectos de sonido
3. **Baja prioridad**: Multiplayer online, torneos, variantes de poker avanzadas

#### 🔧 Mejores Prácticas
- **Documentación**: Mantener README.md y docstrings actualizados
- **Commits atómicos**: Un feature/fix por commit con mensajes descriptivos
- **Code review**: Revisar cambios antes de merge
- **Backwards compatibility**: Mantener compatibilidad con código existente

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
