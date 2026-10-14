# AI-Powered Touchless Virtual Drawing System

A real-time computer vision project that lets you draw on a virtual canvas using hand gestures and a webcam.

## Features
- Real-time hand landmark tracking with MediaPipe
- Touchless drawing with the index finger
- Hand-gesture cursor and colour selection
- Fist gesture eraser
- Smoothed fingertip tracking
- OpenCV interactive window

## Recommended setup
Use **Python 3.11 (64-bit)** on Windows for the easiest MediaPipe installation. Python 3.12 may work depending on available package wheels.

## Run in VS Code (Windows PowerShell)

1. Extract the ZIP file.
2. Open the extracted `AI_Touchless_Virtual_Drawing_System` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Check Python:
   ```powershell
   py -3.11 --version
   ```
5. Create a virtual environment:
   ```powershell
   py -3.11 -m venv venv
   ```
6. Activate it:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this in the same terminal and activate again:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```
7. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
8. Start the app:
   ```powershell
   python app.py
   ```

Allow webcam access if Windows asks.

## Gestures
- **Index finger only:** draw
- **Index + middle fingers:** pause drawing and move the cursor; point at the colour strip at the top to choose a colour
- **Closed fist:** erase
- **C key:** clear canvas
- **Q or Esc:** quit

## Troubleshooting
- **Webcam unavailable:** close other apps using the camera, check Windows Camera privacy settings, and try again.
- **MediaPipe install error:** install Python 3.11 64-bit, recreate `venv`, then reinstall requirements.
- **No hand detected:** improve lighting and keep your hand fully in view.
- This is an educational starter project; gesture detection may need tuning for different cameras and lighting.
