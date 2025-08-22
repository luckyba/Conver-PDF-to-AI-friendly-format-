REQUIREMENTS (EXTERNAL):
- Tesseract OCR (with language data, e.g., eng.traineddata or vie.traineddata in tessdata).
  Example path: C:\Program Files\Tesseract-OCR\tesseract.exe
- Poppler for Windows (the "bin" folder must contain pdfinfo.exe and pdftoppm.exe).

INSTALL PYTHON DEPENDENCIES:
- pip install -r requirements.txt

Install PYINstaller
- python -m pip install --upgrade pip setuptools wheel
- python -m pip install pyinstaller

RUN APP (from source):
- python app.py

BUILD EXE:
- run build_exe.bat OR
  pyinstaller --noconfirm --onefile --windowed --name PDF2JSON_OCR app.py
- the .exe will be in the "dist" folder

USAGE:
- Open the app -> choose PDF -> choose output JSON path
- (Optional) set explicit paths to tesseract.exe and Poppler\bin if not in PATH
- Language: 'eng', 'vie', or 'eng+vie'
- Recommended DPI: 300

COMMON ERRORS:
- "Unable to get page count. Is poppler installed and in PATH?"
  -> Poppler not found. Provide Poppler\bin via the UI or add it to PATH.
- "TesseractNotFoundError"
  -> Tesseract not installed or wrong tesseract.exe path.

