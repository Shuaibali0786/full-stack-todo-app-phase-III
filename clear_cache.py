import os
import shutil

# Delete all __pycache__ directories
for root, dirs, files in os.walk("backend"):
    if "__pycache__" in dirs:
        cache_dir = os.path.join(root, "__pycache__")
        print(f"Deleting: {cache_dir}")
        shutil.rmtree(cache_dir, ignore_errors=True)

    # Delete .pyc files
    for file in files:
        if file.endswith(".pyc"):
            pyc_file = os.path.join(root, file)
            print(f"Deleting: {pyc_file}")
            os.remove(pyc_file)

print("\n✓ Python cache cleared!")
