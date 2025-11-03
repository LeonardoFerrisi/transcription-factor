@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python transcription_factor.py %* 