import os
import sys
import reg_api
import winreg
from __c import C
from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW
from tkinter import Tk, messagebox


def del_ext_keys():
    reg_api.delete_key(winreg.HKEY_CLASSES_ROOT, C.EncExt)
    reg_api.delete_key(winreg.HKEY_CLASSES_ROOT, C.ExtAssociationName)


def del_sendto_link():
    return reg_api.delete_sendto_link(C.SendtoShortcutName)


def del_start_link():
    return reg_api.delete_start_menu_link(C.ExeName)


def del_uninstall_info():
    reg_api.delete_uninstall_info(C.ExeName)


def __del_init():
    """ should be called at last """
    __des_bat_path = os.path.join(C.main_dir, 'des_bat.bat')
    with open(__des_bat_path, 'w+') as _des_bat:
        _des_bat.write('rmdir /Q /S "%s"' % C.main_dir)

    s_info = None
    if os.name == 'nt':
        s_info = STARTUPINFO()
        s_info.dwFlags |= STARTF_USESHOWWINDOW

    Popen([__des_bat_path], startupinfo=s_info)


def main():
    if os.name == 'nt':
        try:
            del_ext_keys()
            del_sendto_link()
            del_start_link()
            del_uninstall_info()
            __del_init()
        except Exception as __e:
            pass


if len(sys.argv) > 1 and sys.argv[1] == '-force':
    main()
else:
    win = Tk()
    win.wm_withdraw()

    __in = messagebox.askyesno(parent=win, title='Confirm Uninstall', message=f'Are you sure to uninstall {C.ExeName} v{C.Version}')
    if __in:
        win.quit()
        win.destroy()
        main()
    else:
        sys.exit()
