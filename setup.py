import sys
from cx_Freeze import setup, Executable

silent = True
base = None
if sys.platform == "win32":
        base = "Win32GUI"

includes = ["PyQt4.QtCore", "PyQt4.QtGui", "re","binstr","numpy","matplotlib.backends.backend_qt4agg","matplotlib.backends.backend_agg","matplotlib.backends.backend_tkagg"]
includefiles =["xfoil.exe","FOILS"]
#setup
setup(
        name = "XGAG",
        version = "2.02",
        options = {"build_exe": {"includes": includes,"include_files":includefiles}},
        executables = [Executable("XGAG.py", base=base)],
)