@echo off
setlocal enabledelayedexpansion

set BINARY_NAME=grassy
set RELEASE_DIR=release
set DIST_DIR=%RELEASE_DIR%\dist
set BUILD_DIR=%RELEASE_DIR%\build
set VENV=venv

:: Colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

:: Read version from version.txt
if not exist "version.txt" (
    echo %RED%❌ version.txt not found%RESET%
    exit /b 1
)
set /p BINARY_VERSION=<version.txt
echo %YELLOW%Building %BINARY_NAME% v%BINARY_VERSION% for Windows...%RESET%

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python not found. Install from python.org%RESET%
    exit /b 1
)

:: Check MSYS2
if not exist "C:\msys64\usr\bin\pacman.exe" (
    echo %RED%❌ MSYS2 not found. Install from https://www.msys2.org then re-run this script.%RESET%
    exit /b 1
)

:: Use UCRT64 instead of mingw64 for better compatibility
set GTK_BIN=C:\msys64\ucrt64\bin
set GTK_LIB=C:\msys64\ucrt64\lib
set GTK_SHARE=C:\msys64\ucrt64\share

:: Install GTK stack via pacman
echo %YELLOW%Installing GTK stack via MSYS2 pacman...%RESET%
C:\msys64\usr\bin\pacman.exe -S --needed --noconfirm ^
    mingw-w64-ucrt-x86_64-gtk4 ^
    mingw-w64-ucrt-x86_64-libadwaita ^
    mingw-w64-ucrt-x86_64-python-gobject ^
    mingw-w64-ucrt-x86_64-gdk-pixbuf2 ^
    mingw-w64-ucrt-x86_64-pango ^
    mingw-w64-ucrt-x86_64-cairo ^
    mingw-w64-ucrt-x86_64-harfbuzz ^
    mingw-w64-ucrt-x86_64-fontconfig ^
    mingw-w64-ucrt-x86_64-freetype ^
    mingw-w64-ucrt-x86_64-graphene ^
    mingw-w64-ucrt-x86_64-libxml2 ^
    mingw-w64-ucrt-x86_64-sqlite3 ^
    mingw-w64-ucrt-x86_64-libepoxy

if errorlevel 1 (
    echo %RED%❌ pacman failed. Try running MSYS2 manually and running:%RESET%
    echo %YELLOW%   pacman -Syu%RESET%
    echo %YELLOW%   then re-run this script.%RESET%
    exit /b 1
)

echo %GREEN%✅ GTK stack installed%RESET%

:: Verify GTK is present
if not exist "%GTK_BIN%\libgtk-4-1.dll" (
    echo %RED%❌ GTK4 DLL not found. Something went wrong.%RESET%
    exit /b 1
)

:: Setup venv
if not exist "%VENV%\Scripts\python.exe" (
    echo %YELLOW%Creating virtual environment...%RESET%
    python -m venv %VENV%
)

call %VENV%\Scripts\activate.bat

echo %YELLOW%Installing dependencies...%RESET%
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: Clean old release
if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
mkdir %RELEASE_DIR%

echo %YELLOW%Running PyInstaller...%RESET%
python -m PyInstaller ^
    --name %BINARY_NAME% ^
    --onedir ^
    --windowed ^
    --distpath %DIST_DIR% ^
    --workpath %BUILD_DIR% ^
    --specpath %RELEASE_DIR% ^
    --hidden-import=gi ^
    --hidden-import=gi.repository.Gtk ^
    --hidden-import=gi.repository.Adw ^
    src/main.py

if errorlevel 1 (
    echo %RED%❌ PyInstaller failed%RESET%
    exit /b 1
)

echo %YELLOW%Copying GTK runtime DLLs...%RESET%
set OUT=%DIST_DIR%\%BINARY_NAME%

:: Core DLLs
for %%f in (
    libgtk-4-1.dll
    libadwaita-1-0.dll
    libglib-2.0-0.dll
    libgobject-2.0-0.dll
    libgio-2.0-0.dll
    libgdk_pixbuf-2.0-0.dll
    libpango-1.0-0.dll
    libpangocairo-1.0-0.dll
    libcairo-2.dll
    libcairo-gobject-2.dll
    libharfbuzz-0.dll
    libfontconfig-1.dll
    libfreetype-6.dll
    libepoxy-0.dll
    libffi-8.dll
    libintl-8.dll
    libpcre2-8-0.dll
    libpixman-1-0.dll
    libpng16-16.dll
    zlib1.dll
    libwinpthread-1.dll
    libgcc_s_seh-1.dll
    libstdc++-6.dll
    libgraphene-1.0-0.dll
    libjpeg-8.dll
    libtiff-6.dll
    libbrotlicommon.dll
    libbz2-1.dll
    libxml2-2.dll
    liblzma-5.dll
    libzstd.dll
) do (
    if exist "%GTK_BIN%\%%f" (
        copy /y "%GTK_BIN%\%%f" "%OUT%\" >nul
    ) else (
        echo %YELLOW%  ⚠ Warning: %%f not found, skipping%RESET%
    )
)

:: GLib schemas (required for Adwaita)
echo %YELLOW%Copying GLib schemas...%RESET%
mkdir "%OUT%\share\glib-2.0\schemas" 2>nul
xcopy /s /q "%GTK_SHARE%\glib-2.0\schemas\*" "%OUT%\share\glib-2.0\schemas\" >nul
"%GTK_BIN%\glib-compile-schemas.exe" "%OUT%\share\glib-2.0\schemas"

:: Icons and themes
echo %YELLOW%Copying icons and themes...%RESET%
mkdir "%OUT%\share\icons" 2>nul
xcopy /s /q "%GTK_SHARE%\icons\hicolor" "%OUT%\share\icons\hicolor\" >nul
xcopy /s /q "%GTK_SHARE%\icons\Adwaita" "%OUT%\share\icons\Adwaita\" >nul 2>&1

mkdir "%OUT%\share\themes" 2>nul
if exist "%GTK_SHARE%\themes\Adwaita" (
    xcopy /s /q "%GTK_SHARE%\themes\Adwaita" "%OUT%\share\themes\Adwaita\" >nul
)

:: GTK settings
mkdir "%OUT%\etc\gtk-4.0" 2>nul
(
    echo [Settings]
    echo gtk-theme-name=Adwaita
    echo gtk-font-name=Segoe UI 9
) > "%OUT%\etc\gtk-4.0\settings.ini"

:: GI typelibs (needed by PyGObject)
echo %YELLOW%Copying typelibs...%RESET%
mkdir "%OUT%\lib\girepository-1.0" 2>nul
for %%f in (
    Gtk-4.0.typelib
    Adw-1.typelib
    GLib-2.0.typelib
    GObject-2.0.typelib
    Gio-2.0.typelib
    Gdk-4.0.typelib
    GdkWin32-4.0.typelib
    Pango-1.0.typelib
    PangoCairo-1.0.typelib
    cairo-1.0.typelib
    GdkPixbuf-2.0.typelib
    Graphene-1.0.typelib
    HarfBuzz-0.0.typelib
) do (
    if exist "%GTK_LIB%\girepository-1.0\%%f" (
        copy /y "%GTK_LIB%\girepository-1.0\%%f" "%OUT%\lib\girepository-1.0\" >nul
    ) else (
        echo %YELLOW%  ⚠ Warning: %%f not found, skipping%RESET%
    )
)

:: GTK4 modules (renderers etc)
echo %YELLOW%Copying GTK4 modules...%RESET%
mkdir "%OUT%\lib\gtk-4.0" 2>nul
if exist "%GTK_LIB%\gtk-4.0" (
    xcopy /s /q "%GTK_LIB%\gtk-4.0\*" "%OUT%\lib\gtk-4.0\" >nul
)

:: GDK pixbuf loaders
echo %YELLOW%Copying pixbuf loaders...%RESET%
mkdir "%OUT%\lib\gdk-pixbuf-2.0" 2>nul
if exist "%GTK_LIB%\gdk-pixbuf-2.0" (
    xcopy /s /q "%GTK_LIB%\gdk-pixbuf-2.0\*" "%OUT%\lib\gdk-pixbuf-2.0\" >nul
)

:: Pango modules
echo %YELLOW%Copying Pango modules...%RESET%
if exist "%GTK_LIB%\pango" (
    mkdir "%OUT%\lib\pango" 2>nul
    xcopy /s /q "%GTK_LIB%\pango\*" "%OUT%\lib\pango\" >nul
)

:: Fonts
echo %YELLOW%Copying fonts...%RESET%
mkdir "%OUT%\share\fonts" 2>nul
if exist "%GTK_SHARE%\fonts" (
    xcopy /s /q "%GTK_SHARE%\fonts\*" "%OUT%\share\fonts\" >nul
)

:: Copy assets if present
if exist "assets" (
    echo %YELLOW%Copying assets...%RESET%
    xcopy /s /q "assets\*" "%OUT%\assets\" >nul
)

:: Create launcher
echo %YELLOW%Creating launcher...%RESET%
(
    echo @echo off
    echo set "SCRIPT_DIR=%%~dp0"
    echo set "GI_TYPELIB_PATH=%%SCRIPT_DIR%%lib\girepository-1.0"
    echo set "GTK_DATA_PREFIX=%%SCRIPT_DIR%%"
    echo set "GDK_PIXBUF_MODULE_FILE=%%SCRIPT_DIR%%lib\gdk-pixbuf-2.0\2.10.0\loaders.cache"
    echo set "XDG_DATA_DIRS=%%SCRIPT_DIR%%share"
    echo set "PATH=%%SCRIPT_DIR%%;%%PATH%%"
    echo start "" "%%SCRIPT_DIR%%%BINARY_NAME%.exe" %%*
) > "%OUT%\launch.bat"

:: Zip it up
echo %YELLOW%Creating zip...%RESET%
set ZIP_NAME=%BINARY_NAME%-%BINARY_VERSION%-windows-x64.zip

where powershell >nul 2>&1
if not errorlevel 1 (
    powershell -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%RELEASE_DIR%\%ZIP_NAME%' -Force"
    echo %GREEN%✅ Done! Output: %RELEASE_DIR%\%ZIP_NAME%%RESET%
) else (
    echo %YELLOW%⚠ PowerShell not found, skipping zip. Package manually from %OUT%%RESET%
)

echo %GREEN%✅ Build complete!%RESET%
echo %YELLOW%   Users should run launch.bat, not the .exe directly%RESET%
echo %YELLOW%   Output location: %OUT%%RESET%

call %VENV%\Scripts\deactivate.bat
endlocal
