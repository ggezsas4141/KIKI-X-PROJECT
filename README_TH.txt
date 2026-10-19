KIKI X PROJECT V4 — Owner License Build

OWNER KEY (keep private):
KIKI-CGKN-JGWD-AKVV-KS8S

WHAT THIS PACKAGE DOES
- Keeps the existing Windows Tkinter dashboard and functions from KIKI_X_PROJECT_V4.py.
- Adds an Owner License Key login gate before opening the dashboard.
- Existing functions include CPU/RAM/GPU monitoring where supported, ping test, performance micro-benchmark, FiveM/FPS/GPU/RAM/network guidance, TEMP cleanup, registry setting backup/restore. Some buttons provide guidance rather than automatic optimization, as in the original source.

BUILD EXE WITH YOUR EXISTING GITHUB REPOSITORY
1. Download and extract this ZIP.
2. In your GitHub repository KIKI-X-PROJECT, replace the existing KIKI_X_PROJECT_V4.py with this package's file (open file > pencil Edit or Add file > Upload files).
3. Ensure requirements.txt is at the repository root.
4. Put .github/workflows/build-windows.yml in that exact path.
5. Commit changes, then open Actions and wait for green check.
6. Open the successful run, find Artifacts, download KIKI_X_PROJECT_V4-Owner-EXE, and extract the ZIP.
7. Run KIKI_X_PROJECT_V4.exe and enter the key above.

IMPORTANT SECURITY LIMITATION
This is a local owner-key gate, not server-side license authentication. The key is embedded in the program and a determined user can extract/bypass it. Do not distribute this build to others if the owner key must remain secret. Strong licensing requires a server endpoint and a hosted database.

SAFETY
- TEMP cleanup deletes files older than 24 hours and cannot restore deleted files.
- Registry change is limited to the VisualFXSetting value and the app saves the previous value for Restore.
- Optimization advice does not guarantee higher FPS.
