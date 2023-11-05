import math
import os
import sys
import secrets
import time
from collections.abc import Iterable
from stat import S_IWUSR, S_IREAD, S_IRGRP, S_IROTH

# Constants used as default in instances
EncExt = ".rce"

# ...........................  Encryption Constants  ............................
# # Minimum value of N = p * q. Original data should always be less than this value
# # Currently 256, which support encryption of 255 (8 bits) at max
# MIN_N = 1 << 8

# # Maximum value of N = p * q. Limits the size of encrypted data
# # currently 2^16 - 1 (or 16 bits), which limits encrypted data to 2 bytes
# MAX_N = (1 << 16) - 1           # Max value of N

"""
Structure

Encryption: original unit (ORG_UNIT_BYTES) ---> encrypted unit (ENC_UNIT_BYTES)
Decryption: encrypted unit (ENC_UNIT_BYTES) ---> original unit (ORG_UNIT_BYTES)

NOTE: encrypted unit must always be BIGGER THAN ORIGINAL UNIT to account for primes and decryption artifacts
"""

# Maximum size (in bytes) of the original data to be treated as a unit of encryption (an integer)
ORG_UNIT_BYTES = 2

# Size (in bytes) of the encrypted data that is decrypted to one original unit
ENC_UNIT_BYTES = ORG_UNIT_BYTES + 1

CHUNK_UNITS = 100  # Number of original/encrypted units in a chunk

# Decryption Constants
DecNormal = 0  # no fail decryption attempts yet
DecFailed = 1  # at least 1 fail decryption attempt
DecLocked = 2  # max fail decryption attempts

DecChancesPerTry = 3  # Max decryption Chances per try
MaxFailTries = 3    # after which it get locked and can only be decrypted by expert dec key

# Access regain secs = base * exp(exponent * fail_count)
AccessRegainSecsBase = round(5 * 60)   # 5 min
AccessRegainSecsExponent = 1

# Encodings
MetaEncoding = 'utf-8'  # Meta and Pointer Data Encoding
TextEncoding = 'utf-8'  # Text File Data Encoding
TextCode = 2  # indicate Text File
ByteCode = 3  # indicate Bytes File (Non Text)

# Sizes (in Bytes) ......................................................
PointerSize = 40960  # Header byte size that stores pointers and decryption data (Pointer Room)
# VoidByteArraySize = sys.getsizeof(bytearray())  # size of empty bytearray object in bytes
# VoidByteSize = sys.getsizeof(bytes())  # size of empty byte object in bytes

# ..............................   Separators   .....................
TextBase = ':'  # joins encrypted ints in a string

# In Meta Data
MetaBase = '||'  # joins and surrounds meta data
NameBase = '#'  # joins file names in meta
DataTypeBase = '#'  # joins data type code of files (2 : text file, 3 : bytes) in meta

# In Pointer and Decryption Data
PointerBase = '/'  # joins and surround pointers
DecCodeBase = '<<'  # joins and surround decryption data  (decryption_code, no_of_fails, timestamp)
PointerDecSeparator = '%%'  # separates pointer and decryption data string in pointer room

# FileDataBase = bytes('__{{||}}__', encoding=TextEncoding)  # used at the end of individual encrypted file data


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


def exp_mod(x, y, p):
    """
    Fast modulo exponentiation algorithm

    @:return (x^y) % p
    """
    res = 1  # Initialize result
    x = x % p  # Update x if it is more than or equal to p

    if x == 0:
        return 0

    while y > 0:
        # If y is odd, multiply x with result
        if y & 1:
            res = (res * x) % p

        # y must be even now
        y = y >> 1  # y = y/2
        x = (x * x) % p
    return res


def to_unicode_arr(string: str):
    """ return generator object having unicode code of each char """
    return (ord(i) for i in string)


def from_unicode_arr(unc_arr: Iterable) -> str:
    """ return generator object having characters for each unicode code point """
    return ''.join(map(chr, unc_arr))


def read_byte(fd, size=4096):
    return fd.read(size)


def yield_byte(fd, size=4096, mutable=True):
    for chunk in iter(lambda _f=fd, _s=size: read_byte(_f, _s), b''):
        yield bytearray(chunk) if mutable else chunk


def is_fd_textfile(fd, chunk_size=102400, encoding='utf-8'):
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


def is_path_textfile(path, chunk_size=102400, encoding='utf-8'):
    with open(path, 'rb') as o__f:
        try:
            o__f.read(chunk_size).decode(encoding=encoding)
        except (ValueError, UnicodeError, IOError):
            return False
        else:
            return True


def get_file_size(fd):
    """
    :param fd: file descriptor object
   """
    _p_pos = fd.tell()  # file position to be restored later
    # ...............
    fd.seek(0, 2)
    _file_size = fd.tell()
    # ..............
    fd.seek(_p_pos, 0)  # restoring file position
    return _file_size


# def get_alt_path(path, count=1):
#     """
#     :param path: path to be checked
#     :param count: current alternate path count
#     :return: alternate path which does not exists yet
#     """
#     if os.path.exists(path):
#         if os.path.isfile(path):
#             __p, __ext = os.path.splitext(path)
#         else:
#             __p, __ext = path, ''
#         __r_p = "".join(reversed(__p))
#         if count > 1 or ('(' in __r_p and __r_p.index('(') < 5):
#             __r_p = __r_p[__r_p.index('(') + 1:]
#             __p = "".join(reversed(__r_p))
#         return get_alt_path(f'{__p}({count}){__ext}', count + 1)
#
#     return path


def get_non_existing_path(path: str, return_suffix: bool = False):
    """
    generate's a non-existing path by Suffixing a number to an existing file/dir path

    :param path: path to be checked
    :param return_suffix: whether to return number suffixed as well
    :return: (number_suffixed, new_path) if return_suffix is True else new_path
    """
    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    num, index, last = 1, 0, len(base) - 1

    if base[last] == ')':
        index = base.rfind('(')
        if index != -1:
            try:
                num = int(base[index + 1: last])
                if base[index - 1] == ' ':
                    index -= 1
                    base = base[:index]
            except (TypeError, ValueError):
                pass

    while True:
        temp = f'{base} ({num}){ext}'
        if os.path.exists(temp):
            num += 1
        else:
            break

    return (num, temp) if return_suffix else temp


def create_batch_file_name(primary_dir, names) -> str:
    return f'{names[0]} (encrypted)'


def get_new_pos(cur_pos, chunk_size, start=0):
    """ to get size multiple of chunk size """
    _size = cur_pos - start
    _q, _r = divmod(_size, chunk_size)
    return cur_pos if _r == 0 else (start + ((_q + 1) * chunk_size))


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


def is_writable(path):
    __dir = path if os.path.splitext(path)[1] == '' else os.path.dirname(path)
    try:
        if not os.path.isdir(__dir):
            os.makedirs(__dir)
        with open(os.path.join(__dir, 'test.cc'), 'wb+') as t__f:
            t__f.write(b'Test File')
    except (PermissionError, OSError, Exception):
        return False
    else:
        os.remove(os.path.join(__dir, 'test.cc'))
        return True


# def generate_random_p_q(min_limit, max_limit):
#     primes = [i for i in range(min_limit, max_limit) if is_prime(i)]      # prime numbers in range
#     prime1, prime2 = secrets.choice(primes), secrets.choice(primes)
#     while prime1 == prime2:
#         prime2 = secrets.choice(primes)
#     return prime1, prime2

def generate_random_p_q(min_n, max_n):
    primes = [i for i in range(math.ceil(math.sqrt(min_n)), math.floor(math.sqrt(max_n))) if
              is_prime(i)]  # prime numbers in range
    p, q = secrets.choice(primes), secrets.choice(primes)
    while p == q:
        q = secrets.choice(primes)
    return p, q

def get_bit_mask(n_bytes):
    res = 0
    while n_bytes > 0:
        res = (res << 8) | 0xFF
        n_bytes -= 1

    return res


def bytes_to_int(arr: bytes) -> int:
    return int.from_bytes(arr, byteorder=sys.byteorder, signed=False)


def int_to_bytes(i: int, n_bytes: int) -> bytes:
    return i.to_bytes(n_bytes, byteorder=sys.byteorder, signed=False)


# ............................... Classes .....................

class Base:

    def __init__(self, prime1=None, prime2=None, auto_generate_primes=False, org_unit_bytes=ORG_UNIT_BYTES, enc_unit_bytes=ENC_UNIT_BYTES,
                 chunk_units=CHUNK_UNITS, text_base=':'):

        self.org_unit_bytes = org_unit_bytes
        self.enc_unit_bytes = enc_unit_bytes

        self.org_chunk_size = org_unit_bytes * chunk_units  # should be a multiple of org_unit_bytes
        self.enc_chunk_size = enc_unit_bytes * chunk_units  # should be a multiple of enc_unit_bytes

        # Primes (uninitialized)
        self.p, self.q = None, None
        self.n = None
        self.pn = None
        self.enc_keys = None
        self.primary_enc_key = None
        self.primary_dec_key = None

        # constants worth attributing
        self.text_base = text_base  # used to join encrypted data
        self.text_code = TextCode
        self.byte_code = ByteCode

        if not (prime1 and prime2) and auto_generate_primes:
            prime1, prime2 = generate_random_p_q(1 << (org_unit_bytes * 8), 1 << (enc_unit_bytes * 8))

        if prime1 and prime2:
            self.init(prime1, prime2)

    def is_initialized(self):
        return self.p and self.q

    def init(self, p, q):
        self.p, self.q = p, q
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)

        self.enc_keys = self.get_enc_keys(1)     # performance limiting
        self.primary_enc_key = self.enc_keys[0]  # first enc key
        self.primary_dec_key = self.get_dec_keys(self.primary_enc_key, 1)[0]  # first dec key of first enc key

    def get_enc_keys(self, count: int = 1) -> list:
        res = []
        if count < 1:
            return res

        for i in range(2, self.pn):
            if co_prime(i, self.n) and co_prime(i, self.pn):
                res.append(i)
                if len(res) >= count:
                    break

        return res

    def get_dec_keys(self, enc_key, count):
        res = []
        if count < 1:
            return res

        primary_dec_key = 0
        for i in range(1, self.pn * count):
            if (enc_key * i) % self.pn == 1:
                primary_dec_key = i
                break

        for j in range(count):
            res.append(primary_dec_key + (j * self.pn))
        return res


class Encryptor(Base):

    def __init__(self, prime1=None, prime2=None, org_unit_bytes=ORG_UNIT_BYTES, enc_unit_bytes=ENC_UNIT_BYTES,
                 text_base=':'):

        Base.__init__(self, prime1=prime1, prime2=prime2, auto_generate_primes=True, org_unit_bytes=org_unit_bytes, enc_unit_bytes=enc_unit_bytes, text_base=text_base)

    def encrypt_int(self, val, key) -> int:
        return exp_mod(val, key, self.n)

    def encrypt_int_default(self, val) -> int:
        return self.encrypt_int(val, self.primary_enc_key)

    def encrypt_int_arr(self, int_arr, key: int) -> map:
        return map(lambda v: self.encrypt_int(v, key), int_arr)

    def encrypt_bytes(self, byte_array: bytes, key: int = None) -> bytearray:
        if not key:
            key = self.primary_enc_key

        res = bytearray()
        for i in range(0, len(byte_array), self.org_unit_bytes):
            o = bytes_to_int(byte_array[i:i + self.org_unit_bytes])  # load original data
            e = self.encrypt_int(o, key)  # encrypt
            res.extend(int_to_bytes(e, self.enc_unit_bytes))  # dump encrypted data

        return res

    def encrypt_str(self, string, key=None) -> str:
        """
        :return: str having encrypted ascii codes of string separated by TextBase
        """
        if key is None:
            key = self.primary_enc_key
        _gen = to_unicode_arr(string)
        return self.text_base.join(str(self.encrypt_int(i, key)) for i in _gen)

    def encrypt_string_arr(self, str_arr, key=None):
        """
        seq: sequence containing strings
        :return: generator having encrypted strings
        """
        return (self.encrypt_str(i, key) for i in str_arr)


class Decryptor(Base):
    def __init__(self, prime1=None, prime2=None, org_unit_bytes=ORG_UNIT_BYTES, enc_unit_bytes=ENC_UNIT_BYTES,
                 text_base=':'):

        Base.__init__(self, prime1=prime1, prime2=prime2, auto_generate_primes=False, org_unit_bytes=org_unit_bytes,
                      enc_unit_bytes=enc_unit_bytes, text_base=text_base)

        # attrs set by set_meta_info, common to both decrypting file or batch file
        self.work_enc_key = -1  # enc key used in given meta
        self.work_dec_key = -1  # first dec key of work enc key
        self.user_pass = ''

    def decrypt_int(self, val, dec_key):
        return exp_mod(val, dec_key, self.n)

    def decrypt_int_arr(self, int_arr, dec_key: int) -> map:
        return map(lambda v: self.decrypt_int(v, dec_key), int_arr)

    def decrypt_bytes(self, byte_array: bytes, dec_key: int = None) -> bytearray:
        if not dec_key:
            dec_key = self.primary_dec_key

        res = bytearray()
        for i in range(0, len(byte_array), self.enc_unit_bytes):
            e = bytes_to_int(byte_array[i:i + self.enc_unit_bytes])  # load encrypted data
            o = self.decrypt_int(e, dec_key)  # decrypt
            res.extend(int_to_bytes(o, self.org_unit_bytes))  # dump decrypted (original) data

        return res

    @staticmethod
    def _str_to_int(_str: str):
        # to protect enc_str splitting to empty strings
        return int(_str) if _str else -1

    def decrypt_str(self, enc_str, dec_key):
        return from_unicode_arr((self.decrypt_int(i, dec_key) for i in map(self._str_to_int, enc_str.split(self.text_base)) if i != -1))

    # def decrypt_seq(self, enc_seq, dec_key):
    #     return (self.decrypt_str(i, dec_key) for i in enc_seq)


class EncBatch(Encryptor):
    """ for encrypting batch of files """

    def __init__(self, org_unit_bytes=ORG_UNIT_BYTES, enc_unit_bytes=ENC_UNIT_BYTES, chunk_units=CHUNK_UNITS,
                 text_encoding=TextEncoding, meta_base=MetaBase, meta_encoding=MetaEncoding,
                 pointer_base=PointerBase, pointer_size=PointerSize, name_base=NameBase, data_code_base=DataTypeBase, dec_code_base=DecCodeBase, pointer_dec_separator=PointerDecSeparator):

        Encryptor.__init__(self, org_unit_bytes=org_unit_bytes, enc_unit_bytes=enc_unit_bytes, text_base=TextBase)

        self.text_encoding = text_encoding

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding

        # pointer attrs
        self.pointer_base = pointer_base
        self.pointer_size = pointer_size
        # specific, includes pointers and decryption codes in form
        # \p1\p2\p3\%%<<code<<no_of_fails<<timestamp<<

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_code_base = dec_code_base  # different form pointer base
        self.pointer_dec_code_sep = pointer_dec_separator

        self.name_base = name_base  # specific
        self.data_code_base = data_code_base  # specific
        # self.file_data_base = file_data_base  # specific, added only in end of encrypted data

        self.names = []  # file names in batch, clear after every task
        self.data_codes = []  # data codes of files in batch in str form, cleared after every task
        self.pointers = []  # pointers of files in batch in str form, cleared after every task

        self.b_f_path = ''  # output batch file path
        self.o_batch_size = 0  # sum of file sizes in batch
        self.total_batch_cal_size = 0  # calibrated size of batch w.r.t to chunk size (only for calculating purposes)
        self.read_batch_size = 0  # bytes read

    def clear_cache(self):
        self.b_f_path = ''
        self.o_batch_size = 0
        self.total_batch_cal_size = 0
        self.read_batch_size = 0

        self.names.clear()
        self.data_codes.clear()
        self.pointers.clear()

    def get_meta_str(self, fd_seq, enc_key_index, pass_word, enc_key):
        for fd in fd_seq:
            _name = os.path.basename(os.path.realpath(fd.name))
            _data_code = self.text_code if is_fd_textfile(fd) else self.byte_code
            _f_size = get_file_size(fd)

            self.names.append(_name)
            self.data_codes.append(str(_data_code))
            self.o_batch_size += _f_size
            self.total_batch_cal_size += get_new_pos(_f_size, self.org_chunk_size,0)

        return f'{self.meta_base}{self.p}{self.meta_base}{self.q}{self.meta_base}{self.encrypt_int(enc_key_index, self.primary_enc_key)}' \
               f'{self.meta_base}{self.encrypt_str(self.encrypt_str(pass_word, enc_key), enc_key)}{self.meta_base}' \
               f'{self.encrypt_str(f"{self.name_base}".join(self.names), enc_key)}{self.meta_base}' \
               f'{self.encrypt_str(f"{self.data_code_base}".join(self.data_codes), enc_key)}{self.meta_base}'

    def get_meta_bytes(self, fd_seq, enc_key_index, pass_word, enc_key):
        return self.get_meta_str(fd_seq, enc_key_index, pass_word, enc_key).encode(encoding=self.meta_encoding)

    def encrypt_batch(self, fd_seq, pass_word, b_f_path=None, enc_ext=EncExt, on_prog_call=lambda *args: print(args)):
        self.clear_cache()

        # 1. encryption key
        enc_key_index = secrets.randbelow(len(self.enc_keys))
        enc_key = self.enc_keys[enc_key_index]

        # 2. meta bytes
        m_b = self.get_meta_bytes(fd_seq, enc_key_index, pass_word, enc_key)
        enc_start_pos = self.pointer_size + len(m_b) + 2  # first pointer: start of first file encrypted data

        # 3. configuring path of output batch file
        if not b_f_path:  # out batch enc file
            __dir = os.path.dirname(os.path.realpath(fd_seq[0].name))
            # __name = "_".join(os.path.splitext(i)[0][:10] for i in self.names[:5])
            __name = create_batch_file_name(__dir, self.names)
            b_f_path = os.path.join(__dir, f'{__name}{enc_ext}')

        self.b_f_path = get_non_existing_path(b_f_path)
        on_prog_call('path', self.b_f_path, 0)
        __no = len(fd_seq)  # no of files

        # 4. encrypting data
        with open(self.b_f_path, 'wb+') as b__f:
            b__f.seek(self.pointer_size, 0)
            on_prog_call('meta', self.b_f_path, 1)
            b__f.write(m_b)

            b__f.seek(enc_start_pos, 0)

            # encryption
            for count, fd in enumerate(fd_seq, start=0):
                _start_pos = b__f.tell()
                self.pointers.append(_start_pos)

                _name = os.path.basename(os.path.realpath(fd.name))

                # 3, writing encrypted data
                fd.seek(0, 0)  # sets file pos to start

                for chunk in yield_byte(fd, size=self.org_chunk_size, mutable=False):
                    enc_chunk = self.encrypt_bytes(chunk, enc_key)
                    b__f.write(enc_chunk)

                    self.read_batch_size += len(chunk)
                    on_prog_call('data', _name,  min(round((self.read_batch_size / self.o_batch_size) * 100, 2), 100))

                # b__f.write(fileDataBase)

                # if self.data_codes[count] == str(self.text_code):  # text file, no need to reed in chunks
                #     chunk = bytes(self.encrypt_str(fd.read().decode(self.text_encoding), enc_key),
                #                   encoding=self.text_encoding)  # main_cli text encryption logic
                #
                #     b__f.write(chunk)
                #     b__f.write(self.file_data_base)
                #     self.r_batch_size += get_filesize(fd)
                #     on_prog_call('data', _name, round((self.r_batch_size / self.o_batch_cal_size) * 100, 2))
                # else:
                #     for chunk in yield_byte(fd, size=self.chunk_size):
                #         chunk.reverse()  # main_cli bytes encryption logic
                #         b__f.write(chunk)
                #         self.r_batch_size += self.chunk_size
                #         on_prog_call('data', _name, round((self.r_batch_size / self.o_batch_cal_size) * 100, 2))
                #     b__f.write(self.file_data_base)

                # if count != __no - 1:
                #     cal_size = get_new_pos(b__f.tell(), self.enc_chunk_size, start=_start_pos)  # calibrating file size
                #     b__f.seek(cal_size, 0)
                #     self.pointers.append(cal_size)

            # 5. writing pointers at beginning of file
            on_prog_call('pointers', self.b_f_path, 100)
            b__f.seek(0, 0)

            # saving pointers and decryption codes
            _dec_code_str = self.dec_code_base + self.dec_code_base.join(
                ('0', '0', str(round(time.time())))) + self.dec_code_base
            _pointer_s = self.pointer_base + f"{self.pointer_base}".join(map(str, self.pointers)) + self.pointer_base
            b__f.write(bytes(_pointer_s + self.pointer_dec_code_sep + _dec_code_str, encoding=self.meta_encoding))

        read_only(self.b_f_path)  # need to be cleared before decryption


class DecBatch(Decryptor):
    def __init__(self, org_unit_bytes=ORG_UNIT_BYTES, enc_unit_bytes=ENC_UNIT_BYTES, chunk_units=CHUNK_UNITS,
                 text_encoding=TextEncoding,
                 meta_base=MetaBase, meta_encoding=MetaEncoding, pointer_base=PointerBase, pointer_size=PointerSize,
                 name_base=NameBase, data_code_base=DataTypeBase, dec_code_base=DecCodeBase, pointer_dec_separator=PointerDecSeparator):
        Decryptor.__init__(self, org_unit_bytes=org_unit_bytes, enc_unit_bytes=enc_unit_bytes, text_base=TextBase)

        self.text_encoding = text_encoding

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding

        # pointer attrs
        self.pointer_base = pointer_base
        self.pointer_size = pointer_size  # specific, includes pointers and decryption codes in form \p1\p2\p3\%%<<code<<no_of_fails<<timestamp<<
        self.dec_data_pos = 0  # position at which decryption data starts

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_code_base = dec_code_base  # different form pointer base
        self.pointer_dec_code_sep = pointer_dec_separator
        self.dec_data = [0, 0, 0]  # in form (file_lock_code, no_of_fails, timestamp)

        self.name_base = name_base  # specific
        self.data_code_base = data_code_base  # specific
        # self.file_data_base = file_data_base  # specific

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
        self.init(int(ms_array[0]), int(ms_array[1]))
        self.work_enc_key = self.enc_keys[self.decrypt_int(int(ms_array[2]), self.primary_dec_key)]
        self.work_dec_key = self.get_dec_keys(self.work_enc_key, 1)[0]

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
        self.total_batch_size = get_file_size(e_b_des)
        e_b_des.seek(0, 0)

        _header_bytes = e_b_des.read(self.pointer_size)
        _header_str = _header_bytes.decode(self.meta_encoding)
        _pointer_str, _dec_data_str = _header_str.split(self.pointer_dec_code_sep)

        sep_encoded = self.pointer_dec_code_sep.encode(self.meta_encoding)
        self.dec_data_pos = _header_bytes.index(sep_encoded) + len(sep_encoded)

        self.dec_data = list(map(int, _dec_data_str.split(self.dec_code_base)[1:-1]))  # since dec_code base is also at start and end
        self.pointers = list(map(int, _pointer_str.split(self.pointer_base)[1:-1]))  # since pointer base is also at start and end
        on_prog_call('pointer', e_b_des.name, round((self.pointer_size / self.total_batch_size) * 100, 2))
        self._next_pointers = self.pointers[1:]  # excluding 1st pointer
        self._next_pointers.append(self.total_batch_size)  # for the last pointer
        # self._next_pointers.append(get_new_pos(self.total_batch_size, chunk_size=self.enc_chunk_size, start=self.pointers[-1]))  # for last pointer

        self.set_meta_info(e_b_des.read(self.pointers[0] - self.pointer_size))
        on_prog_call('meta', e_b_des.name, round((self.pointers[0] / self.total_batch_size) * 100, 2))
        self.read_batch_size = self.pointers[0]

    def get_dec_data_bytes(self, dec_data=(0, 0, 0)):
        return bytes(
            self.dec_code_base + self.dec_code_base.join(str(round(_i)) for _i in dec_data) + self.dec_code_base,
            encoding=self.meta_encoding)

    def set_dec_data(self, e_f_des, dec_data, commit: bool = True):
        self.dec_data = dec_data

        if commit:
            __prev_pos = e_f_des.tell()
            e_f_des.seek(self.dec_data_pos, 0)
            e_f_des.write(self.get_dec_data_bytes(dec_data))
            e_f_des.seek(__prev_pos, 0)

    def update_lock_status(self, e_f_des, fail_count: int, commit: bool = True):
        fail_count = max(0, fail_count)
        if fail_count == 0:
            dec_code = DecNormal
        elif fail_count < MaxFailTries:
            dec_code = DecFailed
        else:
            dec_code = DecLocked

        regain_secs = round(AccessRegainSecsBase * math.exp(AccessRegainSecsExponent * (fail_count - 1))) if fail_count else 0
        regain_timestamp = round(time.time() + regain_secs)

        self.set_dec_data(e_f_des, (dec_code, fail_count, regain_timestamp), commit)
        return dec_code, regain_secs

    def decrypt_batch(self, e_b_des, out_dir=None, set_header=False, on_prog_call=lambda *args: print(args)):
        if set_header:
            self.set_header(e_b_des=e_b_des, on_prog_call=on_prog_call)

        _path = os.path.realpath(e_b_des.name)
        _dir, _fname = os.path.split(_path)
        _name = os.path.splitext(_fname)[0]
        if not out_dir:
            out_dir = os.path.join(_dir, _name[:10] + ' (Decrypted)')
        else:
            out_dir = os.path.join(out_dir, _name[:10] + ' (Decrypted)')

        self.out_dir = get_non_existing_path(out_dir)
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)

        e_b_des.seek(self.pointers[0], 0)

        def _handle_enc_chunk(f_name, org_file, chunk_size):
            enc_chunk = e_b_des.read(chunk_size)
            dec_chunk = self.decrypt_bytes(enc_chunk, dec_key=self.work_dec_key)
            org_file.write(dec_chunk)

            self.read_batch_size += len(enc_chunk)
            on_prog_call('data', f_name, min(round((self.read_batch_size / self.total_batch_size) * 100, 2), 100))

        # main_cli data decryption
        for _name, _d_code, _pointer, _n_pointer in zip(self.names, self.data_codes, self.pointers,
                                                        self._next_pointers):
            _f_path = get_non_existing_path(os.path.join(self.out_dir, _name))
            _r_size = _n_pointer - _pointer
            _r_iters, _r_left = divmod(_r_size, self.enc_chunk_size)

            with open(_f_path, 'wb+') as o__f:
                if _r_iters:
                    for _ in range(_r_iters):
                       _handle_enc_chunk(_name, o__f, self.enc_chunk_size)

                if _r_left:
                    _handle_enc_chunk(_name, o__f, _r_left)

                # if _d_code == self.text_code:  # text file
                #     enc_chunk = e_b_des.read(_r_size).split(self.file_data_base)[0]
                #     o__f.write(bytes(self.decrypt_str(enc_chunk.decode(self.text_encoding), self.work_dec_key), encoding=self.text_encoding))
                #
                #     self.read_batch_size += _r_size
                #     on_prog_call('data', _name, round((self.read_batch_size / self.total_batch_size) * 100, 2))
                # else:
                #     _r_iters = int(_r_size / self.chunk_size)
                #
                #     for _iter in range(0, _r_iters):
                #         enc_chunk = bytearray(e_b_des.read(self.chunk_size))
                #         if _iter == _r_iters - 1:  # last iteration
                #             enc_chunk = enc_chunk.split(self.file_data_base)[0]
                #         enc_chunk.reverse()
                #         o__f.write(enc_chunk)
                #
                #         self.read_batch_size += self.chunk_size
                #         _per = round((self.read_batch_size / self.total_batch_size) * 100, 2)
                #         on_prog_call('data', _name, _per if _per <= 100.00 else 100.00)

