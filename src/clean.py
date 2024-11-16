import os
from pathlib import Path

# START CONFIG
PROJECT_MODULE = "ui"
# END CONFIG

SRC_DIR = Path(__file__).resolve().parent
MODULE_DIR = SRC_DIR / PROJECT_MODULE
os.chdir(SRC_DIR)

for root, dirs, files in os.walk(MODULE_DIR):
    root_path = Path(root)
    
    for file in files:
        if not file.endswith(".c") and not file.endswith(".pyd") and not file.endswith(".so"):
            continue
            
        file_path = root_path / file
        file_path.unlink(file_path)