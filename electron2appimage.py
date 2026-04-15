import sys, os, shutil, subprocess
from pathlib import Path

def confirm():
    confirmees=input("Hey! Electron2AppImage only works on Linux and for Linux Electron apps and it will move and rename your Electron folder! Are you sure you want to continue? (Y/n) ")
    if (((confirmees != "Y") or (confirmees != "y")) and ((confirmees != "N") or (confirmees != "N"))):confirm()

#confirm()

print("Preparing...")

try:
    ename = sys.argv[1]
    aname = sys.argv[2]
    iname = sys.argv[3]
    categories = sys.argv[4]
except Exception:
    print("Usage: electron2appimage [electron app name] [app name] [icon path (with extension)] [categories in .desktop format]")
    sys.exit(0)
subprocess.run(["rm",f"\"{aname}.AppDir\"","-r","-f"])
atool = "/usr/bin/"

if not categories.endswith(";"):
    categories += ";"

print("Making usr/bin folder in AppDir...")

os.makedirs(f"{aname}.AppDir")

os.rename(ename, "bin")

os.makedirs(os.path.join(f"{aname}.AppDir", "usr"))
shutil.move("bin", os.path.join(f"{aname}.AppDir", "usr"))

subprocess.run(["sudo", "chmod", "+x", f"{aname}.AppDir/usr/bin/{ename}"])

print("Generating AppRun...")

apprun = f"""#!/bin/sh
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
sudo sysctl -w kernel.unprivileged_userns_clone=1
HERE="$(dirname "$(readlink -f "${{0}}")")"
exec "$HERE/usr/bin/{ename}" "$@" --no-sandbox
"""

print("Generating .desktop file...")

desktop = f"""[Desktop Entry]
Name={aname}
Exec={ename} %U --no-sandbox
Icon={Path(iname).stem}
Type=Application
Categories={categories}
"""

print("Writing AppRun...")
f=open(f"{aname}.AppDir/AppRun","w");f.write(apprun);f.close()
print("Running chmod +x on AppRun...")
subprocess.run(["sudo", "chmod", "+x", f"{aname}.AppDir/AppRun"])
print("Writing .desktop file...")
f=open(f"{aname}.AppDir/{aname.lower()}.desktop","w");f.write(desktop);f.close()
print("Copying icon...")
shutil.copy2(iname, f"./{aname}.AppDir/{iname}")

print("Checking for appimagetool...")
if os.path.exists("appimagetool-x86_64.AppImage"):
    atool = "./"
    print("Found appimagetool.")
elif os.path.exists(f"/usr/bin/{"appimagetool-x86_64.AppImage"}"):
    print("Found appimagetool.")
else:
    print("Downloading appimagetool...")
    subprocess.run(["sudo", "wget", "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage", "-O", "usr/bin/appimagetool-x86_64.AppImage"])
print("Running chmod +x on appimagetool...")
subprocess.run(["sudo", "chmod", "+x", f"{atool}appimagetool-x86_64.AppImage"])
print("Compiling AppImage...")
os.system(f"ARCH=x86_64 {atool}appimagetool-x86_64.AppImage {aname}.AppDir")

print(f" D O N E ! App in ./{aname}-x86_64.AppImage")