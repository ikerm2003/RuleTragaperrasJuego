# Roadmap de Optimizaciones - RuleTragaperrasJuego

Documento maestro para llevar el proyecto al máximo rendimiento sin perder ninguna funcionalidad.

> Este roadmap define qué hacer (objetivos, prioridades y criterios de aceptación), no cómo implementarlo.

## Estado de ejecución (2026-03-13)

- Estado de continuidad: **Pausado temporalmente** por prioridad de producto; la ejecución continúa por `roadmap.md` (Fase B).

- Resumen real de implementación sobre la todo-list: 19 completadas, 23 pendientes, 42 totales.
- Completado en `main.py` (Rendimiento UI): presets rápidos de rango temporal (`Todo`, `Ultima hora`, `Ultimas 24h`, `Ultimos 7 dias`).
- Completado en `main.py` (Rendimiento UI): vista agregada de tendencia por métrica para el conjunto filtrado (avg agregado, delta del periodo, min/max y brechas de umbral).
- Completado en `main.py` (Rendimiento UI): comparativa agregada por fuente para el conjunto filtrado (avg agregado, delta, métricas incluidas y brechas de umbral).
- Completado en `main.py` (Rendimiento UI): ordenación interactiva para tablas agregadas y detalle por snapshot.
- Completado en `main.py`: instrumentación de tiempos de arranque del menú principal y transiciones de apertura/retorno entre ventanas con exportación a `performance_baseline.json` al cerrar la app.
- Completado en validación: tests unitarios específicos para presets y agregación en `Test/test_main.py`.
- Completado en validación: tests unitarios específicos para agregación por fuente y ordenación en `Test/test_main.py`.
- Completado en validación: tests unitarios específicos para resumen de métricas del menú principal y ordenación por snapshots en `Test/test_main.py`.
- Siguiente foco recomendado (P1): medir frecuencia de I/O en rutas calientes y exponerla en `Rendimiento UI` para correlacionar presión de persistencia con regresiones de latencia.

---

## 1) Objetivo global

Convertir el proyecto en una app de casino de escritorio con rendimiento de nivel producto.

- Arranque rápido.
- Fluidez constante en UI y acciones de juego.
- Persistencia eficiente sin bloqueos perceptibles.
- Uso controlado de CPU, memoria e I/O en sesiones largas.
- Escalabilidad para multiplayer y nuevas funcionalidades.

---

## 2) Restricciones no negociables

- Cero regresiones en reglas de Poker, Blackjack, Ruleta y Tragaperras.
- Compatibilidad total con `main.py` y lanzadores por módulo.
- Integridad total de `casino_config.json` y progreso de jugador.
- UX actual preservada (atajos, flujo, mensajes, estados).

---

## 3) KPIs objetivo de rendimiento

### Arranque

- Reducir tiempo de arranque de app principal frente al baseline.
- Reducir tiempo de apertura de cada juego desde el menú principal.

### Fluidez

- Reducir latencia en acciones clave: apostar, girar, hit/stand, fold/call, abrir/cerrar módulos.
- Evitar bloqueos de UI por operaciones de estado o persistencia.

### Eficiencia

- Reducir operaciones de disco por acción de juego.
- Reducir trabajo de render repetitivo en cada `update_display`.
- Mantener consumo de memoria estable en sesiones prolongadas.

### Estabilidad

- Sin inconsistencias en balance, estadísticas, logros y misiones.
- Sin degradación progresiva tras alternar entre juegos múltiples veces.

---

## 4) Priorización por impacto

## P0  Impacto máximo inmediato

- Consolidar persistencia para evitar guardados redundantes por evento.
- Eliminar renderizado repetido de cartas y recursos visuales idénticos.
- Aplicar actualizaciones de UI solo ante cambios reales de estado.
- Establecer baseline de rendimiento y comparativas obligatorias.

## P1  Impacto alto acumulado

- Optimizar pipeline de estadísticas, misiones y logros por jugada.
- Optimizar refresco en vistas más activas (Poker/Tragaperras/Blackjack).
- Reducir coste de transición entre ventanas y módulos.
- Revisar timers/eventos para eliminar trabajo innecesario en background.

## P2  Escalabilidad y mantenibilidad

- Unificar contratos y lifecycle de módulos de juego.
- Reducir acoplamiento UI/lógica/persistencia.
- Mejorar eficiencia de comunicación en multiplayer.
- Integrar quality gates de rendimiento en releases.

## P3  Optimización continua

- Pulido incremental de micro-costes (UI, imports, estructuras de datos).
- Eliminación de deuda técnica que afecte rendimiento futuro.
- Auditoría periódica para detectar regresiones tempranas.

---

## 5) Todo-list completa de optimizaciones (qué hacer)

### 5.1 Persistencia y estado

- [x] Reducir frecuencia de `save_config` en rutas de ejecución caliente.
- [x] Agrupar cambios relacionados en una sola persistencia efectiva.
- [ ] Evitar escrituras cuando el valor final no cambia.
- [ ] Diferenciar datos que requieren persistencia inmediata frente a diferida.
- [ ] Garantizar recuperación consistente ante cierres inesperados.

### 5.2 Render y UI

- [x] Evitar recreación de pixmaps/elementos visuales idénticos.
- [x] Limitar repintado a widgets realmente modificados.
- [x] Reducir reasignaciones innecesarias de estilos y textos.
- [x] Favorecer actualizaciones diferenciales en lugar de refresh completo.
- [ ] Homogeneizar la política de escalado para minimizar recálculos visuales.

### 5.3 Lógica de juego

- [ ] Eliminar cálculos repetidos dentro de una misma acción.
- [ ] Reutilizar evaluaciones costosas en turnos y validaciones frecuentes.
- [ ] Simplificar rutas de decisión en funciones críticas.
- [ ] Preservar 100% exactitud de reglas y pagos.

### 5.4 Misiones, logros y estadísticas

- [x] Consolidar actualización de progreso por evento de juego.
- [x] Garantizar una sola persistencia por acción compuesta.
- [ ] Eliminar duplicación de cómputo entre sistemas transversales.
- [ ] Mantener exactitud en recompensas y desbloqueos.

### 5.5 Multiplayer

- [x] Mantener una sola fuente de verdad para servidor y estado de sesión.
- [ ] Reducir broadcasts y payloads innecesarios.
- [ ] Mejorar eficiencia bajo múltiples conexiones simultáneas.
- [x] Preservar reglas actuales de token/reconexión.

### 5.6 Arranque y carga de módulos

- [ ] Diferir trabajo no crítico fuera de la ruta inicial.
- [ ] Optimizar inicialización de ventanas y componentes pesados.
- [ ] Unificar comportamiento de `owns_app` en todos los entry points.
- [ ] Reducir coste de importación y bootstrap por módulo.

### 5.7 Estructura de código

- [x] Eliminar funciones y bloques duplicados.
- [ ] Estandarizar patrones repetidos entre juegos.
- [ ] Limpiar imports no usados en rutas principales.
- [x] Reducir complejidad en funciones con alta frecuencia de ejecución.

### 5.8 Validación y rendimiento

- [x] Definir baseline inicial por módulo y por flujo crítico.
- [ ] Hacer comparativa obligatoria antes/después de cada bloque P0/P1.
- [x] Añadir validación de no-regresión de rendimiento a tests clave.
- [ ] Mantener pruebas funcionales críticas en verde durante toda la ejecución.

### 5.9 Observabilidad

- [x] Medir tiempos de arranque, carga de ventana y acciones principales.
- [ ] Medir frecuencia de I/O en rutas calientes.
- [x] Medir coste de render en ciclos de actualización de UI.
- [ ] Establecer umbrales mínimos para bloquear regresiones.

### 5.10 UX sin cambios funcionales

- [x] Reducir latencia percibida en interacción recurrente.
- [x] Evitar micro-congelaciones durante persistencia y update de estado.
- [ ] Mantener feedback visual coherente tras cada optimización.
- [x] Preservar accesos rápidos, navegación y comportamiento actual.

---

## 6) Criterios de aceptación por fase

### Fase A (P0)

- Persistencia consolidada en rutas calientes.
- Reducción medible de trabajo de render repetitivo.
- Baseline y comparativas documentadas.
- Test funcional prioritario en verde.

### Fase B (P1)

- Coste por jugada estable en stats/misiones/logros.
- Mejora de fluidez percibida en todos los juegos.
- Sin incidencias funcionales nuevas.

### Fase C (P2)

- Arquitectura más predecible y menos acoplada.
- Mejor comportamiento bajo carga multiplayer.
- Gates de rendimiento integrados en ciclo de entrega.

### Fase D (P3)

- Proceso continuo de mejora sin deuda acumulada.
- Regresiones detectadas y corregidas dentro del sprint.

---

## 7) Riesgos y mitigación

- Riesgo de pérdida de datos al optimizar persistencia.
  - Mitigación: política explícita por categoría de dato e integridad validada.

- Riesgo de desincronización visual al optimizar UI.
  - Mitigación: validación funcional + visual en cada juego.

- Riesgo de efecto cascada en módulos compartidos.
  - Mitigación: despliegue por fases, validación incremental y rollback claro.

- Riesgo de mejoras locales que degraden el sistema global.
  - Mitigación: medición end-to-end obligatoria contra baseline.

---

## 8) Checklist de release de optimización

- Baseline actualizada y comparativa completada.
- Objetivos de fase documentados (cumplidos o desviaciones justificadas).
- Suite de tests funcionales en verde.
- Validación manual en Poker, Blackjack, Ruleta y Tragaperras.
- Verificación de integridad de balance/stats/logros/misiones.
- Verificación de arranque por `main.py` y por cada `*_main.py`.
- Continuidad documental actualizada (`roadmap.md`, `README.md`, `.github/copilot-instructions.md`).

---

## 9) Orden recomendado de ejecución

1. Persistencia eficiente + baseline.
2. Render diferencial + reutilización visual.
3. Consolidación de pipeline stats/misiones/logros.
4. Startup/lifecycle de módulos.
5. Quality gates y ciclo continuo.

---

## 10) Definición de óptimo alcanzado

Se considera óptimo alcanzado cuando:

- El rendimiento mejora de forma medible y perceptible en todos los juegos.
- No existe pérdida funcional ni inconsistencia de estado.
- El coste de mantenimiento y evolución disminuye claramente.
- El sistema queda preparado para crecer sin degradación significativa.
