@echo off
rem ===========================================================================
rem Starts Comment Moderator in Docker: Ollama, the models and the web app.
rem ===========================================================================
cd /d "%~dp0"
docker compose -f .tools\docker\docker-compose.yml up --build -d
if errorlevel 1 exit /b 1
echo Waiting for http://localhost:7860 ...
:wait
curl -sf http://localhost:7860/ >nul 2>&1 || (timeout /t 3 >nul & goto wait)
echo Comment Moderator is ready: http://localhost:7860
echo CLI in the container: docker compose -f .tools\docker\docker-compose.yml exec app moderator --help
