import os
import pickle
from __c import C

info_dic = {'zip_name': 'main.zip',
            'exe_in_zip': [C.RegExeName + '.exe', ],
            'soft_name': C.ExeName,
            'version': C.Version,
            'soft_author': C.Author,
            'soft_des': C.Description,
            'uninstall_key_name': C.ExeName,
            'main_exe_name': C.ExeName,
            'permissions': 'no'}

with open(os.path.join(C.main_dir, 'info.cc'), 'wb+') as _f:
    pickle.dump(info_dic, _f)
