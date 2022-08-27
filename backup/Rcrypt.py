import os
import sys
import time
import reg_api
from consolecolor import Color
from tkinter import Tk, filedialog
from __c import ColorScheme, C, format_secs
from crypt_api import EncBatch, DecBatch, clear_read_only

# cache progress vars
_file_in_enc_prog = ''
_file_in_dec_prog = ''


def _quit(cap='\n-->> Exiting CLI..........', code=0):
    color.warning(cap)
    win.destroy()
    Cs.save_color_scheme()
    sys.exit(code)


def _pre():  # to ensure all directories and resources exists
    if not os.path.isdir(C.main_data_dir):
        os.makedirs(C.main_data_dir)
    # reg_api.get_reg_value()


def enc_prog(what, f_name, per):
    global _file_in_enc_prog
    if what == 'path':
        color.bprogress(f'\n-> Resolving Output File Path : <<{Cs.FileName} {f_name} {Cs.BoldProgress }>>')
    elif what == 'meta':
        color.bprogress(f'\n-> Packing Meta in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.BoldProgress}>>')
    elif what == 'pointer':
        color.bprogress(f'\n-> Packing Data Pointers in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.BoldProgress}>>')
    elif what == 'data':
        if _file_in_enc_prog == f_name:
            color.progress(f'--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.Percentage}{per} %{Cs.Progress}', end='\r')
        else:
            color.progress(f'\n--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.Percentage}{per} %{Cs.Progress}', end='\r')
            _file_in_enc_prog = f_name


def dec_prog(what, f_name, per):
    global _file_in_dec_prog
    if what == 'meta':
        color.bprogress(f'\n-> Resolving Meta in encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25] + ".."} {Cs.BoldProgress}>>')
    elif what == 'pointer':
        color.bprogress(f'\n-> Resolving Pointers in encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25] + ".."} {Cs.BoldProgress}>>')
    elif what == 'data':
        if _file_in_dec_prog == f_name:
            color.progress(f'--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.Percentage}{per} %{Cs.Progress}', end='\r')
        else:
            color.progress(f'\n--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.Percentage}{per} %{Cs.Progress}', end='\r')
            _file_in_dec_prog = f_name


def _validate_pass(pass_word):
    _u, _l, _s, _d, _len = False, False, False, False, 0
    for i in pass_word:
        if i.isalpha():
            if i.islower():
                _l = True
            else:
                _u = True
        elif i.isnumeric():
            _d = True
        else:
            _s = True
        _len += 1

    return _len, _u, _l, _s, _d


def get_pass(cap='-->> Choose Password', min_length=6):
    color.warning(f'\n-->> Note : Password must have at least 1 upper, 1 lower , 1 special char and 1 digit, {min_length} chars long )')
    __in = input(color(f'{cap} : ', Cs.PasswordIn))
    _len, _u, _l, _s, _d = _validate_pass(__in)

    while not (_len >= min_length and _u and _l and _s and _d):
        if _len < min_length:
            color.bwarning(f'--> Password Strength weak, must be at least {min_length} chars long....')
        elif not _u:
            color.bwarning(f'--> Password must have at least one upper case char....')
        elif not _l:
            color.bwarning(f'--> Password must have at least one lower case char....')
        elif not _s:
            color.bwarning(f'--> Password must have at least one special char....')
        else:
            color.bwarning(f'--> Password must have at least one digit....')

        __in = input(color(f'{cap} : ', Cs.PasswordIn))
        _len, _u, _l, _s, _d = _validate_pass(__in)

    return __in


def check_pass(c_pass, chances=3, file_name='', cap='\n-->> Enter Password'):
    while chances:
        __cap = f'{cap} {"" if not file_name else f"of <<{Cs.FileName} {file_name} {Cs.PasswordIn}>> "}: '
        __in = input(color(__cap, Cs.PasswordIn))
        if __in == c_pass:
            return True
        chances -= 1
        if chances:
            color.bwarning(f'-> Invalid Password, chances left : {color.Cyan}{chances}')

    return False


def set_black_status(e_f_des, fail_count):
    _code = C.DecFailed if fail_count < C.MaxFailChances else C.DecLocked
    _del_time = (C.AccessRegainSecs * fail_count)

    __prev_pos = e_f_des.tell()
    e_f_des.seek(DEC.dec_data_pos, 0)
    e_f_des.log(DEC.get_dec_data_bytes((_code, fail_count, time.time() + _del_time)))
    e_f_des.seek(__prev_pos, 0)

    return _code, _del_time


def release_black_status(e_f_des):
    __prev_pos = e_f_des.tell()
    e_f_des.seek(DEC.dec_data_pos, 0)
    e_f_des.log(DEC.get_dec_data_bytes((0, 0, time.time())))
    e_f_des.seek(__prev_pos, 0)


def encrypt_files(path_seq):
    fd_seq = []
    for __p in path_seq:
        if os.path.isfile(__p):
            if os.path.splitext(__p)[1] == C.EncExt:
                color.warning(f'--> warning : File <<{Cs.FileName} {os.path.basename(__p)} {color.WarnC}>> already encrypted...')
                continue
            r_acc, w_acc = os.access(__p, os.R_OK), os.access(__p, os.W_OK)
            if r_acc and w_acc:
                fd_seq.append(open(__p, 'rb'))
            else:
                color.bwarning(f'-> Error : File <<{Cs.FileName} {os.path.basename(__p)} {color.Bold + color.WarnC}>> Access Denied -->> READ ACCESS : {r_acc}, WRITE ACCESS : {w_acc}')
        else:
            color.bwarning(f'--> Error : File <<{Cs.FileName} {os.path.basename(__p)} {color.Bold + color.WarnC}>> does not exists')

    if fd_seq:
        __in = get_pass()
        __out_name = input(color('\n-->> Choose a name for output encrypted file ("a" for automatic selection, "b" for browse): ', Cs.FileIn))
        while not __out_name:
            color.error('--> Invalid Input')
            __out_name = input(color('\n-->> Choose a name for output encrypted file ("a" for automatic selection, "b" for browse): ', Cs.FileIn))
        if __out_name.lower() == 'a':
            out_path = None
        elif __out_name.lower() == 'b':
            out_path = filedialog.asksaveasfilename(initialdir="C;\\", title="Save As", filetypes=(('Rc Encrypted File', f'*{C.EncExt}'),))
            if out_path:
                out_path += C.EncExt
            else:
                out_path = None
        else:
            out_path = os.path.join(os.path.dirname(path_seq[0]), __out_name + C.EncExt)
        try:
            ENC.encrypt_batch(fd_seq=fd_seq, pass_word=__in, b_f_path=out_path, enc_ext=C.EncExt, on_prog_call=enc_prog)
        except Exception as enc_e:
            color.error(f'\n\n-> Exception while encrypting <<{Cs.FileName} {os.path.basename(ENC.b_f_path)} {color.ErrorC}>> : {enc_e}')
        else:
            color.success(f'\n\n_--> Input Files Encrypted Successfully, Output File :  {Cs.FileName} {os.path.basename(ENC.b_f_path)}')
        finally:
            for fd in fd_seq:
                fd.close()
    else:
        color.error(f'\n\n-->Error : Encryption failed, No Valid Input Files')


def _main_decryption(e_f_des):
    __out_dir = filedialog.askdirectory(initialdir="C;\\", title="Choose a directory to save decrypted files")
    if not __out_dir:
        __out_dir = None
    try:
        DEC.decrypt_batch(e_b_des=e_f_des, out_dir=__out_dir, set_header=False, on_prog_call=dec_prog)
    except Exception as dec_e:
        color.error(
            f'\n\n-> Exception while decrypting <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {color.ErrorC}>> : {dec_e}')
    else:
        color.success(
            f'\n\n--> File <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {color.SuccessC}>> decrypted Successfully, Output Directory : <<{Cs.FileName} {DEC.out_dir} {color.SuccessC}>>')


def decrypt_file(e_f_path, chances=C.DecChances):
    if os.path.isfile(e_f_path):
        if os.path.splitext(e_f_path)[1] == C.EncExt:
            clear_read_only(e_f_path)
            try:
                with open(e_f_path, 'rb+') as e__f:
                    DEC.set_header(e__f, on_prog_call=dec_prog)

                    # checking blacklist status
                    _black_code, _fail_count, _reset_time, = DEC.dec_data
                    if _black_code == C.DecFailed:
                        _del_time = _reset_time - round(time.time())
                        if _del_time > 0:
                            color.error(f'\n -->> Error : Access Unauthorized, Try again after {Cs.Percentage}<< {format_secs(_del_time, out="str")} >>')
                            return False

                    if _black_code in (C.DecNormal, C.DecFailed):
                        if check_pass(c_pass=DEC.user_pass, chances=chances, file_name=os.path.basename(e_f_path)):
                            if _black_code == C.DecFailed:
                                release_black_status(e__f)
                            _main_decryption(e__f)
                        else:
                            _code, _del_time = set_black_status(e__f, _fail_count + 1)
                            if _code == C.DecFailed:
                                color.error(f'\n--> Access Unauthorized, Fail Attempts : {(_fail_count + 1) * C.DecChances}, Try Again After {Cs.Percentage}<< {format_secs(_del_time, out="str")} >>{Cs.Error}....')
                            elif _code == C.DecLocked:
                                color.error(f'\n\n-->> Fatal User Error : Attempts Limit Reached, File Locked and can only be decrypted by {Cs.Percentage}<< Expert Decryption Key >>{Cs.Error}')

                    elif _black_code == C.DecLocked:
                        # if file is locked
                        color.bwarning(f'\n\n ....................   File <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Warn}>> is LOCKED  ...................')
                        __in = input(color(f'\n\n-->> Enter Expert Decryption Key to Unlock <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.CommandIn}>> : ', Cs.CommandIn))
                        if __in == C.ExpertDecKey:
                            release_black_status(e__f)
                            _main_decryption(e__f)
                        else:
                            color.error('\n-->> Error : Invalid Expert Decryption Key')

            except Exception as _enc_file_e:
                color.error(f'\n-> Exception while Decrypting <<{Cs.FileName} {os.path.basename(e_f_path)} {color.ErrorC}>> : {_enc_file_e}')
        else:
            color.error(f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {color.ErrorC}>> is not encrypted')
    else:
        color.error(f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {color.ErrorC}>> does not exists')


def main_cli(task=''):
    if not task:
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ", Cs.CommandIn)).lower()
    while task not in ('e', 'd', 'exit'):
        color.error(f"\n--> Error : Invalid command name '{task}'\n")
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ", Cs.CommandIn)).lower()

    if task == 'e':  # Encryption
        f_paths = filedialog.askopenfilenames(initialdir="C;\\", title="Choose Files to encrypt",
                                              filetypes=(('all files', '*.*'),))
        if f_paths:
            encrypt_files(f_paths)
        else:
            color.error('\n--> Error : No Input Files for Encryption')

    elif task == 'd':
        f_path = filedialog.askopenfilename(initialdir="C;\\", title="Choose Encrypted File to Decrypt",
                                            filetypes=(('Rc Encrypted File', f'*{C.EncExt}'),))
        if f_path:
            decrypt_file(f_path)
        else:
            color.error('\n--> Error : No Input File for Decryption')

    elif task == 'exit':
        _quit()


def main_arg(args):
    _len = len(args)
    if _len >= 2:
        _task = args[1].lower().replace('-', '')  # task arg, can be -e or -d
        if _task == 'e':
            if _len == 2:
                main_cli('e')
            else:
                encrypt_files(args[2:])
        elif _task == 'd':
            if _len == 2:
                main_cli('d')
            else:
                for _enc_path in args[2:]:
                    decrypt_file(_enc_path)
        else:
            color.error(f"\n--> Error : Invalid command name '{_task}'\n")
            main_cli()
    else:
        main_cli()


# main working dir
frozen_attr = getattr(sys, 'frozen', False)
main_dir = os.path.dirname(sys.executable) if frozen_attr else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
_pre()  # ensure all resources

ENC = EncBatch()   # encryptor instance
DEC = DecBatch()   # decryptor instance

Cs = ColorScheme(Color, C.ColorSchemeFilePath)  # Color Scheme of CLI
color = Color(progress=Cs.Progress, warning=Cs.WeakWarn, error=Cs.Error, success=Cs.Success)   # terminal color instance

color.enable_color()  # initialising color
Cs.load_color_scheme()  # loading ColorScheme

print(color(f'\n\n.............................   RC ENCRYPTOR v{C.Version} CLI   ..............................', Cs.Header))

win = Tk()
win.withdraw()

main_arg(sys.argv)  # main_arguments capture function

while True:
    main_cli()
