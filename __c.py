import os
import sys

# ..............................................   Static Functions   .........................
def rgb(*r_g_b):
    return '#%02x%02x%02x' % r_g_b


def format_path(path, chars=30, start_weight=0.7):
    """
    :param path: file path
    :param chars: no of chars in formatted file path
    :param start_weight: weight of head of file path (excluding extension) in output
    :return: formatted file path
    """
    if len(path) <= chars:
        return path
    _name, _ext = os.path.splitext(path)
    _len_n = chars - len(_ext)
    _len_n1 = int(_len_n * start_weight)
    return f'{_name[:_len_n1 - 2]}...{_name[-(_len_n - _len_n1 - 1):]}{_ext}'  # -3 for 3 dots


def get_name(path: str, with_ext: bool = True):
    n = os.path.basename(path)
    return n if with_ext else os.path.splitext(n)[0]


def __format_time_component(val, label: str):
    val = int(round(val))
    return f'{val} {label}' if val > 0 else ""


def format_secs(secs, out='str'):
    min_, sec_ = divmod(secs, 60)
    hr_, min_ = divmod(min_, 60)
    if out == 'tuple':
        return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'

    return " ".join(fmt for fmt in (__format_time_component(hr_, 'hr'),
                                    __format_time_component(min_, 'min'),
                                    __format_time_component(sec_, 'sec')) if len(fmt) > 0)


def format_mills(mills, out='tuple'):
    return format_secs(mills // 1000, out=out)

# ..................................................................................


class Logger:
    def __init__(self, file_path='Log.txt'):
        self.file_path = file_path

    def clear(self):
        with open(self.file_path, 'w+') as l__f:
            l__f.write('')

    def log(self, text):
        with open(self.file_path, 'a+') as l__f:
            l__f.write('\n' + text)

    def warning(self, warning):
        self.log(f'\n -->> WARNING : {warning}\n')

    def error(self, error):
        self.log(f'\n -->> ERROR : {error}\n')

    def by_user(self, message):
        self.log(f'\n --> User Interruption : {message}\n')

    def show_log(self):
        os.startfile(self.file_path)


class C:
    Version = "8.2.0"
    EncExt = ".rce"

    ExeName = "Rcrypt"
    UnInstallExeName = "Uninstall"
    RegExeName = "REG"
    Description = "An encryption enigma"

    Author = "Rohan Chauhan"

    # Current Working Dir
    main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
        os.path.abspath(os.path.realpath(__file__)))
    res_dir = os.path.join(main_dir, "res")
    icons_dir = os.path.join(res_dir, "icons")
    fonts_dir = os.path.join(res_dir, "fonts")

    encrypted_database_dir = os.path.join(os.getenv('UserProfile'), f'{ExeName} Encrypted Database')
    main_data_dir = os.path.join(os.getenv('ProgramData'), ExeName)  # where all data files resides
    log_file_path = os.path.join(main_data_dir, 'CryptLog.txt')  # Log file path

    # REGISTRY Attrs
    SendtoShortcutName = 'Add to Encrypted File'
    ExtAssociationName = ExeName.upper() + EncExt   # IN WINDOWS REGISTRY
    ContextMenuTitle = 'Decrypt'

    # # Encryption Constants
    # MinLimit = 12
    # MaxLimit = 40
    #
    # # Decryption Constants
    # DecNormal = 0
    # DecFailed = 1
    # DecLocked = 2
    # DecChances = 3
    # AccessRegainTime = 2  # minutes to able to retry the decryption
    # AccessRegainSecs = round(AccessRegainTime * 60)
    # MaxFailChances = 3  # after which it get locked and can only be decrypted by expert dec key
    #
    # # Encodings
    # MetaEncoding = 'utf-8'
    # TextEncoding = 'utf-8'
    # TextCode = 2
    # ByteCode = 3
    #
    # # Sizes (in Bytes) ......................................................
    # ChunkSize = 4096
    # PointerSize = 40960
    # VoidByteArraySize = 29
    # VoidByteSize = 17
    #
    # # ..............................   Separators   .....................
    # TextBase = ':'
    #
    # # In Meta Data
    # MetaBase = '||'
    # NameBase = '#'
    # DataTypeBase = '#'
    #
    # # In Pointer and Decryption Data
    # PointerBase = '/'
    # DecCodeBase = '<<'
    # PointerDecSeparator = '%%'
    #
    # FileDataBase = bytes('__{{||}}__', encoding=TextEncoding)
    # ....................................................................
    PassMinChars = 6
    PassGoodChars = 8
    PassStrongChars = 11

    # ..........................   UI constants   ........................
    UiTitle = f'Rcrypt v{Version}'
    UiSize = (600, 400)
    UiLoopInterval = 500  # in ms
    UiFrameAnimationTime = 140  # in ms
    UiFrameAnimationStep = 0.1  # in relx or relwidth

    ext_fonts = [
        # "product_sans_light.ttf",
        "product_sans_medium.ttf",
        "product_sans_regular.ttf",
        # "product_sans_thin.ttf",
        "aquire.otf",
        "aquire_light.otf"
    ]


class ImPaths:
    PassShow = os.path.join(C.icons_dir, 'show_20.png')
    PassHide = os.path.join(C.icons_dir, 'hide_20.png')

    EncIm = os.path.join(C.icons_dir, 'encrypt_color_64.png')
    DecIm = os.path.join(C.icons_dir, 'decrypt_color_64.png')
    MainIcon = os.path.join(C.icons_dir, 'decrypt_color_64.ico')  # For Window icon

    DecIcon = os.path.join(C.icons_dir, 'decrypt_color_64.ico')     # For context menu open with
    EncFileIcon = os.path.join(C.icons_dir, 'encrypted_file_256.ico')   # for encrypted file icon


def resources_check():
    """ Makes Sure of all Resources """
    # Directories
    if not os.path.isdir(C.main_data_dir):
        os.makedirs(C.main_data_dir)
    if not os.path.isdir(C.encrypted_database_dir):
        os.makedirs(C.encrypted_database_dir)

    # Images
    for _attr, _val in ImPaths.__dict__.items():
        if '__' not in _attr:
            if not os.path.exists(_val):
                return False
    return True


def load_ext_fonts():
    import winfonts

    for font in C.ext_fonts:
        winfonts.load_font(os.path.join(C.fonts_dir, font))
