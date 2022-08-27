import reg_api
import os
import winreg
from __c import C, ImPaths


def create_ext_keys():
    # MAIN EXT KEY
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, C.EncExt) as ext__k:
        winreg.SetValueEx(ext__k, '', 0, winreg.REG_SZ, C.ExtAssociationName)
        winreg.SetValueEx(ext__k, 'Content Type', 0, winreg.REG_SZ, 'encrypted/rce')
        winreg.SetValueEx(ext__k, 'Perceived Type', 0, winreg.REG_SZ, 'encrypted')

    # EXT Association Key
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, C.ExtAssociationName) as as__k:
        winreg.SetValueEx(as__k, '', 0, winreg.REG_SZ, 'RCE Encrypted File (Rcrypt)')
        # Default Icon
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, C.ExtAssociationName + '\\DefaultIcon') as ico__k:
            winreg.SetValueEx(ico__k, '', 0, winreg.REG_SZ, ImPaths.EncFileIcon)

        # Shell Command
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, C.ExtAssociationName + '\\shell\\open') as open__k:
            winreg.SetValueEx(open__k, '', 0, winreg.REG_SZ, C.ContextMenuTitle)
            winreg.SetValueEx(open__k, 'Icon', 0, winreg.REG_SZ, ImPaths.DecIcon)

        # Command Key
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, C.ExtAssociationName + '\\shell\\open\\command') as com__k:
            winreg.SetValueEx(com__k, '', 0, winreg.REG_SZ, f'"{os.path.join(C.main_dir, C.ExeName + ".exe")}" --d "%1"')


def create_sendto_link():
    return reg_api.create_sendto_link(os.path.join(C.main_dir, C.ExeName + ".exe"), icon_path=ImPaths.MainIcon, shortcut_name=C.SendtoShortcutName, window_style=1)


def create_start_link():
    return reg_api.create_start_menu_link(os.path.join(C.main_dir, C.ExeName + ".exe"), icon_path=ImPaths.MainIcon, window_style=1)


def add_un_info():
    reg_api.add_uninstall_info(display_name=f'{C.ExeName} v{C.Version} (x86)', uninstall_exe=os.path.join(C.main_dir, C.UnInstallExeName + ".exe"),
                               publisher=C.Author, version=C.Version, icon=ImPaths.MainIcon, install_dir=C.main_dir, exe_name=C.ExeName)


def main():
    if os.name == 'nt':
        try:
            create_ext_keys()
            create_sendto_link()
            create_start_link()
            add_un_info()
        except Exception as __e:
            pass


main()
