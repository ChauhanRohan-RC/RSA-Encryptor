import traceback

from consolecolor import Color, CLITheme
from tkinter import Tk, filedialog
from __c import C, format_secs, resources_check
from crypt_api import *
import pwinput

# cache progress vars
_file_in_enc_prog = ''
_file_in_dec_prog = ''

# Encryptor Instance
_ENC: EncBatch = None

# Decryptor Instance
_DEC: DecBatch = None


def get_encryptor() -> EncBatch:
    global _ENC
    if _ENC is None:
        print(color(f'\n -> Loading Encryptor...', Cs.Header))
        _ENC = EncBatch()

    return _ENC


def get_decryptor() -> DecBatch:
    global _DEC
    if _DEC is None:
        print(color(f'\n -> Loading Decryptor...', Cs.Header))
        _DEC = DecBatch()

    return _DEC


def _quit(cap='\n-->> Exiting CLI..........', code=0):
    print(color(cap, Cs.Warning))
    win.destroy()
    sys.exit(code)


def perform_pre_checks():  # to ensure all directories and resources exists
    resources_check()


def enc_prog(what, f_name, per):
    global _file_in_enc_prog
    if what == 'path':
        print(color(f'\n-> Resolving Output File Path : <<{Cs.FileName} {f_name} {Cs.ProgressHead}>>', Cs.ProgressHead))
    elif what == 'meta':
        print(color(f'\n-> Packing Meta in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.ProgressHead}>>',
                    Cs.ProgressHead))
    elif what == 'pointer':
        print(
            color(f'\n-> Packing Data Pointers in file <<{Cs.FileName} {os.path.basename(f_name)} {Cs.ProgressHead}>>',
                  Cs.ProgressHead))
    elif what == 'data':
        if _file_in_enc_prog == f_name:
            print(color(
                f'--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}',
                Cs.Progress), end='\r')
        else:
            print(color(
                f'\n--> Encrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}',
                Cs.Progress), end='\r')
            _file_in_enc_prog = f_name


def dec_prog(what, f_name, per):
    global _file_in_dec_prog
    if what == 'meta':
        print(color(
            f'\n-> Resolving Meta Data in Encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25]}... {Cs.ProgressHead}>>',
            Cs.ProgressHead))
    elif what == 'pointer':
        print(color(
            f'\n-> Resolving Pointers in Encrypted file <<{Cs.FileName} {os.path.basename(os.path.realpath(f_name))[:25]}... {Cs.ProgressHead}>>',
            Cs.ProgressHead))
    elif what == 'data':
        if _file_in_dec_prog == f_name:
            print(color(
                f'--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}',
                Cs.Progress), end='\r')
        else:
            print(color(
                f'\n--> Decrypting file <<{Cs.FileName} {f_name} {Cs.Progress}>> : {Cs.ProgressPer}{per} %{Cs.Progress}',
                Cs.Progress), end='\r')
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


def _input_pass_internal(prompt, min_length):
    while True:
        cur_pass = pwinput.pwinput(prompt=prompt, mask="*")
        _len, _u, _l, _s, _d = _validate_pass(cur_pass)

        if _len < min_length:
            print(color(f'--> Password Strength weak, must be at least {min_length} chars long....', Cs.WeakWarning))
        elif not _u:
            print(color(f'--> Password must have at least one upper case char....', Cs.WeakWarning))
        elif not _l:
            print(color(f'--> Password must have at least one lower case char....', Cs.WeakWarning))
        elif not _s:
            print(color(f'--> Password must have at least one special char....', Cs.WeakWarning))
        elif not _d:
            print(color(f'--> Password must have at least one digit....', Cs.WeakWarning))
        else:
            return cur_pass


def get_pass(choose_prompt='-->> Choose Password: ', confirm_prompt='-->> Confirm Password: ', min_length=6,
             confirm_chances=2):
    print(color(
        f'\n-->> Note : Password must be at least {min_length} chars long, with an upper case, lower case, special char and digit)',
        Cs.Instruction))

    while True:
        in_pass = _input_pass_internal(prompt=choose_prompt, min_length=min_length)

        for i in range(confirm_chances):
            conf_pass = pwinput.pwinput(prompt=confirm_prompt, mask="*")
            if in_pass == conf_pass:
                break
            elif i < confirm_chances - 1:
                print(color("-->> Password did not match! Try again\n", Cs.Warning))
        else:
            print(color("\n-->> Password Confirmation Failed! Please retry...\n", Cs.Error))
            continue

        break

    return in_pass


def check_pass(c_pass, chances=3, file_name='', prompt='\n-->> Enter Password: '):
    __cap = f'{prompt} {"" if not file_name else f"of <<{Cs.FileName} {file_name} {Cs.UserInput}>> "}: '
    while chances:
        __in = pwinput.pwinput(prompt=__cap, mask="*")
        if __in == c_pass:
            return True
        chances -= 1
        if chances:
            print(color(f'-> Access Unauthorized. Attempts Left : {Cs.HighLight}{chances}{Cs.Warning}', Cs.Warning))

    return False


def encrypt_files(path_seq):
    fd_seq = []
    for __p in path_seq:
        if os.path.isfile(__p):
            if os.path.splitext(__p)[1] == EncExt:
                print(color(
                    f'--> warning : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> already encrypted...',
                    Cs.Warning))
                continue
            r_acc, w_acc = os.access(__p, os.R_OK), os.access(__p, os.W_OK)
            if r_acc and w_acc:
                fd_seq.append(open(__p, 'rb'))
            else:
                print(color(
                    f'-> Error : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> Access Denied -->> READ ACCESS : {r_acc}, WRITE ACCESS : {w_acc}',
                    Cs.Warning))
        else:
            print(color(f'--> Error : File <<{Cs.FileName} {os.path.basename(__p)} {Cs.Warning}>> does not exists',
                        Cs.Warning))

    if fd_seq:
        __in = get_pass()

        __out_name = None
        out_path = None

        while not __out_name:
            __out_name = input(
                color('\n-->> Choose a name for output encrypted file ("a" for automatic selection, "b" for browse): ',
                      Cs.UserInput))

            if not __out_name or __out_name.isspace():
                print(color('--> Warning : No Input File Name', Cs.Warning))
            elif __out_name == 'b':  # browse
                out_path = filedialog.asksaveasfilename(initialdir="C;\\", title="Save As",
                                                        filetypes=(('Rc Encrypted File', f'*{EncExt}'),))
                if out_path:
                    out_path += EncExt
                    break
                else:
                    out_path = None
                    print(color('--> Warning : No Input File Name', Cs.Warning))
                    continue
            elif __out_name == 'a':  # auto
                out_path = None
                break
            else:  # file name specified
                out_path = os.path.join(os.path.dirname(path_seq[0]), __out_name + EncExt)
                break

        encryptor = get_encryptor()
        try:
            encryptor.encrypt_batch(fd_seq=fd_seq, pass_word=__in, b_f_path=out_path, enc_ext=EncExt,
                                    on_prog_call=enc_prog)
        except Exception as enc_e:
            traceback.print_exc()
            traceback.print_exception(enc_e)
            print(color(
                f'\n\n-> Exception while encrypting <<{Cs.FileName} {os.path.basename(encryptor.b_f_path)} {Cs.Error}>> : {Cs.HighLight}{enc_e}{Cs.Error}',
                Cs.Error))
        else:
            print(color(
                f'\n\n_--> Input Files Encrypted Successfully, Output File :  {Cs.FileName} {os.path.basename(encryptor.b_f_path)}{Cs.Success}',
                Cs.Success))
        finally:
            for fd in fd_seq:
                fd.close()
    else:
        print(color(f'\n\n-->Error : Encryption failed, No Valid Input Files', Cs.Error))


def _main_decryption(e_f_des):
    print(color('-->> Access Granted!', Cs.Success))
    __out_dir = filedialog.askdirectory(initialdir="C;\\", title="Choose a directory to save decrypted files")
    if not __out_dir:
        __out_dir = None
    try:
        get_decryptor().decrypt_batch(e_b_des=e_f_des, out_dir=__out_dir, set_header=False, on_prog_call=dec_prog)
    except Exception as dec_e:
        traceback.print_exception(dec_e)
        print(color(
            f'\n\n-> Exception : While Decrypting <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {Cs.Error}>> : {Cs.HighLight}{dec_e}{Cs.Error}',
            Cs.Error))
    else:
        print(color(
            f'\n\n--> File <<{Cs.FileName} {os.path.basename(os.path.realpath(e_f_des.name))} {Cs.Success}>> decrypted Successfully, Output Directory : <<{Cs.FileName} {get_decryptor().out_dir} {Cs.Success}>>',
            Cs.Success))


def decrypt_file(e_f_path, chances=DecChancesPerTry):
    if not os.path.isfile(e_f_path):
        print(
            color(f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> does not exists',
                  Cs.Error))
        return False

    if not os.path.splitext(e_f_path)[1] == EncExt:
        print(color(
            f'\n--> Error : Input file <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> is not Encrypted',
            Cs.Error))
        return False

    clear_read_only(e_f_path)
    decryptor = get_decryptor()

    try:
        with open(e_f_path, 'rb+') as e_f_des:
            decryptor.set_header(e_f_des, on_prog_call=dec_prog)

            # checking blacklist status
            dec_code, fail_count, regain_timestamp, = decryptor.dec_data
            if dec_code == DecFailed:
                regain_secs = regain_timestamp - round(time.time())
                if regain_secs > 0:
                    print(color(
                        f'\n -->> Error : Access Unauthorized, Try again after {Cs.HighLight}<< {format_secs(regain_secs, out="str")} >>{Cs.Error}',
                        Cs.Error))
                    return False

            if dec_code in (DecNormal, DecFailed):
                if check_pass(c_pass=get_decryptor().user_pass, chances=chances,
                              file_name=os.path.basename(e_f_path)):
                    if dec_code != DecNormal:
                        decryptor.update_lock_status(e_f_des, 0, commit=True)
                    _main_decryption(e_f_des)
                else:
                    dec_code, regain_secs = decryptor.update_lock_status(e_f_des, fail_count + 1, commit=True)
                    if dec_code == DecFailed:
                        print(color(
                            f'\n--> Access Unauthorized : {Cs.HighLight}Fail Attempts : {(fail_count + 1) * DecChancesPerTry}{Cs.Error}, Try Again After {Cs.HighLight}<< {format_secs(regain_secs, out="str")} >>{Cs.Error}....'),
                            Cs.Error)
                    elif dec_code == DecLocked:
                        print(color(
                            f'\n\n-->> Authorization Frozen : Attempts Limit Reached, File is now locked and can only be decrypted by {Cs.HighLight}<< Expert Decryption Key >>{Cs.Error}',
                            Cs.Error))

            elif dec_code == DecLocked:
                # if file is locked
                print(color(
                    f'\n\n ....................   File <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Warning}>> is LOCKED  ...................', Cs.Warning))
                print(color('-> Connecting to server for expert decryption verification...', Cs.ProgressHead))

                import jkkguyv523asdasd
                if jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h:
                    __in = pwinput.pwinput(
                        f'\n\n-->> Enter Expert Decryption Key to Unlock <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.UserInput}>> : ',
                        "*")
                    if __in == jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h:
                        decryptor.update_lock_status(e_f_des, 0, commit=True)
                        _main_decryption(e_f_des)
                    else:
                        print(color('\n-->> Error : Invalid Expert Decryption Key', Cs.Error))
                else:
                    print(color('\n-->> Fatal Error : Failed to verify Expert Decryption Key from server!!',
                                Cs.Error))

    except Exception as _enc_file_e:
        traceback.print_exception(_enc_file_e)
        print(color(
            f'\n-> Exception : while Decrypting <<{Cs.FileName} {os.path.basename(e_f_path)} {Cs.Error}>> : {Cs.HighLight}{_enc_file_e}{Cs.Error}',
            Cs.Error))
    finally:
        read_only(e_f_path)


def main_cli(task=''):
    if not task:
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ",
                           Cs.CommandInput)).lower()
    while task not in ('e', 'd', 'exit'):
        print(color(f"\n--> Error : Invalid command name {Cs.HighLight}'{task}'\n", Cs.Error))
        task = input(color("\n-->> Enter Command ('e' for Encryption, 'd' for Decryption, 'exit' to Exit) : ",
                           Cs.CommandInput)).lower()

    if task == 'e':  # Encryption
        f_paths = filedialog.askopenfilenames(initialdir="C;\\", title="Choose Files to encrypt",
                                              filetypes=(('all files', '*.*'),))
        if f_paths:
            encrypt_files(f_paths)
        else:
            print(color('\n--> Error : No Input File for Encryption', Cs.Error))

    elif task == 'd':
        f_path = filedialog.askopenfilename(initialdir="C;\\", title="Choose Encrypted File to Decrypt",
                                            filetypes=(('Rc Encrypted File', f'*{EncExt}'),))
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


# ensure all resources
perform_pre_checks()

# ..............................      Class Instances       .................................
color = Color()  # Terminal Color Instance
color.enable_color()  # initialising color

Cs = CLITheme()  # Theme of CLI

print(color(f'\n\n.............................   RC ENCRYPTOR v{C.Version} CLI   ..............................',
            Cs.Header))

win = Tk()
win.withdraw()

main_arg(sys.argv)  # main_arguments capture function

while True:
    main_cli()
