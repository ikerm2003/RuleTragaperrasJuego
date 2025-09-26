@echo off
echo ====================================
echo  Casino RuleTragaperrasJuego Setup
echo ====================================
echo.

REM Verificar si existe el directorio .venv
if not exist ".venv" (
    echo ERROR: No se encontro el directorio .venv
    echo Por favor, ejecuta: python -m venv .venv
    pause
    exit /b 1
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

if %ERRORLEVEL% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Verificar que .venv\Scripts\activate.bat existe
    pause
    exit /b 1
)

echo Entorno virtual activado correctamente

echo.
echo Instalando dependencias desde requirements.txt...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo ====================================
echo  Setup completado correctamente!
echo ====================================
echo.
echo Para ejecutar la aplicacion:
echo   1. Aplicacion principal: python main.py  
echo   2. Modulo Poker: python Poker\poker_main.py
echo   3. Modulo Blackjack: python Blackjack\blackjack.py
echo.
echo NOTA: Asegurate de tener el entorno virtual activado
echo      ejecutando: .venv\Scripts\activate.bat
echo.

:ask_run
set /p RUN_CHOICE="Quieres ejecutar un modulo ahora? (S/N): "
if /i "%RUN_CHOICE%"=="S" goto module_menu
if /i "%RUN_CHOICE%"=="N" goto finish
echo Opcion no valida. Responde con S o N.
echo.
goto ask_run

:module_menu
echo.
echo Selecciona el modulo a ejecutar:
echo   1. Aplicacion principal (main.py)
echo   2. Modulo Poker (Poker\poker_main.py)
echo   3. Modulo Blackjack (Blackjack\blackjack.py)
echo   4. Volver al menu anterior
echo   0. Salir
echo.

set /p MODULE_CHOICE="Opcion [0-4]: "
if "%MODULE_CHOICE%"=="1" (
    echo.
    echo Lanzando aplicacion principal...
    call python main.py
    goto post_run
)
if "%MODULE_CHOICE%"=="2" (
    echo.
    echo Lanzando modulo Poker...
    call python Poker\poker_main.py
    goto post_run
)
if "%MODULE_CHOICE%"=="3" (
    echo.
    echo Lanzando modulo Blackjack...
    call python Blackjack\blackjack.py
    goto post_run
)
if "%MODULE_CHOICE%"=="0" goto finish

if "%MODULE_CHOICE%"=="4" goto ask_run

echo Opcion no valida. Elige un numero entre 0 y 4.
echo.

goto module_menu

:post_run
echo.
echo El modulo seleccionado ha finalizado.
echo.
goto ask_run

:finish
echo.
pause
