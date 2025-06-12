@echo off
setlocal

:: Step 1: Download Camoufox zip
echo Downloading Camoufox...
curl -L -o camoufox.zip https://github.com/daijro/camoufox/releases/download/v135.0.1-beta.24/camoufox-135.0.1-beta.24-win.x86_64.zip

:: Step 2: Extract camoufox.zip
echo Extracting Camoufox...
powershell -command "Expand-Archive -Force camoufox.zip -DestinationPath camoufox_temp"

:: Step 3: Install Camoufox from extracted folder
echo Installing Camoufox...
pip install camoufox_temp\camoufox-135.0.1-beta.24-py3-none-any.whl

:: Step 4: Install requirements.txt dependencies
echo Installing other requirements...
pip install -r requirements.txt

:: Step 5: Cleanup
del camoufox.zip
rmdir /S /Q camoufox_temp

:: Step 6: Run main.py
echo Running main.py...
python main.py

endlocal
pause
