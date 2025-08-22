@echo off
REM Install deps
pip install -r requirements.txt
pip install pyinstaller

REM Build single-file GUI exe
pyinstaller --noconfirm --onefile --windowed --name PDF2JSON_OCR app.py

echo.
echo Done! Check the "dist" folder for PDF2JSON_OCR.exe
pause
