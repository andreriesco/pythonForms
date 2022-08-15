#!python

# this script is used to generate python code from .ui files
# it will use the default python environment for the project
# please ensure that you installed pyside2 there

import importlib
import sys
import os
import subprocess
import re


def process_ui_file(filename: str):
    pyfilename = os.path.join(os.path.dirname(filename),"ui_"+os.path.splitext(os.path.basename(filename))[0]+".py")

    if not os.path.exists(pyfilename) or os.stat(pyfilename).st_mtime < os.stat(filename).st_mtime:
        print("Processing "+filename+"...")

    pyside2uic = subprocess.run([pyside2uicpath, "-o", pyfilename, filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )

    if pyside2uic.returncode != 0:
        print("Error executing pyside2-uic on file "+filename, file=sys.stderr)
        print(stderr, file=sys.stderr)
        sys.exit(-1)


if len(sys.argv) != 2:
    print("usage: _build_ui_files.py <path>", file=sys.stderr)
    sys.exit(-1)

rootdir = sys.argv[1]

if not os.path.isdir(rootdir):
    print(rootdir+"is not a valid folder", file=sys.stderr)
    sys.exit(-1)


# configures environment for current python interpreter
pythonpath = sys.executable

# check if there's a virtual env module we can activate
binpath = os.path.dirname(pythonpath)
activatepath = os.path.join(binpath, "activate_this.py")

pyside2uicpath = "pyside2-uic"

if os.path.isfile(activatepath):
    exec(open(activatepath).read())
    pyside2uicpath = os.path.join(binpath, pyside2uicpath)

try:
    import PySide2
except:
    print("pyside2 module not found.", file=sys.stderr)
    print("Please install it in your local python environment to be able to build .ui files.", file=sys.stderr)
    print("Something like:", file=sys.stderr)
    print("pip install pyside2", file=sys.stderr)
    print("should work.", file=sys.stderr)
    sys.exit(-1)


try:
    pyside2uic = subprocess.run([pyside2uicpath, "-v"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
except FileNotFoundError:
    print("Can't find pyside2-uic, check that it's in the system path or in your python environment's bin folder.", file=sys.stderr)
    sys.exit(-1)


if pyside2uic.returncode != 0:
    print("Error executing pyside2-uic", file=sys.stderr)
    print(stderr, file=sys.stderr)
    sys.exit(-1)
else:
    ver = pyside2uic.stdout.decode().strip()
    print("Using pyside2-uic version ", ver)

appconfig = re.compile(r"^appconfig_.*")
dotre = re.compile(r"^\..*")
uire = re.compile(r".*\.ui$")

# traverses current folder searching .ui files
for path, dirs, files in os.walk(os.path.abspath(rootdir)):

    # skip folders that have names starting with "." and their subfolders
    process = True

    for dir in path.split(os.path.sep):
        if dotre.match(os.path.basename(dir)) is not None:
            process = False
            break
        if appconfig.match(os.path.basename(dir)) is not None:
            process = False
            break

    if not process:
        continue

    for filename in filter(lambda n: uire.match(n) is not None, files):
        process_ui_file(os.path.join(path, filename))
