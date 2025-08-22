[Setup]
AppName=PDF to JSON OCR
AppVersion=1.0.0
DefaultDirName={pf64}\PDF2JSON_OCR
DefaultGroupName=PDF2JSON_OCR
OutputBaseFilename=PDF2JSON_OCR_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source="dist\PDF2JSON_OCR.exe"; DestDir="{app}"; Flags: ignoreversion
; If bundling Poppler with the installer, uncomment and adjust:
; Source="poppler-24.08.0\bin\*"; DestDir="{app}\poppler_bin"; Flags: recursesubdirs ignoreversion

[Icons]
Name="{group}\PDF to JSON OCR"; Filename="{app}\PDF2JSON_OCR.exe"
Name="{commondesktop}\PDF to JSON OCR"; Filename="{app}\PDF2JSON_OCR.exe"
