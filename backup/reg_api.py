import os
import winreg
import ctypes

"""  most registry commands requires administrator privileges  """


def create_shortcut(exe_path, icon_path, out_dir=None, shortcut_name=None, window_style=1):
    if os.name != 'nt':
        return False

    import win32com.client
    if not out_dir:
        out_dir = os.getenv('AppData') + '\\microsoft\\Windows\\Start Menu\\Programs'
    if not shortcut_name:
        shortcut_name = os.path.splitext(os.path.basename(exe_path))[0]
    shortcut_name += '.lnk'
    out_path = os.path.join(out_dir, shortcut_name)

    if os.path.isdir(out_dir):
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(out_path)
        shortcut.targetpath = exe_path
        shortcut.IconLocation = icon_path
        shortcut.WindowStyle = window_style
        shortcut.save()
        return True
    return False


def create_sendto_link(exe_path, icon_path, shortcut_name, window_style=1):
    return create_shortcut(exe_path=exe_path, icon_path=icon_path, out_dir=os.getenv('AppData') + "\\Microsoft\\Windows\\SendTo", shortcut_name=shortcut_name, window_style=window_style)


def create_start_menu_link(exe_path, icon_path, window_style=1):
    return create_shortcut(exe_path=exe_path, icon_path=icon_path, out_dir=os.getenv('AppData') + '\\microsoft\\Windows\\Start Menu\\Programs', shortcut_name=None, window_style=1)


def is_admin():
    """ returns 1 if admin ,0 otherwise"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return 0


def get_reg_value(reg_path, value_name='', field=winreg.HKEY_CLASSES_ROOT):
    try:
        with winreg.OpenKey(field, reg_path, 0, winreg.KEY_READ) as _k:
            __v, _ = winreg.QueryValueEx(_k, value_name)
            return __v

    except FileNotFoundError:
        return None


def set_reg_value(reg_path, subkey_value_dic, field=winreg.HKEY_CLASSES_ROOT):
    try:
        with winreg.CreateKey(field, reg_path) as _k:
            for key, val in subkey_value_dic.items():
                winreg.SetValueEx(_k, key, 0, winreg.REG_SZ, val)

        return True
    except (PermissionError, OSError, FileNotFoundError):
        return False


def run_as_admin(executable, arg=None):
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', executable, arg, None, 1)


def set_context_command(extension_seq, label, executable, exe_name, icon=None):
    """
    :param extension_seq : extensions for which command is to be set
    :param label: text to show in context menu
    :param icon: icon to shew in context menu
    :param executable: executable path for receiving command
    :param exe_name: title of shell folder
    """
    if icon is None:
        icon = executable

    reg_paths = []
    for _ext in extension_seq:
        try:
            _shell_p = f'SystemFileAssociations\\{_ext}\\shell\\{exe_name}'
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, _shell_p) as _shell_key:
                winreg.SetValueEx(_shell_key, '', 0, winreg.REG_SZ, label)
                winreg.SetValueEx(_shell_key, 'icon', 0, winreg.REG_SZ, icon)

            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{_shell_p}\\command') as _command_key:
                winreg.SetValueEx(_command_key, '', 0, winreg.REG_SZ, f'"{executable}""%1"')

        except (PermissionError, OSError):
            pass
        else:
            reg_paths.append(('HKEY_CLASSES_ROOT', _shell_p))

    return reg_paths


def add_open_with(extension_seq, executable, exe_name):
    exe_name += '.exe'
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'Applications\\{exe_name}\\shell\\open\\command') as _command_key:
        winreg.SetValueEx(_command_key, '', 0, winreg.REG_SZ, f'"{executable}""%1"')

    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'Applications\\{exe_name}\\SupportedTypes') as _s_key:
        for _ext in extension_seq:
            winreg.SetValueEx(_s_key, _ext, 0, winreg.REG_SZ, '')

    return 'HKEY_CLASSES_ROOT', f'Applications\\{exe_name}'


def add_uninstall_info(display_name, uninstall_exe, publisher, version='0.0.0', install_dir=None, icon=None, exe_name=None):
    if not icon:
        icon = uninstall_exe
    if not exe_name:
        exe_name = display_name
    if not install_dir:
        install_dir = os.path.dirname(uninstall_exe)

    version_major, version_minor = map(int, version.split('.')[:2])
    _un_r = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{exe_name}"
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, _un_r) as __key:
            winreg.SetValueEx(__key, "DisplayName", 0, winreg.REG_SZ, display_name)
            winreg.SetValueEx(__key, "DisplayVersion", 0, winreg.REG_SZ, version)
            winreg.SetValueEx(__key, "VersionMajor", 0, winreg.REG_DWORD, version_major)
            winreg.SetValueEx(__key, "VersionMinor", 0, winreg.REG_DWORD, version_minor)
            winreg.SetValueEx(__key, "UninstallString", 0, winreg.REG_SZ, uninstall_exe)
            winreg.SetValueEx(__key, "DisplayIcon", 0, winreg.REG_SZ, icon)
            winreg.SetValueEx(__key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(__key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(__key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(__key, "Language", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(__key, "Publisher", 0, winreg.REG_SZ, publisher)

    except Exception as e:
        print(e)

    finally:
        # returning path of uninstall key. can be reopened using getattr(winreg, field)
        return 'HKEY_LOCAL_MACHINE', _un_r


def get_subkeys(field, key):
    """
    :return: array containing names of all sub keys within the main key
    """
    sub_keys = []
    with winreg.OpenKey(field, key) as _k:
        _info = winreg.QueryInfoKey(_k)
        for _i in range(_info[0]):
            sub_keys.append(winreg.EnumKey(_k, _i))
    return sub_keys


def delete_context_menu_command(extension_seq, exe_name):
    for _ext in extension_seq:
        try:
            _shell_p = f'SystemFileAssociations\\{_ext}\\shell\\{exe_name}'
            delete_key(winreg.HKEY_CLASSES_ROOT, _shell_p)

        except (PermissionError, FileNotFoundError, OSError):
            pass


def delete_open_with(exe_name):
    exe_name = exe_name + '.exe'
    try:
        delete_key(winreg.HKEY_CLASSES_ROOT, f'Applications\\{exe_name}')
    except (PermissionError, FileNotFoundError, OSError):
        pass


def delete_uninstall_info(exe_name):
    try:
        delete_key(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{exe_name}")
    except (PermissionError, FileNotFoundError, OSError):
        pass


def delete_start_menu_link(exe_name):
    shortcut_name = exe_name + '.lnk'
    shortcut_path = os.path.join(os.getenv('APPDATA'), f'microsoft\\Windows\\Start Menu\\Programs\\{shortcut_name}')
    if os.path.isfile(shortcut_path):
        os.remove(shortcut_path)
        return True
    return False


def delete_sendto_link(shortcut_name):
    short_path = os.path.join(os.getenv('AppData') + "\\Microsoft\\Windows\\SendTo", shortcut_name + '.lnk')
    if os.path.isfile(short_path):
        os.remove(short_path)
        return True
    return False


def delete_key(field, key):
    try:
        with winreg.OpenKey(field, key, 0, winreg.KEY_ALL_ACCESS) as _k:
            _no_sks = winreg.QueryInfoKey(_k)[0]  # no of sub keys

            # base case
            if _no_sks == 0:
                winreg.DeleteKey(field, key)
            else:
                sub_keys = []
                for _i in range(_no_sks):
                    sub_keys.append(winreg.EnumKey(_k, _i))
                for _s_key in sub_keys:
                    delete_key(field, f'{key}\\{_s_key}')
                winreg.DeleteKey(field, key)

    except (PermissionError, FileNotFoundError, OSError):
        pass
