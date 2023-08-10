import sys
from cx_Freeze import setup, Executable
from __c import C, ImPaths

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "includes": ["tkinter"]}

# GUI applications require a different TextBase on Windows (the default is for a
# console application).
base = "Win32GUI"

main_crypt = Executable(script="UI.__init__.py",
                        icon=ImPaths.MainIcon,
                        base=base,
                        target_name=C.ExeName)

reg_exe = Executable(script='reg.py',
                     icon=ImPaths.MainIcon,
                     base=base,
                     target_name=C.RegExeName)

un_exe = Executable(script='Uninstall.py',
                    icon=ImPaths.DecIcon,
                    base=base,
                    target_name=C.UnInstallExeName)

setup(name=C.ExeName,
      version=C.Version,
      description=f"{C.ExeName} v{C.Version}",
      author=C.Author,
      options={"build_exe": build_exe_options},
      executables=[main_crypt, reg_exe, un_exe])
