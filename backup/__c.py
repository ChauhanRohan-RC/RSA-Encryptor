import os
import sys


class C:
    Version = "5.0.0"
    EncExt = ".rce"

    ExeName = "Rcrypt"
    UnInstallExeName = "Uninstall"
    RegExeName = "REG"
    Description = "A Powerful Encryptor that can Encrypt almost any file"

    Author = "Rohan Chauhan"
    ExpertDecKey = 'A3f$45fh78gs5fd34gsf#@haasd3224@45#6^*s7%hag32423hdsF*sh)ahdY6532'

    # Current Working Dir
    MainDir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
        os.path.abspath(os.path.realpath(__file__)))
    EncryptDatabaseDir = os.path.join(os.getenv('UserProfile'), f'{ExeName} Encrypted Database')
    MainDataDir = os.path.join(os.getenv('ProgramData'), ExeName)  # where all data files resides
    LogFilePath = os.path.join(MainDataDir, 'CryptLog.txt')  # Log file path

    # REGISTRY Attrs
    SendtoShortcutName = 'Add to Encrypted File'
    ExtAssociationName = ExeName.upper() + EncExt   # IN WINDOWS REGISTRY
    ContextMenuTitle = 'Decrypt'

    # Encryption Constants
    MinLimit = 12
    MaxLimit = 40

    # Decryption Constants
    DecNormal = 0
    DecFailed = 1
    DecLocked = 2
    DecChances = 3
    AccessRegainTime = 10  # minutes to able to retry the decryption
    AccessRegainSecs = round(AccessRegainTime * 60)
    MaxFailChances = 5  # after which it get locked and can only be decrypted by expert dec key

    # Encodings
    MetaEncoding = 'utf-8'
    TextEncoding = 'utf-8'
    TextCode = 2
    ByteCode = 3

    # Sizes (in Bytes) ......................................................
    ChunkSize = 4096
    PointerSize = 40960
    VoidByteArraySize = 29
    VoidByteSize = 17

    # ..............................   Separators   .....................
    TextBase = ':'

    # In Meta Data
    MetaBase = '||'
    NameBase = '#'
    DataTypeBase = '#'

    # In Pointer and Decryption Data
    PointerBase = '/'
    DecCodeBase = '<<'
    PointerDecSeparator = '%%'

    FileDataBase = bytes('__{{||}}__', encoding=TextEncoding)
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


class ImPaths:
    IconsDir = os.path.join(C.MainDir, 'icons')
    PassShow = os.path.join(IconsDir, 'show_20.png')
    PassHide = os.path.join(IconsDir, 'hide_20.png')

    EncIm = os.path.join(IconsDir, 'encrypt_color_64.png')
    DecIm = os.path.join(IconsDir, 'decrypt_color_64.png')
    MainIcon = os.path.join(IconsDir, 'decrypt_color_64.ico')  # For Window icon

    DecIcon = os.path.join(IconsDir, 'decrypt_color_64.ico')     # For context menu open with
    EncFileIcon = os.path.join(IconsDir, 'encrypted_file_256.ico')   # for encrypted file icon


def resources_check():
    """ Makes Sure of all Resources """
    # Directories
    if not os.path.isdir(C.MainDataDir):
        os.makedirs(C.MainDataDir)
    if not os.path.isdir(C.EncryptDatabaseDir):
        os.makedirs(C.EncryptDatabaseDir)

    # Images
    for _attr, _val in ImPaths.__dict__.items():
        if '__' not in _attr:
            if not os.path.exists(_val):
                return False
    return True
