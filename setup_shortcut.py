import os
import subprocess
from PIL import Image

def setup():
    # 1. Paths
    root_dir = r"c:\Users\juanc\Desktop\prueba"
    ico_path = os.path.join(root_dir, "binarias_simulator_icon.ico")
    bat_path = os.path.join(root_dir, "run_binarias_simulator.bat")
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop, "Binarias Simulator.lnk")
    old_shortcut = os.path.join(desktop, "BinSim.lnk")

    # Clean up old shortcut if exists
    if os.path.exists(old_shortcut):
        try:
            os.remove(old_shortcut)
            print("Cleaned up old 'BinSim.lnk' shortcut.")
        except Exception:
            pass

    if os.path.exists(shortcut_path):
        try:
            os.remove(shortcut_path)
        except Exception:
            pass

    print("Creating startup batch file...")
    bat_content = f"""@echo off
title Binarias Simulator - Trading Simulator
cd /d "{root_dir}"
echo Starting Binarias Simulator Backend...
start cmd /c "python app.py"
echo Waiting for server to start...
timeout /t 3 /nobreak > nul
echo Opening interface in browser...
start "" "http://127.0.0.1:5001"
exit
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"  [OK] Created batch script at {bat_path}")

    print("Creating Windows Desktop Shortcut via PowerShell...")
    ps_script = """
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{bat_path}"
$Shortcut.WorkingDirectory = "{root_dir}"
$Shortcut.IconLocation = "{ico_path}"
$Shortcut.Save()
""".format(shortcut_path=shortcut_path, bat_path=bat_path, root_dir=root_dir, ico_path=ico_path)
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True)
        print(f"  [OK] Created Desktop Shortcut at {shortcut_path}")
        # Notify shell of icon changes
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    except Exception as e:
        print(f"  [ERROR] Failed to create shortcut: {e}")

    # Clean up old local files
    for old_file in ["run_binsim.bat", "binsim_icon.ico"]:
        fp = os.path.join(root_dir, old_file)
        if os.path.exists(fp):
            try:
                os.remove(fp)
                print(f"Cleaned up old local file: {old_file}")
            except Exception:
                pass

if __name__ == "__main__":
    setup()
