import os
import sys
import subprocess

python_path = sys.executable
scripts_path = os.path.join(os.path.dirname(python_path), "Scripts")

# Add to environment variable
subprocess.run(f'setx PATH "%PATH%;{scripts_path}" /M', shell=True)

print(f"Added {scripts_path} to system PATH. Restart your computer for changes to take effect.")
