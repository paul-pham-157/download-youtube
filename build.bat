@echo off

REM Install requirements
pip install -r requirements.txt

REM Build the executable
pyinstaller --name=YouTubePlaylistDownloader --windowed --onefile app.py

echo Build completed. The executable is in the 'dist' folder.