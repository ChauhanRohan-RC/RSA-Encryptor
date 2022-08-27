import os
import sys
import time
from consolecolor import Color
from tkinter import Tk, filedialog
from __c import Theme, C, format_secs
from crypt_api import EncBatch, DecBatch, clear_read_only

# cache progress vars
_file_in_enc_prog = ''
_file_in_dec_prog = ''


def _quit(cap='\n-->> Exiting CLI..........', code=0):
    print(color(cap, Cs.Warning))
    win.destroy()
    sys.exit(code)


def _pre():  # to ensure all directories and resources exists
    if not os.path.isdir(C.main_data_dir):
        os.makedirs(C.main_data_dir)
    # reg_api.get_reg_value()


def enc_prog(what, f_name, per):
    global _file_in_enc_prog
    if what == 'path':
        print(color(f'\n-> Resolving Output File Path : <<{Cs.FileName} {f_name} {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'meta':
        print(color(f'\n-> Packing Meta in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'pointer':
        print(color(f'\n-> Packing Data Pointers in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'data':
        if _file_in_enc_prog == f_name:
            print(color(f'--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}', Cs.Progress), end='\r')
        else:
            print(color(f'\n--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}', Cs.Progress), end='\r')
            _file_in_enc_prog = f_name


def dec_prog(what, f_name, per):
    global _file_in_dec_prog
    if what == 'meta':
        print(color(f'\n-> Resolving Meta Data in Encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25]}... {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'pointer':
        print(color(f'\n-> Resolving Pointers in Encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25]}... {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'data':
        if _file_in_dec_prog == f_name:
            print(color(f'--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}', Cs.Progress), end='\r')
        else:
            print(color(f'\n--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}', Cs.Progress), end='\r')
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
    print(color(f'\n-->> Note : Password must have at least 1 upper, 1 lower , 1 special char and 1 digit, {min_length} chars long )', Cs.Instruction))
    __in = input(color(f'{cap} : ', Cs.UserInput))
    _len, _u, _l, _s, _d = _validate_pass(__in)

    while not (_len >= min_length and _u and _l and _s and _d):
        if _len < min_length:
            print(color(f'--> Password Strength weak, must be at least {min_length} chars long....', Cs.WeakWarning))
        elif not _u:
            print(color(f'--> Password must have at least one upper case char....', Cs.WeakWarning))
        elif not _l:
            print(color(f'--> Password must have at least one lower case char....', Cs.WeakWarning))
        elif not _s:
            print(color(f'--> Password must have at least one special char....', Cs.WeakWarning))
        else:
            print(color(f'--> Password must have at least one digit....', Cs.WeakWarning))

        __in = input(color(f'{cap} : ', Cs.UserInput))
        _len, _u, _l, _s, _d = _validate_pass(__in)

    return __in


def check_pass(c_pass, chances=3, file_name='', cap='\n-->> Enter Password'):
    while chances:
        __cap = f'{cap} {"" if not file_name else f"of <<{Cs.FileName} {file_name} {Cs.UserInput}>> "}: '
        __in = input(color(__cap, Cs.UserInput))
        if __in == c_pass:
            return True
        chances -= 1
        if chances:
            print(color(f'-> Invalid Password, chances left : {Cs.HighLight}{chances}{Cs.Warning}', Cs.Warning))

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
                print(color(f'--> warning : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> already encrypted...', Cs.Warning))
                continue
            r_acc, w_acc = os.access(__p, os.R_OK), os.access(__p, os.W_OK)
            if r_acc and w_acc:
                fd_seq.append(open(__p, 'rb'))
            else:
                print(color(f'-> Error : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> Access Denied -->> READ ACCESS : {r_acc}, WRITE ACCESS : {w_acc}', Cs.Warning))
        else:
            print(color(f'--> Error : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> does not exists', Cs.Warning))

    if fd_seq:
        __in = get_pass()
        __out_name = input(color('\n-->> Choose a name for output encrypted file ("a" for automatic selection, "b" for browse): ', Cs.UserInput))
        while not __out_name:
            print(color('--> Warning : No Input File Name', Cs.Warning))
            __out_name = input(color('\n-->> Choose a name for output encrypted file ("a" for automatic selection, "b" for browse): ', Cs.UserInput))
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
            print(color(f'\n\n-> Exception while encrypting <<{Cs.FileName} {os.path.basename(ENC.b_f_path)} {Cs.Error}>> : {Cs.HighLight}{enc_e}{Cs.Error}', Cs.Error))
        else:
            print(color(f'\n\n_--> Input Files Encrypted Successfully, Output File :  {Cs.FileName} {os.path.basename(ENC.b_f_path)}{Cs.Success}', Cs.Success))
        finally:
            for fd in fd_seq:
                fd.close()
    else:
        print(color(f'\n\n-->Error : Encryption failed, No Valid Input Files', Cs.Error))


def _main_decryption(e_f_des):
    __out_dir = filedialog.askdirectory(initialdir="C;\\", title="Choose a directory to save decrypted files")
    if not __out_dir:
        __out_dir = None
    try:
        DEC.decrypt_batch(e_b_des=e_f_des, out_dir=__out_dir, set_header=False, on_prog_call=dec_prog)
    except Exception as dec_e:
        print(color(f'\n\n-> Exception : While Decrypting <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {Cs.Error}>> : {Cs.HighLight}{dec_e}{Cs.Error}', Cs.Error))
    else:
        print(color(f'\n\n--> File <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {Cs.Success}>> decrypted Successfully, Output Directory : <<{Cs.FileName} {DEC.out_dir} {Cs.Success}>>', Cs.Success))


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
                            print(color(f'\n -->> Error : Access Unauthorized, Try again after {Cs.HighLight}<< {format_secs(_del_time, out="str")} >>{Cs.Error}', Cs.Error))
                            return False

                    if _black_code in (C.DecNormal, C.DecFailed):
                        if check_pass(c_pass=DEC.user_pass, chances=chances, file_name=os.path.basename(e_f_path)):
                            if _black_code == C.DecFailed:
                                release_black_status(e__f)
                            _main_decryption(e__f)
                        else:
                            _code, _del_time = set_black_status(e__f, _fail_count + 1)
                            if _code == C.DecFailed:
                                print(color(f'\n--> Access Unauthorized : {Cs.HighLight}Fail Attempts : {(_fail_count + 1) * C.DecChances}{Cs.Error}, Try Again After {Cs.HighLight}<< {format_secs(_del_time, out="str")} >>{Cs.Error}....'), Cs.Error)
                            elif _code == C.DecLocked:
                                print(color(f'\n\n-->> Fatal User Error : Attempts Limit Reached, File Locked and can only be decrypted by {Cs.HighLight}<< Expert Decryption Key >>{Cs.Error}', Cs.Error))

                    elif _black_code == C.DecLocked:
                        # if file is locked
                        print(color(f'\n\n ....................   File <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Warning}>> is LOCKED  ...................'), Cs.Warning)
                        __in = input(color(f'\n\n-->> Enter Expert Decryption Key to Unlock <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.UserInput}>> : ', Cs.UserInput))
                        if __in == C.ExpertDecKey:
                            release_black_status(e__f)
                            _main_decryption(e__f)
                        else:
                            print(color('\n-->> Error : Invalid Expert Decryption Key', Cs.Error))

            except Exception as _enc_file_e:
                print(color(f'\n-> Exception :  while Decrypting <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> : {Cs.HighLight}{_enc_file_e}{Cs.Error}', Cs.Error))
        else:
            print(color(f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> is not Encrypted', Cs.Error))
    else:
        print(color(f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> does not exists', Cs.Error))


def main_cli(task=''):
    if not task:
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ", Cs.CommandInput)).lower()
    while task not in ('e', 'd', 'exit'):
        print(color(f"\n--> Error : Invalid command name {Cs.HighLight}'{task}'\n", Cs.Error))
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ", Cs.CommandInput)).lower()

    if task == 'e':  # Encryption
        f_paths = filedialog.askopenfilenames(initialdir="C;\\", title="Choose Files to encrypt",
                                              filetypes=(('all files', '*.*'),))
        if f_paths:
            encrypt_files(f_paths)
        else:
            print(color('\n--> Error : No Input File for Encryption', Cs.Error))

    elif task == 'd':
        f_path = filedialog.askopenfilename(initialdir="C;\\", title="Choose Encrypted File to Decrypt",
                                            filetypes=(('Rc Encrypted File', f'*{C.EncExt}'),))
        if f_path:
            decrypt_file(f_path)
        else:
            print(color('\n--> Error : No Input File for Decryption', Cs.Error))

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
            print(color(f"\n--> Error : Invalid command name {Cs.HighLight}'{_task}'\n", Cs.Error))
            main_cli()
    else:
        main_cli()


# main working dir
frozen_attr = getattr(sys, 'frozen', False)
main_dir = os.path.dirname(sys.executable) if frozen_attr else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
_pre()  # ensure all resources

# ..............................      Class Instances       .................................
ENC = EncBatch()   # Encryptor Instance
DEC = DecBatch()   # Decryptor Instance

color = Color()    # Terminal Color Instance
color.resources_check()       # initialising color

Cs = Theme()       # Theme of CLI

print(color(f'\n\n.............................   RC ENCRYPTOR v{C.Version} CLI   ..............................', Cs.Header))

win = Tk()
win.withdraw()

main_arg(sys.argv)  # main_arguments capture function

while True:
    main_cli()
