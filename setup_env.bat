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
call .venv\Scripts\activate

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
echo      ejecutando: .venv\Scripts\activate
echo.
pause