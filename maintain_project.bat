@echo off
REM Maintenance Scripts for Markdown to PDF Converter
REM This batch file provides utilities for managing the project

echo Markdown to PDF Converter - Maintenance Tools
echo --------------------------------------------

:menu
echo.
echo 1. Fix Mermaid JS (download compatible version)
echo 2. Flatten project structure
echo 3. Run application
echo 4. Exit
echo.
set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto fix_mermaid
if "%choice%"=="2" goto flatten_project
if "%choice%"=="3" goto run_app
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
goto menu

:fix_mermaid
echo.
echo Fixing Mermaid JS...
python mermaid_fix.py
echo.
pause
goto menu

:flatten_project
echo.
echo Flattening project structure...
set /p source=Enter source directory (or press Enter for current directory): 
set /p target=Enter target directory (or press Enter for "./flattened"): 
set /p clear=Clear target directory first? (y/n): 

if "%source%"=="" set source=.
if "%target%"=="" set target=./flattened

if /i "%clear%"=="y" (
    python flatten_project.py "%source%" "%target%" --clear
) else (
    python flatten_project.py "%source%" "%target%"
)

echo.
pause
goto menu

:run_app
echo.
echo Running Markdown to PDF Converter...
python main.py
echo.
pause
goto menu

:end
echo.
echo Exiting...
exit /b