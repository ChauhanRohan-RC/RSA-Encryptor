import os
import sys
import secrets
import time
from __c import C
from stat import S_IWUSR, S_IREAD, S_IRGRP, S_IROTH

""" ...........................................  Constants ..................................... """
# encrypted file extension
EncExt = C.EncExt

# Sizes
ChunkSize = C.ChunkSize                     # Bytes to read at a time
PointerSize = C.PointerSize                 # Header byte size that stores pointers and decryption data (Pointer Room)
VoidByteArraySize = C.VoidByteArraySize     # size of empty bytearray object in bytes
VoidByteSize = C.VoidByteSize               # size of empty byte object in bytes

# Encryption Constants
MinLimit = C.MinLimit  # min prime limit
MaxLimit = C.MaxLimit  # max prime limit

# decryption constants
DecNormal = C.DecNormal    # no fail decryption attempts yet
DecFailed = C.DecFailed    # at least 1 fail decryption attempt
DecLocked = C.DecLocked    # max fail decryption attempts

# Encodings
TextEncoding = C.TextEncoding           # Text File Data Encoding
MetaEncoding = C.MetaEncoding           # Meta and Pointer Data Encoding
TextCode = C.TextCode                  # indicate Text File
ByteCode = C.ByteCode                  # indicate Bytes File (Non Text)

# ..........................................    Separators     ..................................................
TextBase = C.TextBase                               # joins encrypted ints in a string

# In Meta Data
MetaBase = C.MetaBase                               # joins and surrounds meta data
NameBase = C.NameBase                               # joins file names in meta
DataTypeBase = C.DataTypeBase                       # joins data type code of files (2 : text file, 3 : bytes) in meta

# In Pointer Data
PointerBase = C.PointerBase                         # joins and surround pointers
DecCodeBase = C.DecCodeBase                         # joins and surround decryption data  (decryption_code, no_of_fails, timestamp)
PointerDecSeparator = C.PointerDecSeparator         # separates pointer and decryption data string in pointer room

FileDataBase = C.FileDataBase                       # used at the end of individual encrypted file data


#  ............................................ Static Functions....................................
def gcf(a, b):
    return a if b == 0 else gcf(b, a % b)


def co_prime(a, b):
    return True if gcf(a, b) == 1 else False


def is_prime(n):
    # Corner cases
    if n <= 1:
        return False
    if n <= 3:
        return True

    # if divisible by 2 or 3
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i = i + 6
    return True


def rgb(r_g_b):
    return '#%02x%02x%02x' % r_g_b


def get_ascii(string):
    """ return generator object having ascii code of each char """
    return (ord(i) for i in string)


def read_byte(fd, size=4096):
    return fd.read(size)


def yield_byte(fd, size=4096):
    for chunk in iter(lambda _f=fd, _s=size: read_byte(_f, _s), b''):
        yield bytearray(chunk)


def is_textfile(fd, chunk_size=102400, encoding='utf-8'):
    """
    :param fd: file descriptor opened in "rb" mode
    :param chunk_size: bytes to read
    :param encoding: file encoding
    :return: True if unicode codec can decode bytes
    """
    _p_pos = fd.tell()  # file position to be restored later
    __chunk = fd.read(chunk_size)
    try:
        __chunk.decode(encoding)
    except (ValueError, UnicodeError, IOError):
        return False
    else:
        return True
    finally:
        fd.seek(_p_pos, 0)  # restoring file position


def get_filesize(fd):
    """
    :param fd: file descriptor object
   """
    _p_pos = fd.tell()   # file position to be restored later
    # ...............
    fd.seek(0, 2)
    _file_size = fd.tell()
    # ..............
    fd.seek(_p_pos, 0)  # restoring file position
    return _file_size


def get_alt_path(path, count=1):
    """
    :param path: path to be checked
    :param count: current alternate path count
    :return: alternate path which does not exists yet
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            __p, __ext = os.path.splitext(path)
        else:
            __p, __ext = path, ''
        __r_p = "".join(reversed(__p))
        if count > 1 or ('(' in __r_p and __r_p.index('(') < 5):
            __r_p = __r_p[__r_p.index('(') + 1:]
            __p = "".join(reversed(__r_p))
        return get_alt_path(f'{__p}({count}){__ext}', count + 1)

    return path


def get_new_pos(pos, chunk_size, start=0):
    """ to get size multiple of chunk size """
    _size = pos - start
    _q, _r = divmod(_size, chunk_size)
    if _r == 0:
        return pos
    return start + ((_q + 1) * chunk_size)


def read_only(file_path):
    try:
        os.chmod(file_path, S_IREAD | S_IRGRP | S_IROTH)
    except (OSError, IOError):
        return False
    else:
        return True


def clear_read_only(file_path):
    try:
        os.chmod(file_path, S_IWUSR | S_IREAD)
    except (OSError, IOError):
        return False
    else:
        return True


# ............................... Classes .....................
class Encryptor:
    def __init__(self, prime1=None, prime2=None, min_limit=12, max_limit=40, text_base=':'):

        """ take p and q such that they are prime and p*q > max of original value (no in ascii table) """
        self.min_limit = min_limit
        self.max_limit = max_limit

        if prime1 is None or prime2 is None:
            primes = [i for i in range(self.min_limit, self.max_limit) if is_prime(i)]  # prime numbers in range
            prime1, prime2 = secrets.choice(primes), secrets.choice(primes)
            while prime1 == prime2:
                prime2 = secrets.choice(primes)

        self.p = prime1
        self.q = prime2
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)
        self.text_base = text_base  # used to join encrypted data

        self.enc_keys = self.get_enc_keys()
        self._enc_key = self.enc_keys[0]

        # constants worth attributing
        self.void_bytearray_size = VoidByteArraySize
        self.void_byte_size = VoidByteSize
        self.text_code = TextCode
        self.byte_code = ByteCode

    def get_enc_keys(self):
        return [i for i in range(2, self.pn) if co_prime(i, self.n) and co_prime(i, self.pn)]

    def encrypt_int(self, val, key):
        return (val ** key) % self.n

    def encrypt_str(self, string, key=None):
        """
        :return: str having encrypted ascii codes of string separated by TextBase
        """
        if key is None:
            key = self._enc_key
        _gen = get_ascii(string)
        return self.text_base.join(str(self.encrypt_int(i, key)) for i in _gen)

    def encrypt_seq(self, seq, key=None):
        """
        seq: sequence containing strings
        :return: generator having encrypted strings
        """
        return (self.encrypt_str(i, key) for i in seq)


class Decryptor:
    def __init__(self, prime1=None, prime2=None, text_base=':'):

        if prime1 and prime2:
            self.p, self.q = prime1, prime2
            self.n = self.p * self.q
            self.pn = (self.p - 1) * (self.q - 1)

            self.enc_keys = self.get_enc_keys()
            self._enc_key = self.enc_keys[0]  # first enc key
            self._dec_key = self.get_dec_keys(self._enc_key, 2)[0]  # first dec key of first enc key

        self.text_base = text_base  # used to split encrypted data

        # constants worth attributing
        self.void_bytearray_size = VoidByteArraySize
        self.void_byte_size = VoidByteSize
        self.text_code = TextCode
        self.byte_code = ByteCode

        # attrs set by set_meta_info, common to both decrypting file or batch file
        self.work_enc_key = -1  # enc key used in given meta
        self.work_dec_key = -1  # first dec key of work enc key
        self.user_pass = ''

    def set_primes(self, p, q):
        self.p, self.q = p, q
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)

        self.enc_keys = self.get_enc_keys()
        self._enc_key = self.enc_keys[0]
        self._dec_key = self.get_dec_keys(self._enc_key, 2)[0]

    def get_enc_keys(self):
        return [i for i in range(2, self.pn) if co_prime(i, self.n) and co_prime(i, self.pn)]

    def get_dec_keys(self, enc_key, num=1):
        return [i for i in range(1, num * self.pn) if (enc_key * i) % self.pn == 1]

    def get_dec_gen(self, enc_key, limit=10 ** 5):
        return (i for i in range(1, limit) if (enc_key * i) % self.pn == 1)

    def decrypt_int(self, val, dec_key):
        return (val ** dec_key) % self.n

    @staticmethod
    def _str_to_int(_str):
        # to protect enc_str splitting to empty strings
        return int(_str) if _str else -1

    def decrypt_str(self, enc_str, dec_key):
        return ''.join(chr(self.decrypt_int(i, dec_key)) for i in map(self._str_to_int, enc_str.split(self.text_base)) if i != -1)

    def decrypt_seq(self, enc_seq, dec_key):
        return (self.decrypt_str(i, dec_key) for i in enc_seq)

    @staticmethod
    def _decode_byte(byte, encoding='utf-8'):
        return byte.decode(encoding)


class EncBatch(Encryptor):
    """ for encrypting batch of files """
    def __init__(self, text_encoding=TextEncoding, chunk_size=ChunkSize, meta_base=MetaBase, meta_encoding=MetaEncoding,
                 pointer_base=PointerBase, pointer_size=PointerSize, name_base=NameBase, data_code_base=DataTypeBase,
                 file_data_base=FileDataBase, dec_code_base=DecCodeBase, pointer_dec_separator=PointerDecSeparator):

        Encryptor.__init__(self, min_limit=MinLimit, max_limit=MaxLimit, text_base=TextBase)

        self.chunk_size = chunk_size         # specific
        self.text_encoding = text_encoding

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding

        # pointer attrs
        self.pointer_base = pointer_base
        self.pointer_size = pointer_size      # specific, includes pointers and decryption codes in form \p1\p2\p3\%%<<code<<no_of_fails<<timestamp<<

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_code_base = dec_code_base  # different form pointer base
        self.pointer_dec_code_sep = pointer_dec_separator

        self.name_base = name_base            # specific
        self.data_code_base = data_code_base  # specific
        self.file_data_base = file_data_base  # specific, added only in end of encrypted data

        self.names = []  # file names in batch, clear after every task
        self.data_codes = []  # data codes of files in batch in str form, cleared after every task
        self.pointers = []  # pointers of files in batch in str form, cleared after every task

        self.b_f_path = ''     # output batch file path
        self.o_batch_size = 0  # sum of file sizes in batch
        self.o_batch_cal_size = 0  # calibrated size of batch w.r.t to chunk size (only for calculating purposes)
        self.r_batch_size = 0  # bytes read

    def clear_cache(self):
        self.b_f_path = ''
        self.o_batch_size = 0
        self.o_batch_cal_size = 0
        self.r_batch_size = 0

        self.names.clear()
        self.data_codes.clear()
        self.pointers.clear()

    def get_meta_str(self, fd_seq, enc_key_index, pass_word, enc_key):
        for fd in fd_seq:
            _name = os.path.basename(os.path.realpath(fd.name))
            _data_code = self.text_code if is_textfile(fd) else self.byte_code
            _f_size = get_filesize(fd)

            self.names.append(_name)
            self.data_codes.append(str(_data_code))
            self.o_batch_size += _f_size
            self.o_batch_cal_size += _f_size if _data_code == self.text_code else get_new_pos(_f_size, self.chunk_size, 0)

        return f'{self.meta_base}{self.p}{self.meta_base}{self.q}{self.meta_base}{self.encrypt_int(enc_key_index, self._enc_key)}' \
               f'{self.meta_base}{self.encrypt_str(self.encrypt_str(pass_word, enc_key), enc_key)}{self.meta_base}' \
               f'{self.encrypt_str(f"{self.name_base}".join(self.names), enc_key)}{self.meta_base}' \
               f'{self.encrypt_str(f"{self.data_code_base}".join(self.data_codes), enc_key)}{self.meta_base}'

    def get_meta_bytes(self, fd_seq, enc_key_index, pass_word, enc_key):
        m_b = bytes(self.get_meta_str(fd_seq, enc_key_index, pass_word, enc_key), encoding=self.meta_encoding)
        return m_b, sys.getsizeof(m_b) - self.void_byte_size

    def encrypt_batch(self, fd_seq, pass_word, b_f_path=None, enc_ext=EncExt, on_prog_call=lambda *args: print(args)):
        self.clear_cache()

        # 1. encryption key
        enc_key_index = secrets.randbelow(len(self.enc_keys))
        enc_key = self.enc_keys[enc_key_index]

        # 2. meta bytes
        m_b, m_s = self.get_meta_bytes(fd_seq, enc_key_index, pass_word, enc_key)
        self.pointers.append(str(self.pointer_size + m_s))  # first pointer

        # 3. configuring path of output batch file
        if not b_f_path:  # out batch enc file
            __dir = os.path.dirname(os.path.realpath(fd_seq[0].name))
            __name = "_".join(os.path.splitext(i)[0][:10] for i in self.names[:5])
            b_f_path = os.path.join(__dir, f'{__name}{enc_ext}')

        self.b_f_path = get_alt_path(b_f_path)
        on_prog_call('path', self.b_f_path, 0)
        __no = len(fd_seq)  # no of files

        # 4. encrypting data
        with open(self.b_f_path, 'wb+') as b__f:
            b__f.seek(self.pointer_size, 0)
            on_prog_call('meta', self.b_f_path, 1)
            b__f.write(m_b)

            # encryption
            for count, fd in enumerate(fd_seq, start=0):
                __start_pos = b__f.tell()
                _name = os.path.basename(os.path.realpath(fd.name))

                # 3, writing encrypted data
                fd.seek(0, 0)  # sets file pos to start

                if self.data_codes[count] == str(self.text_code):  # text file, no need to reed in chunks
                    chunk = bytes(self.encrypt_str(fd.read().decode(self.text_encoding), enc_key),
                                  encoding=self.text_encoding)  # main_cli text encryption logic

                    b__f.write(chunk)
                    b__f.write(self.file_data_base)
                    self.r_batch_size += get_filesize(fd)
                    on_prog_call('data', _name, round((self.r_batch_size / self.o_batch_cal_size) * 100, 2))
                else:
                    for chunk in yield_byte(fd, size=self.chunk_size):
                        chunk.reverse()  # main_cli bytes encryption logic
                        b__f.write(chunk)
                        self.r_batch_size += self.chunk_size
                        on_prog_call('data', _name, round((self.r_batch_size / self.o_batch_cal_size) * 100, 2))
                    b__f.write(self.file_data_base)

                if count != __no - 1:
                    cal_size = get_new_pos(b__f.tell(), self.chunk_size, start=__start_pos)  # calibrating file size
                    b__f.seek(cal_size, 0)
                    self.pointers.append(str(cal_size))

            # 5. writing pointers at beginning of file
            on_prog_call('pointers', self.b_f_path, 100)
            b__f.seek(0, 0)

            # saving pointers and decryption codes
            _dec_code_str = self.dec_code_base + self.dec_code_base.join(('0', '0', str(round(time.time())))) + self.dec_code_base
            _pointer_s = self.pointer_base + f"{self.pointer_base}".join(self.pointers) + self.pointer_base
            b__f.write(bytes(_pointer_s + self.pointer_dec_code_sep + _dec_code_str, encoding=self.meta_encoding))

        read_only(self.b_f_path)  # need to be cleared before decryption


class DecBatch(Decryptor):
    def __init__(self, text_encoding=TextEncoding, chunk_size=ChunkSize, meta_base=MetaBase, meta_encoding=MetaEncoding,
                 pointer_base=PointerBase, pointer_size=PointerSize, name_base=NameBase, data_code_base=DataTypeBase,
                 file_data_base=FileDataBase, dec_code_base=DecCodeBase, pointer_dec_separator=PointerDecSeparator):
        Decryptor.__init__(self, text_base=TextBase)

        self.chunk_size = chunk_size  # specific
        self.text_encoding = text_encoding

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding

        # pointer attrs
        self.pointer_base = pointer_base
        self.pointer_size = pointer_size      # specific, includes pointers and decryption codes in form \p1\p2\p3\%%<<code<<no_of_fails<<timestamp<<
        self.dec_data_pos = 0  # position at which decryption data starts

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_code_base = dec_code_base  # different form pointer base
        self.pointer_dec_code_sep = pointer_dec_separator
        self.dec_data = [0, 0, 0]  # in form (file_lock_code, no_of_fails, timestamp)

        self.name_base = name_base  # specific
        self.data_code_base = data_code_base  # specific
        self.file_data_base = file_data_base  # specific

        self.meta_str = ''
        self.names = []  # file names in batch, clear after every task
        self.data_codes = []  # data codes of files in batch in int form, cleared after every task
        self.pointers = []  # pointers of files in batch in int form, cleared after every task
        self._next_pointers = []  # next pointer to given pointer

        self.out_dir = ''  # output directory
        self.batch_strength = 0  # no of files in batch
        self.total_batch_size = 0  # file size of encrypted_batch file
        self.read_batch_size = 0  # bytes read

    def clear_cache(self):
        self.dec_data_pos = 0
        self.dec_data = [0, 0, 0]
        self.meta_str = ''
        self.names.clear()  # file names in batch, clear after every task
        self.data_codes.clear()  # data codes of files in batch in int form, cleared after every task
        self.pointers.clear()  # pointers of files in batch in int form, cleared after every task
        self._next_pointers.clear()

        self.out_dir = ''
        self.batch_strength = 0  # no of files in batch
        self.total_batch_size = 0  # file size of encrypted_batch file
        self.read_batch_size = 0  # bytes read

    def set_meta_info(self, meta_bytes):
        self.meta_str = meta_bytes.decode(self.meta_encoding)
        ms_array = self.meta_str.split(self.meta_base)[1:-1]

        # main_cli info
        self.set_primes(int(ms_array[0]), int(ms_array[1]))
        self.work_enc_key = self.enc_keys[self.decrypt_int(int(ms_array[2]), self._dec_key)]
        self.work_dec_key = self.get_dec_keys(self.work_enc_key, 2)[0]

        # user pass word
        self.user_pass = self.decrypt_str(self.decrypt_str(ms_array[3], self.work_dec_key), self.work_dec_key)

        # name of files in batch
        self.names = self.decrypt_str(ms_array[4], self.work_dec_key).split(self.name_base)
        self.batch_strength = len(self.names)

        # data codes of files in batch
        self.data_codes = list(map(int, self.decrypt_str(ms_array[5], self.work_dec_key).split(self.data_code_base)))

    def set_header(self, e_b_des, on_prog_call=lambda *args: print(args)):
        """
        :param e_b_des: encrypted batch file descriptor object in rb mode
        :param on_prog_call: call for progress
        sets meta info and pointers, also sets file position to first pointer
        """
        self.clear_cache()
        self.total_batch_size = get_filesize(e_b_des)
        e_b_des.seek(0, 0)

        __pointer_dec_str = e_b_des.read(self.pointer_size).decode(self.meta_encoding)
        __pointer_s, __dec_s = __pointer_dec_str.split(self.pointer_dec_code_sep)
        self.dec_data_pos = sys.getsizeof(bytes(__pointer_s + self.pointer_dec_code_sep, encoding=self.meta_encoding)) - self.void_byte_size

        self.dec_data = list(map(int, __dec_s.split(self.dec_code_base)[1:-1]))     # since dec_code base is also at start and end
        self.pointers = list(map(int, __pointer_s.split(self.pointer_base)[1:-1]))  # since pointer base is also at start and end
        on_prog_call('pointer', e_b_des.name, round((self.pointer_size / self.total_batch_size) * 100, 2))
        self._next_pointers = self.pointers[1:]  # excluding 1st pointer
        self._next_pointers.append(get_new_pos(self.total_batch_size, chunk_size=self.chunk_size, start=self.pointers[-1]))  # for last pointer

        self.set_meta_info(e_b_des.read(self.pointers[0] - self.pointer_size))
        on_prog_call('meta', e_b_des.name, round((self.pointers[0] / self.total_batch_size) * 100, 2))
        self.read_batch_size = self.pointers[0]

    def get_dec_data_bytes(self, dec_data=(0, 0, 0)):
        return bytes(self.dec_code_base + self.dec_code_base.join(str(round(_i)) for _i in dec_data) + self.dec_code_base, encoding=self.meta_encoding)

    def decrypt_batch(self, e_b_des, out_dir=None, set_header=False, on_prog_call=lambda *args: print(args)):
        if set_header:
            self.set_header(e_b_des=e_b_des, on_prog_call=on_prog_call)
        else:
            # file position should be at first pointer
            e_b_des.seek(self.pointers[0], 0)

        _path = os.path.realpath(e_b_des.name)
        _dir, _fname = os.path.split(_path)
        _name = os.path.splitext(_fname)[0]
        if not out_dir:
            out_dir = os.path.join(_dir, _name[:10] + '..(Decrypted)')
        else:
            out_dir = os.path.join(out_dir, _name[:10] + '..(Decrypted)')

        self.out_dir = get_alt_path(out_dir)
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)

        # main_cli data decryption
        for _name, _d_code, _pointer, _n_pointer in zip(self.names, self.data_codes, self.pointers, self._next_pointers):
            _f_path = get_alt_path(os.path.join(self.out_dir, _name))
            _r_size = _n_pointer - _pointer

            with open(_f_path, 'wb+') as o__f:
                if _d_code == self.text_code:  # text file
                    chunk = e_b_des.read(_r_size).split(self.file_data_base)[0]
                    o__f.write(bytes(self.decrypt_str(chunk.decode(self.text_encoding), self.work_dec_key), encoding=self.text_encoding))

                    self.read_batch_size += _r_size
                    on_prog_call('data', _name, round((self.read_batch_size / self.total_batch_size) * 100, 2))
                else:
                    _r_iters = int(_r_size / self.chunk_size)

                    for _iter in range(0, _r_iters):
                        chunk = bytearray(e_b_des.read(self.chunk_size))
                        if _iter == _r_iters - 1:  # last iteration
                            chunk = chunk.split(self.file_data_base)[0]
                        chunk.reverse()
                        o__f.write(chunk)

                        self.read_batch_size += self.chunk_size
                        _per = round((self.read_batch_size / self.total_batch_size) * 100, 2)
                        on_prog_call('data', _name, _per if _per <= 100.00 else 100.00)


# if __name__ == '__main__':
#     path = r"D:\rc\PycharmProjects\GAME\arc_bg_bg1_bullet1_button.rce"
#
#     clear_read_only(path)
#     DEC = DecBatch()
#     with open(path, 'rb+') as e__f:
#         DEC.set_header(e__f)
#         print(DEC.user_pass)
