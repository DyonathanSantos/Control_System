import os
import shutil

def safe_move(src, dest):
    """Move file or folder safely, skipping if it already exists."""
    if not os.path.exists(src):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest):
        shutil.move(src, dest)
        print(f"✅ Moved: {src} → {dest}")
    else:
        print(f"⚠️ Skipped (already exists): {dest}")

# Get current base dir (where this script is)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Paths
old_root = os.path.join(base_dir, "System-for-commerce", "APP")
new_app_dir = os.path.join(base_dir, "app")
data_dir = os.path.join(base_dir, "data")

# Make new structure
os.makedirs(new_app_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# Move Python files to /app
for filename in ["crud.py", "create_db.py", "GUI.py", "main.py", "teste.py"]:
    src = os.path.join(old_root, filename)
    dest = os.path.join(new_app_dir, filename.lower())  # lowercase file names
    safe_move(src, dest)

# Move DB file to /data
safe_move(os.path.join(old_root, "base.db"), os.path.join(data_dir, "base.db"))

# Move requirements.txt (if exists)
safe_move(os.path.join(base_dir, "Teste", "requirements.txt"),
          os.path.join(base_dir, "requirements.txt"))

# Fix .gitignore name
ignore_old = os.path.join(old_root, "Ignore.gitignore")
ignore_new = os.path.join(base_dir, ".gitignore")
safe_move(ignore_old, ignore_new)

print("\n✅ Project structure reorganized successfully!")
print("Remember to check your imports (e.g., from app.crud import ...) after moving files.")
