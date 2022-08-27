import os
from consolecolor import FG


def format_mills(mills, out='tuple'):
    sec_ = mills // 1000
    min_, sec_ = divmod(sec_, 60)
    hr_, min_ = divmod(min_, 60)
    if out == 'tuple':
        return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'
    return f'{hr_:02d} hr {min_:02d} min {sec_:02d} sec'


def format_secs(secs, out='str'):
    min_, sec_ = divmod(secs, 60)
    hr_, min_ = divmod(min_, 60)
    if out == 'tuple':
        return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'
    return f'{hr_:02d} hr {min_:02d} min {sec_:02d} sec'


class C:
    Version = '4.0.0'
    EncExt = '.rce'
    ExeName = 'Rcrypt'
    ExpertDecKey = 'A3f$45fh78gs5fd34gsf#@haasd3224@45#6^*s7%hag32423hdsF*sh)ahdY6532'

    MainDataDir = os.path.join(os.getenv('AppData'), ExeName)               # where all data files resides
    ColorSchemeFilePath = os.path.join(MainDataDir, 'ColorScheme.txt')      # to Save And Modify Colour Scheme

    # Encryption Constants
    MinLimit = 12
    MaxLimit = 40

    # Decryption Constants
    DecNormal = 0
    DecFailed = 1
    DecLocked = 2
    DecChances = 3
    AccessRegainTime = 10                       # minutes to able to retry the decryption
    AccessRegainSecs = AccessRegainTime * 60
    MaxFailChances = 5                          # after which it get locked and can only be decrypted by expert dec key

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


class Theme:
    WeakWarning = FG.BrightYellow
    Warning = FG.Yellow
    WeakError = FG.BrightRed
    Error = FG.Red
    Success = FG.Green

    UserInput = FG.BrightCyan
    CommandInput = FG.BrightBlue

    FileName = FG.BrightBlue
    Progress = FG.White
    ProgressPer = FG.BoldCyan
    ProgressHead = FG.BrightMagenta

    Header = FG.BoldWhite
    HighLight = FG.BoldCyan
    Instruction = FG.BrightMagenta


# class ColorScheme:
#     def __init__(self, color_ob, file_path=''):
#         self.color_ob = color_ob
#         self.file_path = file_path
#
#         self.WeakWarn = self.color_ob.Yellow
#         self.Warn = self.color_ob.BoldYellow
#         self.Error = self.color_ob.Red
#         self.Success = self.color_ob.Green
#
#         self.PasswordIn = self.color_ob.Cyan
#         self.FileIn = self.color_ob.BoldBlue
#
#         self.Progress = self.color_ob.Magenta
#         self.BoldProgress = self.color_ob.Bold + self.Progress
#         self.Percentage = self.color_ob.BoldCyan
#         self.FileName = self.color_ob.Blue
#
#         self.CommandIn = self.color_ob.BoldCyan
#         self.Header = self.color_ob.Header
#
#     def load_color_scheme(self):
#         if self.file_path and os.path.isfile(self.file_path):
#             with open(self.file_path, 'r') as c__f:
#                 for _str in c__f.readlines():
#                     if _str and not _str.isspace():
#                         if '#' in _str:
#                             _str = _str.split('#')[0]
#                             if not _str or _str.isspace():
#                                 continue
#                         if '=' in _str:
#                             _attr, _val = _str.replace(' ', '').replace('\n', '').split('=')
#                             if hasattr(self, _attr):
#                                 if hasattr(self.color_ob, _val):
#                                     setattr(self, _attr, getattr(self.color_ob, _val))
#                                 elif _val in self.color_ob.__dict__.values():
#                                     setattr(self, _attr, _val)
#
#     def save_color_scheme(self):
#         with open(self.file_path, 'w+') as cs__f:
#             __unicode = f'\n\n# .............  ColorScheme Rcrypt v{C.Version} .....................\n\n# Keys are attributes of Class ColorScheme, Values are attributes of Class TermColor\n\n'
#
#             for __attr, __val in self.__dict__.items():
#                 if '__' not in __attr:
#                     __unicode += f'{__attr} = {__val}\n'
#
#             cs__f.log(__unicode)
