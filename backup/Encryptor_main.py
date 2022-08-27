import os
import os.path
import random
import sys
import time
from getpass import getpass
from tkinter import *
from tkinter import filedialog
from subprocess import Popen

version = 4.0


def gcf(a, b):  # greatest common factor
    if b == 0:
        return a
    else:
        return gcf(b, a % b)


def coprime(a, b):
    if gcf(a, b) == 1:
        return True
    return False


def isprime(n):
    # Corner cases
    if n <= 1:
        return False
    if n <= 3:
        return True

    # This is checked so that we can skip
    # middle five numbers in below loop
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i = i + 6

    return True


class FileManager:
    import pickle
    import shutil
    from stat import S_IREAD, S_IWUSR

    def __init__(self, fname=None):
        self.fname = fname

    def log(self, x):
        file = open(self.fname, "w+")
        file.write(x)
        file.close()

    def wb(self, data):
        try:
            file = open(self.fname, "wb+")
            file.write(data)
            file.close()
        except Exception as e:
            print(e)

    def append(self, y):
        file = open(self.fname, "a+")
        file.write(y)
        file.close()

    def read(self):
        try:
            file = open(self.fname, "r+")
            r = file.read()
            file.close()
            return r
        except FileNotFoundError:
            print(f" <{self.fname}> does not exist, could not read")

    def rl(self):
        try:
            file = open(self.fname, "r+")
            r = file.readlines()
            file.close()
            return r
        except FileNotFoundError:
            print(f" <{self.fname}> does not exist, could not readlines")

    def rb(self):
        try:
            file = open(self.fname, "rb+")
            r = file.read()
            file.close()
            return r
        except Exception as e:
            print(e)

    def create(self):
        try:
            file = open(self.fname, "x")
            file.close()
            return True
        except FileExistsError:

            print(f"File < {self.fname} > already exist")
            return False

    def delete(self):
        try:
            os.remove(self.fname)
            return True
        except FileNotFoundError:
            print("No such file to delete")
            return False

    def dir_name(self, filepath):
        dir_, name = os.path.split(filepath)
        return dir_, name

    def name_ex(self, filename):
        name, ex = os.path.splitext(filename)
        return name, ex

    def scan(self, fileformat_list, start, mode='path'):
        filename = []
        filepath = []
        for path, subdir, files in os.walk(start):

            for file in files:
                if self.name_ex(file)[1].lower() in fileformat_list:
                    filename.append(file)
                    filepath.append(os.path.join(path, file))
        if mode == "name":
            return filename
        elif mode == "path":
            return filepath
        else:
            return filepath, filename

    def write_bytes(self, data):
        try:
            with open(self.fname, 'wb+') as file:
                self.pickle.dump(data, file)
        except Exception as e:
            print(f'could not log bytes : {e}')

    def read_bytes(self):
        try:
            with open(self.fname, 'rb+') as file:
                data = self.pickle.load(file)
                return data

        except Exception as e:
            print(f'could not read bytes : {e}')

    def rename(self, opath, nname):
        try:
            head, tail = os.path.split(opath)
            npath = os.path.join(head, nname)
            os.renames(opath, npath)
            return True
        except FileNotFoundError:
            print("file does not exist")
            return False

    def copy(self, opath, npath):
        try:
            self.shutil.copy(opath, npath)
            return True
        except Exception as e:
            print(f"could not copy : {e}")
            return False

    def cleartext(self):
        try:
            file = open(self.fname, "w+")
            file.write("")
            file.close()
        except FileNotFoundError:
            print("file not found")

    def readonly(self):
        try:
            os.chmod(self.fname, self.S_IREAD)
            return True
        except FileNotFoundError:
            print("file not found")
            return False

    def clearreadonly(self):
        try:
            os.chmod(self.fname, self.S_IWUSR)
            return True
        except FileNotFoundError:
            print('File not found')
            return False

    def shuffle(self, list1, list2=None):
        if list2:
            c = list(zip(list1, list2))
            random.shuffle(c)
            list1, list2 = zip(*c)
            return list(list1), list(list2)
        else:
            random.shuffle(list1)
            return list1

    def exists(self):
        if os.path.exists(self.fname):
            return True
        else:
            return False

    def platform(self):
        if sys.platform.startswith('win'):
            return "win"
        elif sys.platform.startswith('darwin'):
            return 'darwin'
        else:
            return 'linux'


class Encryptor:
    def __init__(self, prime1, prime2,
                 base=' '):  # take p and q such that they are prime and p*q > max of orignal value (no in ascii table)
        self.p = prime1
        self.q = prime2
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)
        self.base = base  # used to concorate encrypted data

    def get_encryption_keys(self):
        encryption_keys = []
        for e__ in range(2, self.pn):
            if coprime(e__, self.n) and coprime(e__, self.pn):
                encryption_keys.append(e__)

        return encryption_keys

    def get_decryption_keys(self, encryption_key, no_of_keys=1):
        decryption_keys = []

        for i in range(1, no_of_keys * self.pn):
            if (encryption_key * i) % self.pn == 1:
                decryption_keys.append(i)
        return decryption_keys

    def encrypt_int(self, int_, key):
        return (int_**key) % self.n

    def encrypt_string(self, string_, key=None):
        if key is None:
            key = self.get_encryption_keys()[0]
        ascii_ = []
        e_ascii = []
        for i in range(len(string_)):
            ascii_.append(int(ord(string_[i])))

        for i in ascii_:
            e_ascii.append(self.encrypt_int(i, key))
        return self.base.join(str(i) for i in e_ascii)

    def encrypt_list(self, list_, key=None):
        if key is None:
            key = self.get_encryption_keys()[0]
        out_list = []
        for str_ in list_:
            out_list.append(self.encrypt_string(str_, key))
        return out_list

    def pack_meta(self, e_key_index, password_, original_ext, read_mode_, key):

        #      META :  (f'{p} {q} {e_key_in}' , 'pass', 'original ext', 'read_mode')
        #      pass ,ext and read_mode are encrypted

        meta_str = f'{self.p}{self.base}{self.q}{self.base}{e_key_index}'
        return meta_str, self.encrypt_string(self.encrypt_string(password_, key), key), self.encrypt_string(original_ext, key), self.encrypt_string(read_mode_, key)


class Decryptor:
    def __init__(self, prime1, prime2, base=' '):
        self.p = prime1
        self.q = prime2
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)
        self.base = base  # used to concorate encrypted data

        self.d_list = []
        self.e_list = []
        self.encryption_keys = []
        self.decryption_keys = []

    def get_encryption_keys(self):
        self.encryption_keys.clear()

        for e__ in range(2, self.pn):
            if coprime(e__, self.n) and coprime(e__, self.pn):
                self.encryption_keys.append(e__)

        return self.encryption_keys

    def get_decryption_keys(self, encryption_key, no_of_keys=1):
        self.decryption_keys.clear()

        for i in range(1, no_of_keys * self.pn):
            if (encryption_key * i) % self.pn == 1:
                self.decryption_keys.append(i)
        return self.decryption_keys

    def decrypt_int(self, int_, key):
        return (int_ ** key) % self.n

    def decrypt_string(self, e_string, key):
        self.e_list.clear()
        self.d_list.clear()

        a = e_string.split(self.base)
        for i in a:
            self.e_list.append(int(i))

        for i in self.e_list:
            self.d_list.append(self.decrypt_int(i, key))

        return ''.join(chr(i) for i in self.d_list)

    def decrypt_list(self, enc_list, key):
        out_list = []
        for e_str__ in enc_list:
            out_list.append(self.decrypt_string(e_str__, key))
        return out_list

    def unpack_meta(self, meta_touple__, d_key__):
        password_ = self.decrypt_string(self.decrypt_string(meta_touple__[1], d_key__), d_key__)
        original_file_ext_ = self.decrypt_string(meta_touple__[2], d_key__)
        read_mode_ = self.decrypt_string(meta_touple__[3], d_key__)

        return password_, original_file_ext_, read_mode_


# .................... Static functions.................................

def get_info_from_meta(meta_touple_, base=' '):
    prime1, prime2, enc_key_in = meta_touple_[0].split(base)
    prime1, prime2, enc_key_in = int(prime1), int(prime2), int(enc_key_in)
    return prime1, prime2, enc_key_in


def sys_exit(code=0, secs=1.5):
    time.sleep(secs)
    sys.exit(code)


# ..........................................MAIN CODE................................

# Directories.................
if getattr(sys, 'frozen', False):
    main_dir = os.path.dirname(sys.executable)
else:
    main_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, 'sdk')
icons_dir = os.path.join(sdk_dir, 'icons')
reg_dir = os.path.join(sdk_dir, 'reg')

check_file = os.path.join(reg_dir, 'checkreg.cc')

fcheck = FileManager(check_file)

if not fcheck.exists():
    m_exe1 = os.path.join(main_dir, 'Encryptor.exe')
    m_exe = m_exe1.encode('unicode_escape').decode()

    reg_path1 = os.path.join(reg_dir, 'reg1.reg')
    reg_path = reg_path1.encode('unicode_escape').decode()

    decryptor_ico1 = os.path.join(icons_dir, 'decryption_exe.ico')
    decryptor_ico = decryptor_ico1.encode('unicode_escape').decode()

    encrypted_ico1 = os.path.join(icons_dir, 'encrypted_file.ico')
    encrypted_ico = encrypted_ico1.encode('unicode_escape').decode()

    bat_path = os.path.join(reg_dir, 'reg.bat')

    freg = FileManager(reg_path1)
    fbat = FileManager(bat_path)

    freg.write(f'Windows Registry Editor Version 5.00\n\n[HKEY_CLASSES_ROOT]\n\n[HKEY_CLASSES_ROOT\*]\n\n[HKEY_CLASSES_ROOT\*\shell]\n\n[HKEY_CLASSES_ROOT\*\shell\Encryptor]\n"Icon"="\\"{m_exe}\\""\n@="Encrypt"\n[HKEY_CLASSES_ROOT\*\shell\Encryptor\command]\n@="\\"{m_exe}\\"\\"%1\\""'
               f'\n\n[HKEY_CLASSES_ROOT]\n[HKEY_CLASSES_ROOT\.rce]\n\n[HKEY_CLASSES_ROOT\.rce\DefaultIcon]\n@="\\"{encrypted_ico}\\""\n\n[HKEY_CLASSES_ROOT\.rce\Shell]\n\n[HKEY_CLASSES_ROOT\.rce\Shell\Encryptor]\n@="Decrypt"\n"Icon"="\\"{decryptor_ico}\\""\n\n[HKEY_CLASSES_ROOT\.rce\Shell\Encryptor\command]\n@="\\"{m_exe}\\"\\"%1\\""')
    fbat.write(f'regedit.exe /S "{reg_path1}"')
    p = Popen([bat_path])
    p.wait()

    fcheck.create()

# .................................................................................................................
expert_decryption_key = 'rohan@1234'  # IMPORTANT
max_dec_attempts = 3

# Fle info........................
ext = '.rce'
# ...................................
pass_cache = None


def main(o_file_path, password=None):
    global pass_cache

    # Input file info................
    fm = FileManager()

    o_file_dir, o_file_fname = fm.dir_name(o_file_path)
    o_file_n, o_file_ex = fm.name_ex(o_file_fname)

    fmo = FileManager(o_file_path)

    if o_file_ex == ext:
        mode = 'd'  # can be encryption or decryption depending on input file
    else:
        mode = 'e'

    read_mode = 'str'  # can be str or bytes

    if mode == 'e':  # ENCRYPTION............
        # Checking compatibility of file
        if pass_cache is None:
            print('\n\n ......................... MODE : ENCRYPTOR ........................')
        try:
            if fmo.exists():
                print('\nReading the file........ ')
                try:
                    o_data = fmo.read()
                    read_mode = 'str'
                    print(f'\nfile read successfully, mode : {read_mode}........')
                except Exception as e:
                    print(e)
                    try:
                        o_data = fmo.rb()
                        read_mode = 'bytes'
                        print(f'\nfile read successfully, mode : {read_mode}........')
                    except Exception as e:
                        print(e)
                        o_data = None
                        # sys_exit()
            else:
                print('File does not exists or access is denied...')
                o_data = None
                # sys_exit()
        except Exception as e:
            print(e)
            o_data = None
            # sys_exit()

        if o_data is not None:
            # choosing prime numbers
            min_limit = 10
            max_limit = 40

            primes = [i for i in range(min_limit, max_limit) if isprime(i)]  # prime numbers in range

            p = random.choice(primes)
            q = random.choice(primes)

            while q == p:
                q = random.choice(primes)

            E = Encryptor(p, q)

            e_keys = E.get_encryption_keys()
            e_key = random.choice(e_keys)  # choosing a random key
            e_key_in = e_keys.index(e_key)


            if read_mode == 'str':
                e_str = E.encrypt_string(o_data, e_key)
            else:
                e_str = o_data
            if password is None:
                password = getpass('\n--> Choose a password : ')
                confirm = getpass('   --> Confirm password : ')
                while not password:
                    print('\n\n            NO PASSWORD DETECTED, file encryption compromised')
                    retry_in = input('\n Press < r > to reinput password : ')
                    if retry_in == 'r':
                        password = getpass('Choose a password : ')
                        confirm = getpass('Confirm password : ')
                        continue
                    else:
                        password = '``'
                        confirm = '``'
                        break
                while confirm != password:
                    print('\n Password did not match , try again')
                    password = getpass('Choose a password : ')
                    confirm = getpass('Confirm password : ')

            pass_cache = password

            e_data = [e_str, E.pack_meta(e_key_in, password, o_file_ex, read_mode, e_key)]

            fme = FileManager(os.path.join(o_file_dir, f'{o_file_n}{ext}'))
            if fme.exists():
                overwrite_in = input('\nEncrypted file already exists , press < o > to overwrite : ')
                if overwrite_in == 'o':
                    fme.clearreadonly()
                    # fme.delete()
                else:
                    print('\nEncryption cancelled by user ............')
                    # sys_exit()
            else:
                overwrite_in = 'o'
            if overwrite_in == 'o':
                fme.write_bytes(e_data)
                fme.readonly()

                print(f'\nEncryption of {o_file_n} successful.........')
                del_input = input(f'\n      Do you want to delete the original <{o_file_n}> file\n(press < y > for yes) : ')
                if del_input == 'y':
                    fmo.delete()
                    print('\n File deleted successfully')
                # sys_exit(secs=1)

        else:
            print(f'Encryption of {o_file_n} Failed.....file is either corrupted or blank')
            # sys_exit()

    elif mode == 'd':
        print('\n\n ......................... MODE : DECRYPTOR ........................')
        fmo.clearreadonly()

        e_data = fmo.read_bytes()  # in form [e-str, ('p q e_key_in', e_pass, e_ext, e_read_mode)]
        e_str = e_data[0]  # main_cli file data

        meta_touple = e_data[-1]  # last element
        p, q, e_key_in = get_info_from_meta(meta_touple)

        D = Decryptor(p, q)

        e_keys = D.get_encryption_keys()
        e_key = e_keys[e_key_in]

        d_key = D.get_decryption_keys(e_key)[0]

        main_pass, o_ex, read_mode = D.unpack_meta(meta_touple, d_key)

        attempt_count = 0
        success = False
        if main_pass != '``':
            while attempt_count < max_dec_attempts:
                pass_in = getpass(f'\nEnter the password of encrypted {o_file_n} file: ')
                if pass_in == expert_decryption_key or pass_in == main_pass:
                    print('\nDecrypting the file........')
                    success = True
                    break

                else:
                    print('\n                     PASSWORD UNAUTHORIZED               \n')
                    success = False
                    attempt_count += 1
                    print(f'You have {max_dec_attempts - attempt_count} chances left')

        else:
            print('No password detected, auto decryption in progress.......')
            success = True

        if not success:
            print(f'\n DECRYPTION OF {o_file_n} FAILED (unauthorized).............')
            # sys_exit()
        else:
            if read_mode == 'str':
                d_str = D.decrypt_string(e_str, d_key)
            else:
                d_str = e_str
            fmd = FileManager(os.path.join(o_file_dir, f'{o_file_n}{o_ex}'))
            if fmd.exists():
                overwrite_in = input('\nDecrypted file already exists , press < o > to overwrite : ')
                if overwrite_in != 'o':
                    print('\nDecryption cancelled by user ............')
                    # sys_exit()
            else:
                overwrite_in = 'o'
            if overwrite_in == 'o':
                if read_mode == 'str':
                    fmd.write(d_str)
                else:
                    fmd.wb(d_str)
                print(f'\n Decryption of {o_file_n} Successful..........')
                # sys_exit(secs=1)


if __name__ == '__main__':

    print(f'\n\n ................................... RC FILE ENCRYPTOR v{version}........................')
    if len(sys.argv) == 1:
        win = Tk()
        win.withdraw()
        file_list = filedialog.askopenfilenames(title='Load Files to encrypt/encrypt', initialdir='C;\\')
        win.destroy()
    else:
        file_list = sys.argv[1:]

    if file_list:
        for path in file_list:
            main(path, password=pass_cache)
    sys_exit()
