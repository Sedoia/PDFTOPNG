import PyInstaller.__main__
import os
import sys
import shutil
import subprocess
import datetime

# --- CONFIGURATION ---
SCRIPT_NAME = "sedo_converter_v2.py"  # Name of your script
APP_NAME = "SedoConverter_GodMode"    # Name of the final exe
ICON_FILE = "icon.ico"                # Optional: if you have an .ico file, set path here, else None
AUTHOR_NAME = "Sedo"                  # Used for License

# --- UTILS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_dir():
    return os.path.dirname(os.path.abspath(__file__))

def pause():
    """Pauses execution to allow user to read messages."""
    input("\nPress Enter to return to menu...")

# --- MODULE 1: EXE BUILDER ---
def check_requirements():
    print("\n--- CHECKING REQUIREMENTS ---")
    missing = []
    try: import tkinterdnd2
    except ImportError: missing.append("tkinterdnd2")
    try: import pymupdf
    except ImportError: missing.append("pymupdf")
    try: import PIL
    except ImportError: missing.append("pillow")

    if missing:
        print(f"❌ ERROR: Missing libraries: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        return False
    print("✅ All libraries found.")
    return True

def build_exe():
    current_dir = get_current_dir()
    os.chdir(current_dir)
    print(f"📂 Working in: {current_dir}")

    if not check_requirements(): 
        pause()
        return

    if not os.path.exists(SCRIPT_NAME):
        print(f"❌ ERROR: Could not find {SCRIPT_NAME}.")
        print(f"   Make sure {SCRIPT_NAME} is in: {current_dir}")
        pause()
        return

    print(f"--- STARTING BUILD FOR {APP_NAME} ---")
    
    args = [
        SCRIPT_NAME,
        f'--name={APP_NAME}',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--collect-all=tkinterdnd2',
        '--hidden-import=pymupdf',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
    ]
    if ICON_FILE and os.path.exists(ICON_FILE):
        args.append(f'--icon={ICON_FILE}')

    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*40)
        print("✅ BUILD SUCCESSFUL!")
        print(f"   Location: {os.path.join(current_dir, 'dist', APP_NAME + '.exe')}")
        print("="*40)
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
    
    pause()

# --- MODULE 2: DOCS GENERATOR (THE PROFESSIONAL STUFF) ---
def generate_docs():
    """Generates README, LICENSE, etc. with a casual tone if they don't exist."""
    print("\n📝 Checking documentation...")

    # 1. README.md
    if not os.path.exists("README.md"):
        print("   + Generating README.md (Casual Style)...")
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"""# 🚀 {APP_NAME.replace('_', ' ')}

> *Because honestly, who has time to pay for simple PDF tools?*

## What is this?
Hey! 👋 This is a tool I built to handle PDF conversions without the headache. It’s got a "God Mode" interface (dark theme, obviously) and handles the stuff that usually annoys me about other converters.

**Key Features:**
* **Drag & Drop:** Just toss your files in.
* **Night Mode:** Inverts colors for late-night reading.
* **Stitch Mode:** Takes a multi-page PDF and glues it into one *loooooong* image.
* **Smart Crop:** Auto-trims those annoying white borders.
* **Page Ranges:** Convert pages 1-5, or just page 42. You're the boss.

## How to Run It
### Option 1: The Easy Way (EXE)
If you don't care about code and just want it to work:
1.  Go to the [Releases/Dist folder](./dist).
2.  Download `{APP_NAME}.exe`.
3.  Run it. Done.

### Option 2: The Dev Way (Python)
If you want to tinker with the code:
```bash
# Clone the repo
git clone [https://github.com/YourUsername/RepoName.git](https://github.com/YourUsername/RepoName.git)

# Install requirements
pip install -r requirements.txt

# Run it
python {SCRIPT_NAME}
```

## Contributing
Found a bug? Have a cool idea?
Feel free to open an issue or submit a Pull Request. I promise I don't bite.

## License
MIT License. Do whatever you want with it, just don't sue me if your computer explodes (it won't).
""")

    # 2. REQUIREMENTS.TXT
    if not os.path.exists("requirements.txt"):
        print("   + Generating requirements.txt...")
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write("tkinterdnd2\npymupdf\nPillow\npyinstaller\n")

    # 3. LICENSE
    if not os.path.exists("LICENSE"):
        print("   + Generating MIT LICENSE...")
        year = datetime.datetime.now().year
        with open("LICENSE", "w", encoding="utf-8") as f:
            f.write(f"""MIT License

Copyright (c) {year} {AUTHOR_NAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
            
    # 4. CONTRIBUTING.md
    if not os.path.exists("CONTRIBUTING.md"):
        print("   + Generating CONTRIBUTING.md...")
        # CRITICAL FIX: Added encoding="utf-8" to handle emojis
        with open("CONTRIBUTING.md", "w", encoding="utf-8") as f:
            f.write("""# Contributing

Yo! Thanks for checking out the code.

If you want to add features or fix bugs, here is the flow:
1.  **Fork** this repo.
2.  **Clone** it to your machine.
3.  **Hack away**.
4.  **Test** your changes (make sure the EXE build still works!).
5.  Submit a **Pull Request**.

Keep the code clean, keep the vibes good. Happy coding! 💻
""")

# --- MODULE 3: GITHUB AUTOMATION ---
def create_gitignore():
    if not os.path.exists(".gitignore"):
        print("📝 Creating .gitignore...")
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write("\n# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Build\nbuild/\n*.spec\n\n# IDE\n.vscode/\nvenv/\n")

def run_git(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def git_automate():
    current_dir = get_current_dir()
    os.chdir(current_dir)
    print(f"📂 Git Operations in: {current_dir}\n")

    # 1. Generate Pro Docs (Always do this first!)
    generate_docs()
    create_gitignore()

    # 2. Check for Git
    print("\n🔍 Checking for Git...")
    if not run_git("git --version"):
        print("\n❌ ERROR: Git is not installed (or not in your PATH).")
        print("   I've created your README and LICENSE, but I can't upload to GitHub")
        print("   until you install Git.")
        print("\n   👉 Download here: https://git-scm.com/downloads")
        print("   (After installing, close and reopen this terminal!)")
        pause()
        return

    # 3. Init
    if not os.path.exists(os.path.join(current_dir, ".git")):
        print("✨ Initializing Git...")
        run_git("git init")
        run_git("git branch -M main")

    # 4. Remote Check
    res = subprocess.run("git remote get-url origin", shell=True, capture_output=True)
    if res.returncode != 0:
        print("\n⚠️  Link your GitHub Repo!")
        print("   (Create a new empty repo at https://github.com/new)")
        url = input("   🔗 Paste URL here: ").strip()
        if url: 
            run_git(f"git remote add origin {url}")
        else:
            print("   Skipping remote link (Local only mode).")

    # 5. Identity Check (Fixes "Author identity unknown" error)
    print("\n👤 Checking Git Identity...")
    # Check if email is configured locally or globally
    res_email = subprocess.run("git config user.email", shell=True, capture_output=True, text=True).stdout.strip()
    
    if not res_email:
        print("   Git doesn't know who you are yet (required for committing).")
        name = input("   Enter your Name (e.g., Sedo): ").strip()
        email = input("   Enter your Email: ").strip()
        
        if name and email:
            # Setting it locally for this repo is safer/easier for the user
            run_git(f'git config user.name "{name}"')
            run_git(f'git config user.email "{email}"')
        else:
            print("❌ Error: Name and Email are required by Git. Aborting.")
            pause()
            return

    # 6. Add Files
    print("\n📦 Staging files...")
    run_git("git add .")

    # 7. Ask about EXE
    exe_path = os.path.join("dist", f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        print(f"\n❓ Found App: {exe_path}")
        print("   (Normally we don't upload EXEs to git history, but for small projects it's fine)")
        if input("   Upload the .exe file too? (y/n): ").lower() == 'y':
            run_git(f'git add -f "{exe_path}"')

    # 8. Commit & Push
    msg = f"Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"📝 Committing: '{msg}'...")
    run_git(f'git commit -m "{msg}"')

    print("\n🚀 Pushing to GitHub...")
    if run_git("git push -u origin main"):
        print("\n✅ DONE! Your project is live and looks professional.")
    else:
        print("\n❌ Push failed. (Check login/internet)")
        print("   If you haven't linked a repo, this is expected.")
    
    pause()

# --- MAIN MENU ---
def main():
    while True:
        try:
            clear_screen()
            print("=========================================")
            print("   SEDO'S DEV TOOL - GOD MODE")
            print("=========================================")
            print("1. 🔨 Build EXE (Create App)")
            print("2. ☁️  Generate Docs & Push to GitHub")
            print("3. ❌ Exit")
            print("=========================================")
            
            choice = input("Select (1-3): ")
            if choice == "1": build_exe()
            elif choice == "2": git_automate()
            elif choice == "3": sys.exit()
            else:
                print("Invalid choice.")
                # Small pause to see invalid choice message
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            pause()

if __name__ == "__main__":
    main()
    