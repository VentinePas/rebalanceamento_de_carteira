@echo off
setlocal
cd /d "%~dp0"

echo =====================================================
echo   Rebalanceamento de Carteira - Gerar instalador
echo =====================================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado neste computador.
    echo Instale o Python 3 para gerar o instalador. O usuario final NAO precisara dele.
    echo Download: https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

if not exist ".build_venv\Scripts\python.exe" (
    echo Criando ambiente de compilacao...
    py -3 -m venv .build_venv
    if errorlevel 1 goto erro
)

set "PYTHON=.build_venv\Scripts\python.exe"
echo Instalando/atualizando PyInstaller...
"%PYTHON%" -m pip install --upgrade pip pyinstaller
if errorlevel 1 goto erro

echo.
echo Gerando o executavel do programa...
"%PYTHON%" -m PyInstaller --clean --noconfirm --onefile --windowed --name RebalanceamentoCarteira rebalanceamento_carteira_gui.py
if errorlevel 1 goto erro

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"

if not defined ISCC goto sem_inno

if not exist "installer" mkdir "installer"
echo.
echo Gerando o instalador para distribuir...
"%ISCC%" "instalador_rebalanceamento.iss"
if errorlevel 1 goto erro

echo.
echo SUCESSO! O arquivo para enviar por email esta em:
echo %CD%\installer\Instalador_Rebalanceamento_Carteira.exe
echo.
echo A pessoa que receber esse arquivo nao precisa de Python nem de CMD.
echo.
pause
exit /b 0

:sem_inno
echo.
echo O executavel foi criado na pasta dist, mas o Inno Setup nao foi encontrado.
echo Instale o Inno Setup e execute este arquivo .bat novamente:
echo https://jrsoftware.org/isdl.php
 echo.
pause
exit /b 2

:erro
echo.
echo Ocorreu um erro ao gerar os arquivos. Leia as mensagens acima.
echo.
pause
exit /b 1
