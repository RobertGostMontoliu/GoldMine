# When env is activated, build using: python setup.py build_ext --inplace
from Cython.Build import cythonize
import os
from pathlib import Path
import re
from setuptools import Extension, setup

# START CONFIG
PROJECT_MODULE = "ui"
# END CONFIG

SRC_DIR = Path(__file__).resolve().parent
MODULE_DIR = SRC_DIR / PROJECT_MODULE
os.chdir(SRC_DIR)

try:
    extensions = []
    modules = set()
    
    # Convert all .py files to .pyx and update __init__.py
    with open(MODULE_DIR / "__init__.py", "w", encoding="utf-8") as init_f:
        modules.add(f"{PROJECT_MODULE}.entrypoint")
        init_f.write(f"import {PROJECT_MODULE}.entrypoint\n")
        
        for root, dirs, files in os.walk(MODULE_DIR):
            root_path = Path(root)
        
            for file in files:
                if not file.endswith(".py") or file == "__init__.py":
                    continue
            
                file_path = root_path / file
            
                # Copy all imports into __init__.py
                # Assumes black formatting
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                
                    # Continue if not an import line
                    if not line.startswith("import ") and not line.startswith("from "):
                        continue
                
                    # Strip comments
                    # Comments can only be trailing on import statements
                    line = line.split("#")[0].strip()
                
                    # Handle 'import ...'
                    if line.startswith("import "):
                        import_statement = line
                        module_name = line.split("import")[1].strip().split(" as ")[0].strip()
                    
                    # Handle 'from ... import ...'
                    elif line.startswith("from ") and " import " in line and " as " not in line:
                        import_statement = line
                        module_name = line.split("from")[1].strip().split(" import ")[0].strip()
                    
                    # Handle 'from ... import ... as ...'
                    elif line.startswith("from ") and " import " in line and " as " in line:
                        import_statement = line
                        module_name = line.split("from")[1].strip().split(" import ")[0].strip()
                    
                    else:
                        continue
                    
                    # Add import statement to __init__.py if not already added
                    if import_statement not in modules:
                        init_f.write(f"{import_statement}\n")
                        modules.add(import_statement)
                            
                # Rename file
                new_file_path = file_path.parent / f"{file_path.stem}.pyx"
                
                file_path.rename(new_file_path)
                file_path = new_file_path
                
                base_name = re.sub(
                    f"^{f'{SRC_DIR.as_posix()}/'}",
                    "",
                    (root_path / file_path.stem).as_posix(),
                )
                
                name = base_name.replace("/", ".")
                source = [f"{base_name}.pyx"]
                
                extensions.append(Extension(name, source))
                
    # Compile python files
    setup(
        ext_modules=cythonize(
            extensions,
            annotate=False,
            compiler_directives={"language_level": "3"},
        ),
    )
    
finally:
    # Convert all .pyx files back to .py
    for root, dirs, files in os.walk(MODULE_DIR):
        root_path = Path(root)
        
        for file in [file for file in files if file.endswith(".pyx")]:
            file_path = root_path / file
            new_file_path = file_path.parent / f"{file_path.stem}.py"
            
            file_path.rename(new_file_path)