import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win64":
        base = "Win64GUI"

includes = ["PyQt4.QtCore", "PyQt4.QtGui", "re","matplotlib","scipy","numpy","matplotlib.backends.backend_qt4agg","matplotlib.backends.backend_agg","matplotlib.backends.backend_tkagg"]

#setup
setup(
        name = "",
        version = "",
        options = {"build_exe": {"includes": includes}},
        executables = [Executable("AFDesignGA.py", base=base)],
)