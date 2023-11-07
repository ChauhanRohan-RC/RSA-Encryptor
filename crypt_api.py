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

"""
Structure

Encryption: original unit (ORG_UNIT_BYTES) ---> encrypted unit (ENC_UNIT_BYTES)
Decryption: encrypted unit (ENC_UNIT_BYTES) ---> original unit (ORG_UNIT_BYTES)

NOTE: encrypted unit must always be BIGGER THAN ORIGINAL UNIT to account for primes and decryption artifacts
"""

# Maximum size (in bytes) of the original data to be treated as a unit of encryption (an integer)
ORG_UNIT_BYTES = 3

# Size (in bytes) of the encrypted data that is decrypted to one original unit
ENC_UNIT_BYTES = ORG_UNIT_BYTES + 1

CHUNK_UNITS = 100  # Number of original/encrypted units in a chunk

MEM_POINTER_BYTES = 8  # Size of memory pointer in bytes

# Decryption Constants
DecNormal = 0  # no fail decryption attempts yet
DecFailed = 1  # at least 1 fail decryption attempt
DecLocked = 2  # max fail decryption attempts

DecChancesPerTry = 3  # Max decryption Chances per try
MaxFailTries = 3  # after which it get locked and can only be decrypted by expert dec key

# Access regain secs = base * exp(exponent * fail_count)
AccessRegainSecsBase = round(5)  # 5 min
AccessRegainSecsExponent = 1

# Encodings
MetaEncoding = 'utf-8'  # Meta and Pointer Data Encoding
TextEncoding = 'utf-8'  # Text File Data Encoding

# ..............................   Separators   .....................
TextBase = ':'  # joins encrypted ints in a string

# In Meta Data
MetaBase = '||'  # joins and surrounds meta data
NameBase = '#'  # joins file names in meta

# In Pointer and Decryption Data
PointerBase = '/'  # joins and surround pointers
DecStatusBase = '<<'  # joins and surround decryption data  (decryption_code, no_of_fails, timestamp)


#  ............................................ Static Functions....................................
def gcd_euclid(a, b):
    # gcd(0, b) = b; gcd(a, 0) = a, gcd(0, 0) = 0
    if a == 0:
        return b

    if b == 0:
        return a

    while b:
        a, b = b, a % b

    return a


def gcd_bitwise(a, b):
    # gcd(0, b) = b; gcd(a, 0) = a, gcd(0, 0) = 0
    if a == 0:
        return b

    if b == 0:
        return a

    # Finding K, where K is the greatest power of 2 that divides both a and b.
    k = 0

    while ((a | b) & 1) == 0:
        a = a >> 1
        b = b >> 1
        k = k + 1

    # Dividing a by 2 until a becomes odd
    while (a & 1) == 0:
        a = a >> 1

    # From here on, 'a' is always odd.
    while b != 0:

        # If b is even, remove all factor of 2 in b
        while (b & 1) == 0:
            b = b >> 1

        # Now a and b are both odd. Swap if necessary so a <= b, then set b = b - a (which is even).
        if a > b:
            a, b = b, a  # Swap a and b.

        b = b - a

    # restore common factors of 2
    return a << k


def co_prime(a, b):
    return math.gcd(a, b) == 1


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


# def is_fd_textfile(fd, chunk_size=102400, encoding='utf-8'):
#     """
#     :param fd: file descriptor opened in "rb" mode
#     :param chunk_size: bytes to read
#     :param encoding: file encoding
#     :return: True if unicode codec can decode bytes
#     """
#     _p_pos = fd.tell()  # file position to be restored later
#     __chunk = fd.read(chunk_size)
#     try:
#         __chunk.decode(encoding)
#     except (ValueError, UnicodeError, IOError):
#         return False
#     else:
#         return True
#     finally:
#         fd.seek(_p_pos, 0)  # restoring file position


# def is_path_textfile(path, chunk_size=102400, encoding='utf-8'):
#     with open(path, 'rb') as o__f:
#         try:
#             o__f.read(chunk_size).decode(encoding=encoding)
#         except (ValueError, UnicodeError, IOError):
#             return False
#         else:
#             return True


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
#     :return: alternate path which does not exist yet
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
    generates a non-existing path by Suffixing a number to an existing file/dir path

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


def create_batch_file_name(names) -> str:
    return f'{names[0]} (encrypted)'


# def get_new_pos(cur_pos, chunk_size, start=0):
#     """ to get size multiple of chunk size """
#     _size = cur_pos - start
#     _q, _r = divmod(_size, chunk_size)
#     return cur_pos if _r == 0 else (start + ((_q + 1) * chunk_size))


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


def collect_iterable(gen, max_count: int) -> list:
    res = []
    max_count = max(0, max_count)

    try:
        while max_count:
            res.append(next(gen))
            max_count -= 1
    except StopIteration:
        pass

    return res


def generate_random_p_q(min_n, max_n, max_prime_count=4):
    gen = (i for i in range(math.ceil(math.sqrt(min_n)), math.floor(math.sqrt(max_n))) if is_prime(i))
    primes = collect_iterable(gen, max_prime_count)  # prime numbers in range

    p, q = secrets.choice(primes), secrets.choice(primes)
    while p == q:
        q = secrets.choice(primes)
    return p, q


def create_bit_mask(n_bytes):
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

    def __init__(self,
                 prime1=None,
                 prime2=None,
                 auto_generate_primes=False,
                 org_unit_bytes=ORG_UNIT_BYTES,
                 enc_unit_bytes=ENC_UNIT_BYTES,
                 chunk_units=CHUNK_UNITS,
                 text_base=TextBase):

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

        self.enc_keys = self.get_enc_keys(1)  # performance limiting
        self.primary_enc_key = self.enc_keys[0]  # first enc key
        self.primary_dec_key = self.get_dec_keys(self.primary_enc_key, 1)[0]  # first dec key of first enc key

    def get_enc_keys(self, max_count: int = 1) -> list:
        gen = (i for i in range(2, self.pn) if
               co_prime(i, self.p - 1) and co_prime(i, self.q - 1) and co_prime(i, self.p) and co_prime(i, self.q))

        return collect_iterable(gen, max_count)

    def get_dec_keys(self, enc_key, max_count) -> list:
        res = []
        if max_count < 1:
            return res

        for i in range(1, self.pn * max_count):
            if (enc_key * i) % self.pn == 1:
                # i is the primary decryption key
                for j in range(max_count):
                    res.append(i + (j * self.pn))
                break

        return res


class Encryptor(Base):

    def __init__(self,
                 prime1=None,
                 prime2=None,
                 org_unit_bytes=ORG_UNIT_BYTES,
                 enc_unit_bytes=ENC_UNIT_BYTES,
                 text_base=TextBase):

        Base.__init__(self, prime1=prime1, prime2=prime2, auto_generate_primes=True, org_unit_bytes=org_unit_bytes,
                      enc_unit_bytes=enc_unit_bytes, text_base=text_base)

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
    def __init__(self,
                 prime1=None,
                 prime2=None,
                 org_unit_bytes=ORG_UNIT_BYTES,
                 enc_unit_bytes=ENC_UNIT_BYTES,
                 text_base=TextBase):

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
        return from_unicode_arr(
            (self.decrypt_int(i, dec_key) for i in map(self._str_to_int, enc_str.split(self.text_base)) if i != -1))

    # def decrypt_seq(self, enc_seq, dec_key):
    #     return (self.decrypt_str(i, dec_key) for i in enc_seq)


class EncBatch(Encryptor):
    """ for encrypting batch of files """

    def __init__(self,
                 org_unit_bytes=ORG_UNIT_BYTES,
                 enc_unit_bytes=ENC_UNIT_BYTES,
                 meta_base=MetaBase,
                 meta_encoding=MetaEncoding,
                 pointer_base=PointerBase,
                 name_base=NameBase,
                 dec_status_base=DecStatusBase):

        Encryptor.__init__(self, org_unit_bytes=org_unit_bytes, enc_unit_bytes=enc_unit_bytes, text_base=TextBase)

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding

        # pointer attrs
        self.pointer_base = pointer_base
        # specific, includes pointers and decryption codes in form
        # \p1\p2\p3\%%<<code<<no_of_fails<<timestamp<<

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_status_base = dec_status_base  # different form pointer base

        self.name_base = name_base  # specific
        # self.data_code_base = data_code_base  # specific
        # self.file_data_base = file_data_base  # specific, added only in end of encrypted data

        # self.data_codes = []  # data codes of files in batch in str form, cleared after every task
        self.file_pointers = []  # pointers of files in batch in str form, cleared after every task

        self.b_f_path = ''  # output batch file path
        self.org_batch_size = 0  # sum of file sizes in batch
        # self.total_batch_cal_size = 0  # calibrated size of batch w.r.t to chunk size (only for calculating purposes)
        self.read_batch_size = 0  # bytes read

    def clear_cache(self):
        self.b_f_path = ''
        self.org_batch_size = 0
        # self.total_batch_cal_size = 0
        self.read_batch_size = 0

        # self.data_codes.clear()
        self.file_pointers.clear()

    def get_meta_str(self, file_names, enc_key_index, pass_word, enc_key):
        main = self.meta_base.join((
            str(self.p),
            str(self.q),
            str(self.encrypt_int(enc_key_index, self.primary_enc_key)),
            self.encrypt_str(self.encrypt_str(pass_word, enc_key), enc_key),
            self.encrypt_str(self.name_base.join(file_names), enc_key)
        ))

        return self.meta_base + main + self.meta_base

    def encrypt_batch(self, fd_seq, pass_word, b_f_path=None, enc_ext=EncExt, on_prog_call=lambda *args: print(args)):
        self.clear_cache()

        # 1. encryption key
        enc_key_index = secrets.randbelow(len(self.enc_keys))
        enc_key = self.enc_keys[enc_key_index]

        file_names = []
        for fd in fd_seq:
            _f_name = os.path.basename(os.path.realpath(fd.name))
            _f_size = get_file_size(fd)

            file_names.append(_f_name)
            self.org_batch_size += _f_size

        # 2. configuring path of output batch file
        if not b_f_path:  # out batch enc file
            __dir = os.path.dirname(os.path.realpath(fd_seq[0].name))
            # __name = "_".join(os.path.splitext(i)[0][:10] for i in self.names[:5])
            __name = create_batch_file_name(file_names)
            b_f_path = os.path.join(__dir, f'{__name}{enc_ext}')

        self.b_f_path = get_non_existing_path(b_f_path)
        on_prog_call('path', self.b_f_path, 0)
        __no = len(fd_seq)  # no of files

        # leaving space for the pointers to meta, file_pointers and dec_status_data
        enc_start_pos = MEM_POINTER_BYTES * 3

        with open(self.b_f_path, 'wb+') as e_f_des:
            e_f_des.seek(enc_start_pos, 0)

            # 3. encrypting files
            for count, fd in enumerate(fd_seq, start=0):
                self.file_pointers.append(e_f_des.tell())

                _f_name = os.path.basename(os.path.realpath(fd.name))

                # 3, writing encrypted data
                fd.seek(0, 0)  # sets file pos to start

                for chunk in yield_byte(fd, size=self.org_chunk_size, mutable=False):
                    enc_chunk = self.encrypt_bytes(chunk, enc_key)
                    e_f_des.write(enc_chunk)

                    self.read_batch_size += len(chunk)
                    on_prog_call('data',
                                 _f_name,
                                 min(round((self.read_batch_size / self.org_batch_size) * 100, 2), 100))

            # 4. writing meta information
            pos_meta_start = e_f_des.tell()
            self.file_pointers.append(pos_meta_start)  # end of last file enc data

            on_prog_call('meta', self.b_f_path, 1)
            meta_str = self.get_meta_str(file_names, enc_key_index, pass_word, enc_key)
            meta_bytes = meta_str.encode(self.meta_encoding)
            e_f_des.write(meta_bytes)

            # 4. writing pointers
            pos_pointers_start = e_f_des.tell()

            on_prog_call('pointers', self.b_f_path, 100)
            file_pointers_str = self.pointer_base + f"{self.pointer_base}".join(
                map(str, self.file_pointers)) + self.pointer_base
            file_pointers_bytes = file_pointers_str.encode(self.meta_encoding)
            e_f_des.write(file_pointers_bytes)

            # 5. Writing decryption status data
            pos_dec_status_start = e_f_des.tell()
            dec_status_str = self.dec_status_base + self.dec_status_base.join(
                map(str, (0, 0, round(time.time())))) + self.dec_status_base

            dec_status_bytes = dec_status_str.encode(self.meta_encoding)
            e_f_des.write(dec_status_bytes)

            # 6. Writing header memory pointers at start
            e_f_des.seek(0, 0)
            e_f_des.write(int_to_bytes(pos_meta_start, MEM_POINTER_BYTES))
            e_f_des.write(int_to_bytes(pos_pointers_start, MEM_POINTER_BYTES))
            e_f_des.write(int_to_bytes(pos_dec_status_start, MEM_POINTER_BYTES))

        read_only(self.b_f_path)  # need to be cleared before decryption


class DecBatch(Decryptor):
    def __init__(self,
                 org_unit_bytes=ORG_UNIT_BYTES,
                 enc_unit_bytes=ENC_UNIT_BYTES,
                 meta_base=MetaBase,
                 meta_encoding=MetaEncoding,
                 pointer_base=PointerBase,
                 name_base=NameBase,
                 dec_status_base=DecStatusBase):

        Decryptor.__init__(self, org_unit_bytes=org_unit_bytes, enc_unit_bytes=enc_unit_bytes, text_base=TextBase)

        # meta attrs
        self.meta_base = meta_base
        self.meta_encoding = meta_encoding
        self.name_base = name_base  # specific
        self.pointer_base = pointer_base

        # dec code constants, decryption code is in form <<code<<no_of_fails<<timestamp<<
        self.dec_status_base = dec_status_base  # different form pointer base
        self.dec_data = [0, 0, 0]  # in form (file_lock_code, no_of_fails, timestamp)

        self.org_file_names = []  # file names in batch, clear after every task
        self.head_pointers = [0, 0, 0]  # pointers to the start of meta, file_pointers and dec_status
        self.file_pointers = []  # pointers of files in batch in int form, cleared after every task

        self.out_dir = ''  # output directory
        self.batch_file_count = 0  # no of files in batch
        self.total_batch_size = 0  # file size of encrypted_batch file
        self.read_batch_size = 0  # bytes read

    @property
    def meta_data_pos(self):
        return self.head_pointers[0]

    @property
    def file_pointers_data_pos(self):
        return self.head_pointers[1]

    @property
    def dec_status_data_pos(self):
        return self.head_pointers[2]

    def clear_cache(self):
        self.dec_data = [0, 0, 0]
        self.org_file_names.clear()  # file names in batch, clear after every task
        self.head_pointers = [0, 0, 0]  # pointers to the start of meta, file_pointers and dec_status
        self.file_pointers.clear()  # pointers of files in batch in int form, cleared after every task

        self.out_dir = ''
        self.batch_file_count = 0  # no of files in batch
        self.total_batch_size = 0  # file size of encrypted_batch file
        self.read_batch_size = 0  # bytes read

    def set_meta_info(self, meta_bytes):
        meta_str = meta_bytes.decode(self.meta_encoding)
        ms_array = meta_str.split(self.meta_base)[1:-1]

        # main_cli info
        self.init(int(ms_array[0]), int(ms_array[1]))
        self.work_enc_key = self.enc_keys[self.decrypt_int(int(ms_array[2]), self.primary_dec_key)]
        self.work_dec_key = self.get_dec_keys(self.work_enc_key, 1)[0]

        # user pass word
        self.user_pass = self.decrypt_str(self.decrypt_str(ms_array[3], self.work_dec_key), self.work_dec_key)

        # name of files in batch
        self.org_file_names = self.decrypt_str(ms_array[4], self.work_dec_key).split(self.name_base)
        self.batch_file_count = len(self.org_file_names)

    def set_header(self, e_b_des, on_prog_call=lambda *args: print(args)):
        """
        :param e_b_des: encrypted batch file descriptor object in rb mode
        :param on_prog_call: call for progress
        sets meta info and pointers, also sets file position to first pointer
        """
        self.clear_cache()
        self.total_batch_size = get_file_size(e_b_des)

        # 1. Read head pointers from file
        e_b_des.seek(0, 0)
        meta_start = bytes_to_int(e_b_des.read(MEM_POINTER_BYTES))
        file_pointers_start = bytes_to_int(e_b_des.read(MEM_POINTER_BYTES))
        dec_status_start = bytes_to_int(e_b_des.read(MEM_POINTER_BYTES))
        self.head_pointers = [meta_start, file_pointers_start, dec_status_start]
        self.read_batch_size += MEM_POINTER_BYTES * 3

        # 2. Read meta information
        meta_size = file_pointers_start - meta_start
        on_prog_call('meta', e_b_des.name, round((self.read_batch_size / self.total_batch_size) * 100, 2))

        e_b_des.seek(meta_start, 0)
        meta_bytes = e_b_des.read(meta_size)
        self.set_meta_info(meta_bytes)
        self.read_batch_size += meta_size

        # 3. Read file pointers
        file_pointers_size = dec_status_start - file_pointers_start
        on_prog_call('pointer', e_b_des.name, round((self.read_batch_size / self.total_batch_size) * 100, 2))

        e_b_des.seek(file_pointers_start, 0)
        file_pointers_bytes = e_b_des.read(file_pointers_size)
        file_pointers_str = file_pointers_bytes.decode(self.meta_encoding)
        self.file_pointers = list(
            map(int, file_pointers_str.split(self.pointer_base)[1:-1]))  # since pointer base is also at start and end
        self.read_batch_size += file_pointers_size

        # 4. Read decryption status data
        dec_status_size = self.total_batch_size - dec_status_start
        e_b_des.seek(dec_status_start, 0)
        dec_status_bytes = e_b_des.read(dec_status_size)
        dec_status_str = dec_status_bytes.decode(self.meta_encoding)
        self.dec_data = list(
            map(int,
                dec_status_str.split(self.dec_status_base)[1:-1]))  # since dec_status base is also at start and end
        self.read_batch_size += dec_status_size

    def get_dec_data_bytes(self, dec_data=(0, 0, 0)):
        return bytes(
            self.dec_status_base + self.dec_status_base.join(str(round(_i)) for _i in dec_data) + self.dec_status_base,
            encoding=self.meta_encoding)

    def set_dec_data(self, e_f_des, dec_data, commit: bool = True):
        self.dec_data = dec_data

        if commit:
            __prev_pos = e_f_des.tell()
            e_f_des.seek(self.dec_status_data_pos, 0)
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

        regain_secs = round(
            AccessRegainSecsBase * math.exp(AccessRegainSecsExponent * (fail_count - 1))) if fail_count else 0
        regain_timestamp = round(time.time() + regain_secs)

        self.set_dec_data(e_f_des, (dec_code, fail_count, regain_timestamp), commit)
        return dec_code, regain_secs

    def decrypt_batch(self, e_b_des, out_dir=None, set_header=False, on_prog_call=lambda *args: print(args)):
        if set_header:
            self.set_header(e_b_des=e_b_des, on_prog_call=on_prog_call)

        enc_file_path = os.path.realpath(e_b_des.name)
        enc_file_dir, enc_file_name = os.path.split(enc_file_path)
        enc_file_name_no_ext = os.path.splitext(enc_file_name)[0]
        if not out_dir:
            out_dir = os.path.join(enc_file_dir, enc_file_name_no_ext[:10] + ' (Decrypted)')
        else:
            out_dir = os.path.join(out_dir, enc_file_name_no_ext[:10] + ' (Decrypted)')

        self.out_dir = get_non_existing_path(out_dir)
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)

        def _handle_enc_chunk(_org_file_name, _org_file_des, _chunk_size):
            enc_chunk = e_b_des.read(_chunk_size)
            dec_chunk = self.decrypt_bytes(enc_chunk, dec_key=self.work_dec_key)
            _org_file_des.write(dec_chunk)

            self.read_batch_size += len(enc_chunk)
            on_prog_call('data', _org_file_name,
                         min(round((self.read_batch_size / self.total_batch_size) * 100, 2), 100))

        # main_cli data decryption
        for i, org_f_name in enumerate(self.org_file_names, start=0):
            out_file_path = get_non_existing_path(os.path.join(self.out_dir, org_f_name))

            org_file_enc_size = self.file_pointers[i + 1] - self.file_pointers[i]
            iters, left_bytes = divmod(org_file_enc_size, self.enc_chunk_size)

            e_b_des.seek(self.file_pointers[i], 0)
            with open(out_file_path, 'wb+') as org_f_des:
                if iters:
                    for _ in range(iters):
                        _handle_enc_chunk(org_f_name, org_f_des, self.enc_chunk_size)

                if left_bytes:
                    _handle_enc_chunk(org_f_name, org_f_des, left_bytes)
