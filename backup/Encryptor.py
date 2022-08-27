import os
import os.path
import secrets
from backup.filemanager import FileManager
from tkinter import *
from tkinter import filedialog, messagebox


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


def get_read_mode(fpath):
    try:
        with open(fpath, 'r') as _r_file:
            _r_file.read(10)
    except UnicodeDecodeError:
        return 'rb'
    else:
        return 'r'


# .............................Classes
class Encryptor:
    def __init__(self, prime1=None, prime2=None, min_limit=12, max_limit=40, base=' '):
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
        self.base = base  # used to concorate encrypted data

    def get_encryption_keys(self):
        encryption_keys = []
        for e__ in range(2, self.pn):
            if co_prime(e__, self.n) and co_prime(e__, self.pn):
                encryption_keys.append(e__)

        return encryption_keys

    def get_decryption_keys(self, encryption_key, no_of_keys=1):
        decryption_keys = []
        for i in range(1, no_of_keys * self.pn):
            if (encryption_key * i) % self.pn == 1:
                decryption_keys.append(i)
        return decryption_keys

    def encrypt_int(self, int_, key):
        return (int_ ** key) % self.n

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
        return meta_str, self.encrypt_string(self.encrypt_string(password_, key), key), self.encrypt_string(
            original_ext, key), self.encrypt_string(read_mode_, key)

    def encrypt_file(self, file_path_, password_, ext_='.rce', empty_pass_='``~~``'):  # depends upon Filemanager class
        file_dir_, file_fname_ = fm.dir_name(file_path_)
        file_name_, file_ext_ = fm.name_ex(file_fname_)

        fmo_ = FileManager(file_path_)

        try:
            o_data_ = fmo_.read()
            read_mode_ = 'str'
        except Exception as e:
            print(e)
            try:
                o_data_ = fmo_.rb()
                read_mode_ = 'bytes'
            except Exception as e:
                print(e)
                return -1, None, None

        e_keys_ = self.get_encryption_keys()
        e_key_ = secrets.choice(e_keys_)  # choosing a random key
        e_key_in_ = e_keys_.index(e_key_)

        if read_mode_ == 'str':
            emaindata_ = self.encrypt_string(o_data_, e_key_)
        else:
            emaindata_ = o_data_

        if password_ == '':
            password_ = empty_pass_

        e_data_ = [emaindata_, self.pack_meta(e_key_in_, password_, file_ext_, read_mode_, e_key_)]
        new_path_ = os.path.join(file_dir_, f'{file_name_}{ext_}')
        fmn_ = FileManager(new_path_)
        if fmn_.exists():
            print('encrypted file already exists')
            return 0, fmn_, e_data_
        fmn_.write_bytes(e_data_)
        fmn_.readonly()
        return 1, None, None


class Decryptor:
    def __init__(self, prime1, prime2, base=' '):
        self.p = prime1
        self.q = prime2
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)
        self.base = base  # used to concorate encrypted data

    def get_encryption_keys(self):
        encryption_keys_ = []

        for e__ in range(2, self.pn):
            if co_prime(e__, self.n) and co_prime(e__, self.pn):
                encryption_keys_.append(e__)

        return encryption_keys_

    def get_decryption_keys(self, encryption_key, no_of_keys=1):
        decryption_keys_ = []

        for i in range(1, no_of_keys * self.pn):
            if (encryption_key * i) % self.pn == 1:
                decryption_keys_.append(i)
        return decryption_keys_

    def decrypt_int(self, int_, key):
        return (int_ ** key) % self.n

    def decrypt_string(self, e_string, key):
        e_list = []
        d_list = []

        a = e_string.split(self.base)
        for i in a:
            e_list.append(int(i))

        for i in e_list:
            d_list.append(self.decrypt_int(i, key))

        return ''.join(chr(i) for i in d_list)

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

    def decrypt_file(self, file_path_, password_, empty_pass_='``~~``'):
        file_dir_, file_fname_ = fm.dir_name(file_path_)
        file_name_ = fm.name_ex(file_fname_)[0]

        fmo_ = FileManager(file_path_)
        fmo_.clearreadonly()

        e_data_ = fmo_.read_bytes()
        emaindata_ = e_data_[0]  # main_cli file data

        meta_touple_ = e_data_[-1]  # last element
        meta_str_ = meta_touple_[0]

        p_, q_, e_key_in_ = meta_str_.split(self.base)
        self.p = int(p_)
        self.q = int(q_)
        self.n = self.p * self.q
        self.pn = (self.p - 1) * (self.q - 1)
        e_key_in_ = int(e_key_in_)  # setting primes for the decryptor

        e_keys_ = self.get_encryption_keys()
        e_key_ = e_keys_[e_key_in_]
        d_key_ = self.get_decryption_keys(e_key_)[0]
        cpass_, file_ext_, read_mode_ = self.unpack_meta(meta_touple_, d_key_)

        # checking input password........
        if cpass_ == empty_pass_:
            if password_ != expert_dec_key and password_ != '':
                return -1, None, None
        else:
            if password_ != expert_dec_key and password_ != cpass_:
                return -1, None, None

        # Decryption of main_cli data.........
        if read_mode_ == 'str':
            d_data_ = self.decrypt_string(emaindata_, d_key_)
        else:
            d_data_ = emaindata_

        new_path_ = os.path.join(file_dir_, f'{file_name_}{file_ext_}')
        fmn_ = FileManager(new_path_)
        if fmn_.exists():
            print('decrypted file already exists')
            if read_mode_ == 'str':
                return 0.1, fmn_, d_data_
            return 0.2, fmn_, d_data_

        if read_mode_ == 'str':
            fmn_.write(d_data_)
        else:
            fmn_.wb(d_data_)
        return 1, None, None


class main_frame(Frame):
    def __init__(self, master, caption='Choose an action.....', **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.label = Label(self, text=caption, font='comicsans 12 bold', bg='white', relief='flat', bd=0)
        self.enc_button = Button(self, text=' Encryption ', image=encryption_image, compound=RIGHT, font='comicsans 10',
                                 relief='flat', bg='white', bd=0, activebackground=rgb((210, 210, 230)),
                                 command=self.load_forenc)
        self.dec_button = Button(self, text=' Decryption ', image=decryption_image, compound=LEFT, font='comicsans 10',
                                 relief='flat', bg='white', bd=0, activebackground=rgb((210, 210, 230)),
                                 command=self.load_fordec)

        self.label.place(x=win_width // 2, y=45, anchor='center')
        self.enc_button.place(x=20, y=100)
        self.dec_button.place(x=win_width - 120, y=100)

        self['bg'] = 'white'

    def load_forenc(self, path__=None):
        if path__ is None:
            path__ = filedialog.askopenfilename(title='Load Files to encrypt', initialdir='C;\\',
                                            filetypes=(('all files', '*'),))
        if path__:
            if os.path.isfile(path__):
                if os.path.splitext(path__)[1] != ext:
                    enc_screen.check_ = True
                    enc_screen.file_path = path__
                    enc_screen.config_status(f'File : {os.path.split(path__)[1]}')
                    enc_screen.pass_e.focus_force()
                    enc_screen.tkraise()
                else:
                    messagebox.showinfo('Error',
                                        '      File already encrypted !! \n Choose Decryption to decrypt it...')
            else:
                messagebox.showinfo('Load error', '     File does not exist or is inaccessible')

    def load_fordec(self, path__=None):
        if path__ is None:
            path__ = filedialog.askopenfilename(title='Load Files to decrypt', initialdir='C;\\',
                                            filetypes=(('encrypted file', f'*{ext}'),))
        if path__:
            if os.path.isfile(path__):
                if os.path.splitext(path__)[1] == ext:
                    dec_screen.file_path = path__
                    dec_screen.config_status(f'File : {os.path.split(path__)[1]}')
                    dec_screen.pass_e.focus_force()
                    dec_screen.tkraise()
                else:
                    messagebox.showinfo('Error',
                                        '      File is not encrypted !! \n Choose Encryption to enncrypt it...')
            else:
                messagebox.showinfo('Load error', '     File does not exist or is inaccessible')


class enc_frame(Frame):  # make check_ = True and assign a file when raising it
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.check_ = False
        self.file_path = None
        self.encryptor = Encryptor()
        self.pass_label = Label(self, text='Choose a password  ', font='comicgans 10 italic', bg='white', relief='flat')
        self.pass_e = Entry(self, show='*', width=round(win_width / 20), font='comicsans 10', bg='white', bd=3,
                            relief='groove', fg='black')

        self.confirm_label = Label(self, text='Confirm password   ', font='comicgans 10 italic', bg='white',
                                   relief='flat')
        self.confirm_e = Entry(self, show='*', width=round(win_width / 20), font='comicsans 10', bg='white', bd=3,
                               relief='groove', fg='black')

        self.show_pb = Button(self, command=lambda arg='p': self.toggle_hide(arg), image=unhide_image, bg='white',
                              relief='flat', bd=0, activebackground='white')
        self.show_cb = Button(self, command=lambda arg='c': self.toggle_hide(arg), image=unhide_image, bg='white',
                              relief='flat', bd=0, activebackground='white')

        self.status = Label(self, font='comicsans 8', text='Encrryption : ', bg=rgb((230, 230, 230)),
                            relief='groove', bd=2)
        self.progress_l = Label(self, font='comicsans 12 italic', bg='white', relief='flat', bd=0)

        self.next_b = Button(self, image=next_image, relief='flat', bg='white', activebackground='white', bd=0,
                             command=self.submit)
        self.back_b = Button(self, image=back_image, relief='flat', bg='white', activebackground='white', bd=0,
                             command=raise_main)

        self.back_b.place(x=6, y=3)
        self.pass_label.place(x=20, y=50)
        self.pass_e.place(x=150, y=50)

        self.confirm_label.place(x=25, y=90)
        self.confirm_e.place(x=150, y=90)

        self.show_pb.place(x=win_width - 60, y=50)
        self.show_cb.place(x=win_width - 60, y=90)

        self.next_b.place(x=win_width - 50, y=win_height - 40)
        self.status.place(x=0, y=win_height - 18, relwidth=1)

        self['bg'] = 'white'
        self.pass_e.bind('<Return>', self.submit)
        self.confirm_e.bind('<Return>', self.submit)
        self.check_loop()

    def toogle_widgets_state(self):
        if self.next_b['state'] == NORMAL:
            self.pass_e['state'] = DISABLED
            self.confirm_e['state'] = DISABLED
            self.show_cb['state'] = DISABLED
            self.show_pb['state'] = DISABLED
            self.back_b['state'] = DISABLED
            self.next_b['state'] = DISABLED
        else:
            self.pass_e['state'] = NORMAL
            self.confirm_e['state'] = NORMAL
            self.show_cb['state'] = NORMAL
            self.show_pb['state'] = NORMAL
            self.back_b['state'] = NORMAL
            self.next_b['state'] = NORMAL

    def submit(self, event=None):
        if self.file_path is not None:
            pass_ = self.pass_e.get()
            confirm_ = self.confirm_e.get()
            if pass_ == '':
                rein = messagebox.askyesno(title='Warning',
                                           message='Encryption without password can be risky,\n Do you want to enter password again?? ')
                if rein:
                    self.pass_e.delete(0, END)
                    self.confirm_e.delete(0, END)
                    return None, None
                else:
                    pass_ = ''
            else:
                if pass_ != confirm_:
                    messagebox.showwarning(message='password did not match, try again.....')
                    self.confirm_e.delete(0, END)
                    return None, None
            self.toogle_widgets_state()
            self.config_status(f'Encrypting file {os.path.split(self.file_path)[1]}')
            status_, fmin_, e_data_ = self.encryptor.encrypt_file(self.file_path, pass_)

            if status_ == -1:
                messagebox.showerror('Error', 'Encryption Failed , file read unauthorized')
            elif status_ == 1:
                messagebox.showinfo('Success', 'Encryption successful...')
                del_in__ = messagebox.askyesno('Delete input file', 'Do you want to delete the original encrypted file \n(recommended for best results).......')
                if del_in__:
                    os.remove(self.file_path)
            elif status_ == 0:
                in__ = messagebox.askyesno('Overwrite',
                                           'Encrypted file already exists, do you want to overwrite .....')
                if in__:
                    fmin_.write_bytes(e_data_)
                    messagebox.showinfo('Success', 'Encryption successful...')
                    del_in__ = messagebox.askyesno('Delete input file',
                                                   'Do you want to delete the original encrypted file \n(recommended for best results).......')
                    if del_in__:
                        os.remove(self.file_path)
                else:
                    messagebox.showerror('Error', 'Encryption Failed , denied by user....')

            raise_main()
            self.toogle_widgets_state()
        else:
            raise_main()

    def toggle_hide(self, entry):
        if entry == 'p':
            if self.pass_e['show'] == '*':
                self.pass_e['show'] = ''
                self.show_pb['image'] = hide_image
            else:
                self.pass_e['show'] = '*'
                self.show_pb['image'] = unhide_image
        elif entry == 'c':
            if self.confirm_e['show'] == '*':
                self.confirm_e['show'] = ''
                self.show_cb['image'] = hide_image
            else:
                self.confirm_e['show'] = '*'
                self.show_cb['image'] = unhide_image

    def check_loop(self):
        try:
            if self.check_:
                pass_ = self.pass_e.get()
                confirm_ = self.confirm_e.get()
                if confirm_ == pass_:
                    self.confirm_e['fg'] = 'green'
                else:
                    self.confirm_e['fg'] = 'red'
            self.master.after(500, self.check_loop)
        except Exception as e:
            print(e)

    def config_status(self, text):
        self.status['text'] = text[0:65] + '....'


class dec_frame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.file_path = None
        self.attempt_count = 0
        self.max_count = 3

        self.decryptor = Decryptor(3, 7)  # auto reset on loading file
        self.pass_label = Label(self, text='Enter the password  ', font='comicsans 11 italic', bg='white',
                                relief='flat', bd=0)
        self.pass_e = Entry(self, show='*', width=round(win_width / 18), font='comicsans 10', bg='white', bd=3,
                            relief='groove', fg='black')
        self.show_pb = Button(self, command=self.toggle_hide, image=unhide_image, bg='white',
                              relief='flat', bd=0, activebackground='white')

        self.next_b = Button(self, image=next_image, relief='flat', bg='white', activebackground='white', bd=0,
                             command=self.submit)
        self.back_b = Button(self, image=back_image, relief='flat', bg='white', activebackground='white', bd=0,
                             command=raise_main)
        self.status = Label(self, font='comicsans 8', text='Decryption : ', bg=rgb((230, 230, 230)),
                            relief='groove', bd=2)

        self.back_b.place(x=6, y=3)
        self.pass_label.place(x=10, y=70)
        self.pass_e.place(x=150, y=70)
        self.show_pb.place(x=win_width - 50, y=70)
        self.next_b.place(x=win_width - 50, y=win_height - 45)
        self.status.place(x=0, y=win_height - 18, relwidth=1)

        self['bg'] = 'white'
        self.pass_e.bind('<Return>', self.submit)

    def toogle_widgets_state(self):
        if self.next_b['state'] == NORMAL:
            self.pass_e['state'] = DISABLED
            self.show_pb['state'] = DISABLED
            self.back_b['state'] = DISABLED
            self.next_b['state'] = DISABLED
        else:
            self.pass_e['state'] = NORMAL
            self.show_pb['state'] = NORMAL
            self.back_b['state'] = NORMAL
            self.next_b['state'] = NORMAL

    def submit(self, event=None):
        if self.file_path is not None:
            pass_ = self.pass_e.get()

            self.toogle_widgets_state()
            status_, fmin_, d_data_ = self.decryptor.decrypt_file(self.file_path, pass_)
            self.config_status(f'decrypting file {os.path.split(self.file_path)[1]}')
            if status_ == -1:
                self.attempt_count += 1
                if self.attempt_count < self.max_count:
                    messagebox.showerror('Error',
                                         f'Decryption Failed , PASSWORD UNAUTHORIZED\n You have {self.max_count - self.attempt_count} chances left...')
                    self.toogle_widgets_state()
                    return False
                else:
                    messagebox.showerror('Error', 'Decryption Failed , PASSWORD UNAUTHORIZED\n Max attempt limit reached...try again later')

            elif status_ == 1:
                messagebox.showinfo('Success', 'Decryption successful...')
            elif status_ == 0.1:
                in__ = messagebox.askyesno('Overwrite', 'Decrypted file already exists, do you want to overwrite ....')
                if in__:
                    fmin_.log(d_data_)
                    messagebox.showinfo('Success', 'Decryption successful...')
                else:
                    messagebox.showerror('Error', 'Decryption Failed , denied by user....')

            elif status_ == 0.2:
                in__ = messagebox.askyesno('Overwrite',
                                           'Decrypted file already exists, do you want to overwrite ....')
                if in__:
                    fmin_.wb(d_data_)
                    messagebox.showinfo('Success', 'Decryption successful...')
                else:
                    messagebox.showerror('Error', 'Decryption Failed , denied by user....')

            raise_main()
            self.toogle_widgets_state()
        else:
            raise_main()

    def toggle_hide(self):
        if self.pass_e['show'] == '*':
            self.pass_e['show'] = ''
            self.show_pb['image'] = hide_image
        else:
            self.pass_e['show'] = '*'
            self.show_pb['image'] = unhide_image

    def config_status(self, text):
        self.status['text'] = text[0:65] + '....'


def raise_main():
    main_screen.tkraise()
    enc_screen.pass_e.delete(0, END)
    enc_screen.confirm_e.delete(0, END)
    dec_screen.pass_e.delete(0, END)
    dec_screen.attempt_count = 0


'''  .............DIRECTORIES  and VARS............. '''
if getattr(sys, 'frozen', False):
    main_dir = os.path.dirname(sys.executable)
else:
    main_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, 'sdk')
icons_dir = os.path.join(sdk_dir, 'icons')
# reg_dir = os.path.join(sdk_dir, 'reg')
# do_reg(reg_dir)  # checking registry status
fm = FileManager()  # main_cli filemanager.....

ext = '.rce'
version = 1.0
empty_pass = '``~~``'
# .................................................................
expert_dec_key = '9675850494'  # .............IMPORTANT............
# .................................................................
win_width, win_height = 350, 170

win = Tk()
screen_width, screen_height = win.winfo_screenwidth(), win.winfo_screenheight()
win.geometry(
    f'{win_width}x{win_height}+{round((screen_width - win_width) / 2)}+{round((screen_height - win_height) / 2)}')

# images..................................................
main_ico = os.path.join(icons_dir, 'encryption_exe.ico')
encryption_image = PhotoImage(file=os.path.join(icons_dir, "encryption_image32.png"))  # size 32 pix
decryption_image = PhotoImage(file=os.path.join(icons_dir, "decryption_image32.png"))  # size 32 pix
hide_image = PhotoImage(file=os.path.join(icons_dir, 'hide.png'))
unhide_image = PhotoImage(file=os.path.join(icons_dir, 'unhide.png'))
back_image = PhotoImage(file=os.path.join(icons_dir, 'back.png'))
next_image = PhotoImage(file=os.path.join(icons_dir, 'next.png'))
# ..............................................................
win.iconbitmap(main_ico)
win.resizable(0, 0)

dec_screen = dec_frame(win)  # decryption screen
enc_screen = enc_frame(win)  # encryption screen
main_screen = main_frame(win)  # main_cli load screen

dec_screen.place(x=0, y=0, relwidth=1, relheight=1)
enc_screen.place(x=0, y=0, relwidth=1, relheight=1)
main_screen.place(x=0, y=0, relwidth=1, relheight=1)

if len(sys.argv) <= 1:
    raise_main()
else:
    file_path = sys.argv[1]
    file_ext = fm.name_ex(file_path)[1]
    if file_ext == ext:
        main_screen.load_fordec(file_path)
    else:
        main_screen.load_forenc(file_path)


win.mainloop()
