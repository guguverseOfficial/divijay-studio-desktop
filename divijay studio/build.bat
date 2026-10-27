@echo off
pyinstaller --onefile --windowed --name="DivijayStudio" --icon="assets/icons/icon.ico" --add-data "ffmpeg.exe;." DivijayStudio.py
pause