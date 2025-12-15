"""Launcher for worms_rumble.py that ensures pygame is installed and logs import errors.

Usage:
    python run_worms.py

If pygame is missing, this script writes the traceback to assets/logs/error.txt and
prints platform-specific install instructions.
"""
import os
import sys
import traceback

log_dir = os.path.join('assets', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'error.txt')

try:
    import pygame  # noqa: F401
except Exception:
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('Failed to import pygame. Traceback:\n')
        traceback.print_exc(file=f)

    print('ERROR: Pygame is not installed or failed to import.')
    print(f'A traceback was written to {log_path}')
    print('\nInstall pygame for the Python you are using:')
    print('1) Ensure you are using the same python executable:')
    print('   python -c "import sys; print(sys.executable, sys.version)"')
    print('2) Install pygame using pip:')
    print('   python -m pip install --upgrade pip')
    print('   python -m pip install pygame')
    print('\nOr create and use a venv:')
    print('   python -m venv .venv')
    print('   .\\.venv\\Scripts\\Activate.ps1  # PowerShell')
    print('   python -m pip install -r requirements.txt')
    sys.exit(1)

# If pygame import succeeded, just run the game script using the same interpreter
print('Pygame is available — launching worms_rumble.py')
import subprocess
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'worms_rumble.py')])
