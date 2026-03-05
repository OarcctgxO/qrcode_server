@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Устанавливаем путь к виртуальному окружению
set VENV_DIR=.venv

:: Проверяем, существует ли папка виртуального окружения
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение не найдено в папке %VENV_DIR%
    echo Пожалуйста, создайте его командой: python -m venv .venv
    pause
    exit /b 1
)

:: Активируем виртуальное окружение
echo Активация виртуального окружения...
call "%VENV_DIR%\Scripts\activate.bat"

:: Проверяем, установлен ли PyInstaller в окружении
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ВНИМАНИЕ] PyInstaller не найден в текущем окружении. Устанавливаем...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить PyInstaller.
        pause
        exit /b 1
    )
)

:: Запускаем PyInstaller
echo Запуск PyInstaller...
python -m PyInstaller --onefile main.py

:: Деактивируем окружение (опционально)
call deactivate

echo.
echo Сборка завершена. Исполняемый файл находится в папке dist.
pause