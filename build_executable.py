import PyInstaller.__main__

# This runs PyInstaller from Python code rather than the command line.
# See https://pyinstaller.org/en/stable/usage.html#running-pyinstaller-from-python-code
# This is the same as running the following in the command line:
# pyinstaller --noconsole --noconfirm --icon "./resources/brachify_splash-ico.ico" --name "brachify" --splash ".\src\windows\splashscreen\brachify_splash.png" --hidden-import "pydicom.pixels.encoders.gdcm" --hidden-import "OCC" --hidden-import "pydicom.pixels.encoders.pylibjpeg" --paths=src "./src/launch.py" --exclude-module PyQt5

HIDDEN_IMPORTS = [
    'pydicom.pixels.encoders.gdcm',
    'OCC',
    'pydicom.pixels.encoders.pylibjpeg',
]


if __name__ == "__main__":
    hidden_import_args = [arg for module_name in HIDDEN_IMPORTS for arg in ('--hidden-import', module_name)]
    PyInstaller.__main__.run([
        '--noconsole',
        '--noconfirm',
        '--icon',
        './resources/brachify_splash-ico.ico',
        '--name',
        'brachify',
        '--splash',
        './src/windows/splashscreen/brachify_splash.png',
        *hidden_import_args,
        '--paths=src',
        './src/launch.py',
        '--exclude-module',
        'PyQt5',

    ])
