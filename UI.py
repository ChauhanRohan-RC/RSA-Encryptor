
# .....................................         IMPORTS       ......................................
# Widgets
from tkinter import filedialog, messagebox, Frame, LabelFrame, Tk, Listbox, Canvas, Entry, Label, StringVar, PhotoImage
from tkwidgets import FrameAnimator, HScrollScale, VScrollScale, HoverB, HProgressBar

# Main Encryptor and Decryptor api
from crypt_api import DecBatch, EncBatch, is_writable, is_path_textfile, \
    get_non_existing_path, get_new_pos, yield_byte, read_only, clear_read_only

# Constants and resources
from __c import *
from threading import Thread
import time
import secrets
import jkkguyv523asdasd

# .............................      Constants     .........................
bg = rgb(10, 10, 10)
fg = rgb(248, 248, 248)
abg = rgb(40, 40, 40)
afg = rgb(32, 218, 255)

# Normal Buttons
b_font = ('product sans', 10)
b_relief = 'flat'
b_bd = 0
b_bg = bg
b_fg = fg
b_abg = abg
b_afg = afg
b_hoverbg = abg
b_hoverfg = afg

# Menu Buttons
menu_b_font = ("aquire", 13)
menu_b_relief = 'flat'
menu_b_bd = 0

# Title Labels
tl_font = ("product sans", 14)
tl_relief = 'flat'
tl_bd = 0

# small Labels
l_font = ("product sans", 10)
l_relief = 'flat'
l_bd = 0

# notice Labels
nl_font = ("product sans", 9)
nl_relief = 'flat'
nl_bd = 0

# Entry
e_bg = rgb(20, 20, 20)
e_fg = rgb(255, 255, 255)
e_insertbg = rgb(240, 240, 240)         # cursor color
e_font_small = ("product sans", 9)
e_font_large = ("product sans", 12)
e_relief = 'groove'
e_bd = 2

# Listbox
list_font =("product sans", 10)
list_bd = 0
list_relief = 'flat'
list_bg = rgb(20, 20, 20)
list_fg = rgb(250, 250, 250)
list_abg = abg
list_afg = afg


# ................................      Static Functions  ........................
def dummy(*args, **kwargs):
    pass


class EncFileIn(Frame):
    """
    Encryption : Files Input
    main attrs : files
    """

    def __init__(self, master, main_tk, enc_ext=C.EncExt, next_call=lambda _a='Next': print(_a),
                 back_call=lambda _a='Back': print(_a), **kwargs):
        self.master = master
        self.main_tk = main_tk
        self.enc_ext = enc_ext  # to exclude
        self.next_call, self.back_call = next_call, back_call

        self.files = []  # stores input file paths

        kwargs['bg'] = bg
        kwargs['highlightthickness'] = 0
        Frame.__init__(self, self.master, **kwargs)
        self.title_l = Label(self, bg=bg, fg=fg, relief=tl_relief, font=tl_font, bd=tl_bd,
                             text='Select files to encrypt', anchor='center')

        self.list_canvas = Canvas(self, **kwargs)

        self.y_scroll = VScrollScale(self.list_canvas, width=18, rel_height=0.8, relx=0.92, rely=0.05, slider_fill='black')
        self.x_scroll = HScrollScale(self.list_canvas, height=18, rel_width=0.85, relx=0.05, rely=0.89, slider_fill='black')
        self.listbox = Listbox(self.list_canvas, font=list_font, selectmode='single', height=2, bg=list_bg, fg=list_fg,
                               selectbackground=list_abg, selectforeground=list_afg, yscrollcommand=self.y_scroll.set,
                               xscrollcommand=self.x_scroll.set, activestyle='dotbox', highlightthickness=0,
                               relief='flat')
        self.y_scroll.set_command(self.listbox.yview)
        self.x_scroll.set_command(self.listbox.xview)

        # List Frame Placing
        self.listbox.place(x=0, y=0, relwidth=0.9, relheight=0.87)

        self.add_b = HoverB(self, text='Add', command=self.add_file, width=8, bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg,
                            hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        self.remove_b = HoverB(self, text='Remove', command=self.remove_file, width=8, bg=b_bg, fg=b_fg, abg=b_abg,
                               afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd,
                               state='disabled')

        self.clear_b = HoverB(self, text='Clear', command=self.clear_files, width=8, bg=b_bg, fg=b_fg, abg=b_abg,
                              afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd,
                              state='disabled')

        self.next_b = HoverB(self, text='Next', width=6, command=self.next_call, bg=b_bg, fg=b_fg, abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd,
                             state='disabled')

        self.back_b = HoverB(self, text='Back', width=6, command=self.back_call, bg=b_bg, fg=b_fg, abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        # main place
        self.title_l.place(relx=0, rely=0.05, relwidth=1, anchor='nw')
        self.list_canvas.place(relx=0.42, rely=0.52, relwidth=0.8, relheight=0.66, anchor='center')
        self.add_b.place(relx=.98, rely=0.3, anchor='e')
        self.remove_b.place(relx=.98, rely=0.5, anchor='e')
        self.clear_b.place(relx=.98, rely=0.7, anchor='e')

        self.next_b.place(relx=0.98, rely=0.98, anchor='se')
        self.back_b.place(relx=0.85, rely=0.98, anchor='se')

    def clear(self):
        # Clears the frame like new
        self.files.clear()
        self.listbox.delete(0, 'end')
        self.next_b['state'] = 'disabled'
        self.remove_b['state'] = 'disabled'
        self.clear_b['state'] = 'disabled'

    def init(self):
        # when came from animation
        self.add_b.focus_set()
        pass

    def add_file(self, event=None):
        _file_paths = filedialog.askopenfilenames(initialdir="C;\\", title="Select Files to encrypt",
                                                  filetypes=(('all files', '*.*'),), parent=self.main_tk)
        if _file_paths:
            for _f_path in _file_paths:
                self._add_file(_f_path)

    def _add_file(self, f_path):
        if f_path not in self.files:
            if os.path.isfile(f_path):
                if os.path.splitext(f_path)[1] == self.enc_ext:
                    logger.warning(f'File << {f_path} >> already Encrypted')
                    return
                if os.access(f_path, os.R_OK):
                    self.files.append(f_path)
                    self.listbox.insert('end', f' --> {os.path.basename(f_path)}')
                    logger.log(f'Encryption : File << {f_path} >> added to list')
                    if self.next_b['state'] == 'disabled':
                        self.next_b['state'] = 'normal'
                        self.remove_b['state'] = 'normal'
                        self.clear_b['state'] = 'normal'
                else:
                    logger.warning(f'File << {f_path} >> does not have Read Access')
            else:
                logger.warning(f'File << {f_path} >> does not exists')

    def remove_file(self, event=None):
        if self.files:
            _index = self.listbox.index('active')
            _f_path = self.files.pop(_index)
            self.listbox.delete(_index)
            logger.log(f'Encryption : File << {_f_path} >> removed from the list')
            if not self.files:
                self.next_b['state'] = 'disabled'
                self.remove_b['state'] = 'disabled'
                self.clear_b['state'] = 'disabled'

    def clear_files(self, event=None):
        self.clear()
        logger.log(f'\nEncryption : File List Cleared')


class EncUserIn(Frame):
    """
    Encryption : User Pass and output file input
    main attrs : user_pass, out_path are str vars
    """

    def __init__(self, master, main_tk, enc_ext=C.EncExt, next_call=lambda _a='Next': print(_a),
                 back_call=lambda _a='Back': print(_a), **kwargs):
        self.master = master
        self.main_tk = main_tk
        self.enc_ext = enc_ext  # for output file
        self.next_call, self.back_call = next_call, back_call

        self.user_pass = StringVar(self.main_tk, '')  # User Input PassWord
        self.out_path = StringVar(self.main_tk,
                                  os.path.join(os.getenv('UserProfile'), f'Untitled{self.enc_ext}'))  # Output File path

        kwargs['bg'] = bg
        Frame.__init__(self, self.master, **kwargs)

        self.pass_frame = LabelFrame(self, bg=bg, bd=2, text=' Choose Password ', fg=fg, font=tl_font,
                                     labelanchor='n', )
        self.path_frame = LabelFrame(self, bg=bg, bd=2, text=' Save As ', fg=fg, font=tl_font, labelanchor='n')

        self.pass_l = Label(self.pass_frame, bg=bg, fg=fg, font=l_font, text=' Password ', relief=l_relief, bd=l_bd,
                            anchor='center', width=10)
        self.conf_l = Label(self.pass_frame, bg=bg, fg=fg, font=l_font, text=' Confirm ', relief=l_relief, bd=l_bd,
                            anchor='center', width=10)
        self.pass_e = Entry(self.pass_frame, bg=e_bg, fg=e_fg, insertbackground=e_insertbg, font=e_font_small, relief=e_relief, bd=e_bd, show='*',
                            textvariable=self.user_pass)
        self.conf_e = Entry(self.pass_frame, bg=e_bg, fg=e_fg,  insertbackground=e_insertbg, font=e_font_small, relief=e_relief, bd=e_bd, show='*')

        self.pass_show_b = HoverB(self.pass_frame, image=self.main_tk.pass_hide_im, compound='center', width=30, height=26,
                                  bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg,
                                  font=b_font, relief=b_relief, bd=b_bd)

        self.conf_show_b = HoverB(self.pass_frame, image=self.main_tk.pass_hide_im,  compound='center', width=30, height=26,
                                  bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg,
                                  font=b_font, relief=b_relief, bd=b_bd)

        self.pass_check_l = Label(self.pass_frame, bg=bg, font=nl_font, text='Password Strength : Weak', fg='#FF7171',
                                  relief=nl_relief, bd=nl_bd, anchor='center')

        self.path_e = Entry(self.path_frame, bg=e_bg, fg=e_fg,  insertbackground=e_insertbg, font=e_font_small, relief=e_relief, bd=e_bd,
                            textvariable=self.out_path)
        self.browse_b = HoverB(self.path_frame, text='Browse', width=8, bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg,
                               hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd,
                               command=self.browse)

        self.next_b = HoverB(self.path_frame, text='Next', width=6, command=self._next_call, bg=b_bg, fg=b_fg,
                             abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd,
                             state='disabled')
        self.back_b = HoverB(self.path_frame, text='Back', width=6, command=self.back_call, bg=b_bg, fg=b_fg, abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        self.pass_show_b.bind('<ButtonPress-1>', self.show_pass_press)
        self.pass_show_b.bind('<ButtonRelease-1>', self.show_pass_release)
        self.conf_show_b.bind('<ButtonPress-1>', self.show_conf_press)
        self.conf_show_b.bind('<ButtonRelease-1>', self.show_conf_release)

        # pass frame placing
        self.pass_l.place(relx=0.05, rely=0.3)
        self.pass_e.place(relx=0.25, rely=0.29, relwidth=0.55)
        self.pass_check_l.place(relx=0.2, rely=0.1, relwidth=0.6)
        self.pass_show_b.place(relx=0.82, rely=0.29)
        self.conf_l.place(relx=0.05, rely=0.6)
        self.conf_e.place(relx=0.25, rely=0.59, relwidth=0.55)
        self.conf_show_b.place(relx=0.82, rely=0.59)

        # path frame placing
        self.path_e.place(relx=0.12, rely=0.28, relwidth=0.68)
        self.browse_b.place(relx=0.82, rely=0.25)
        self.next_b.place(relx=0.98, rely=0.98, anchor='se')
        self.back_b.place(relx=0.86, rely=0.98, anchor='se')

        self.pass_frame.place(x=0, y=0, relwidth=1, relheight=0.6)
        self.path_frame.place(x=0, rely=0.585, relwidth=1, relheight=0.415)

    def set_binds(self):
        # Bindings
        self.pass_e.bind('<Up>', lambda _e: self.path_e.focus_set())
        self.pass_e.bind('<Down>', lambda _e: self.conf_e.focus_set())
        self.conf_e.bind('<Up>', lambda _e: self.pass_e.focus_set())
        self.conf_e.bind('<Down>', lambda _e: self.path_e.focus_set())
        self.path_e.bind('<Up>', lambda _e: self.conf_e.focus_set())
        self.path_e.bind('<Down>', lambda _e: self.pass_e.focus_set())
        self.pass_e.bind('<Return>', self._next_call)
        self.conf_e.bind('<Return>', self._next_call)
        self.path_e.bind('<Return>', self._next_call)

    def _next_call(self, event=None):
        if self.next_b['state'] == 'normal':
            self.next_call()

    def clear(self):
        # clears frame after forgot
        self.user_pass.set("")  # User Input PassWord
        self.pass_e.delete(0, 'end')
        self.conf_e.delete(0, 'end')
        self.next_b['state'] = 'disabled'
        self.out_path.set(os.path.join(os.getenv('UserProfile'), f'Untitled{self.enc_ext}'))
        self.pass_check_l.configure(text='Password Strength : Weak', fg='#FF7171')

        self.remove_loop_func()

    def release_binds(self):
        # Release Bindings
        self.pass_e.unbind('<Up>')
        self.pass_e.unbind('<Down>')
        self.conf_e.unbind('<Up>')
        self.conf_e.unbind('<Down>')
        self.path_e.unbind('<Up>')
        self.path_e.unbind('<Down>')
        self.pass_e.unbind('<Return>')
        self.conf_e.unbind('<Return>')
        self.path_e.unbind('<Return>')

    def init(self):
        # when came from animation
        self.set_binds()
        self.main_tk.add_loop_func(self.info_check)
        self.main_tk.run_ui_loop()
        self.pass_e.focus_set()

    def remove_loop_func(self):
        self.release_binds()
        self.main_tk.remove_loop_func(self.info_check)

    def browse(self):
        out_path = filedialog.asksaveasfilename(parent=self.main_tk, initialdir="C;\\", title="Save As",
                                                filetypes=(('Encrypted File', f'*{C.EncExt}'),))
        if out_path:
            out_path += self.enc_ext
            self.out_path.set(out_path)

    def show_pass_press(self, event=None):
        self.pass_e['show'] = ''
        self.pass_show_b['image'] = self.main_tk.pass_show_im

    def show_pass_release(self, event=None):
        self.pass_e['show'] = '*'
        self.pass_show_b['image'] = self.main_tk.pass_hide_im

    def show_conf_press(self, event=None):
        self.conf_e['show'] = ''
        self.conf_show_b['image'] = self.main_tk.pass_show_im

    def show_conf_release(self, event=None):
        self.conf_e['show'] = '*'
        self.conf_show_b['image'] = self.main_tk.pass_hide_im

    @staticmethod
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

    def _disable_next(self):
        if self.next_b['state'] == 'normal':
            self.next_b['state'] = 'disabled'

    def info_check(self):
        __pass = self.user_pass.get()
        if __pass:
            _len, _u, _l, _s, _d = self._validate_pass(__pass)
            if _len < C.PassMinChars:
                self.pass_check_l.configure(fg='#FF7171', text='Password Strength : Weak')
                self._disable_next()
                return
            if not _u:
                self.pass_check_l.configure(fg='#FF7171', text='Must have a Upper Case Char')
                self._disable_next()
                return
            if not _l:
                self.pass_check_l.configure(fg='#FF7171', text='Must have a Lower Case Char')
                self._disable_next()
                return
            if not _s:
                self.pass_check_l.configure(fg='#FF7171', text='Must have a Special Char')
                self._disable_next()
                return
            if not _d:
                self.pass_check_l.configure(fg='#FF7171', text='Must have a Digit')
                self._disable_next()
                return

            if C.PassMinChars <= _len < C.PassGoodChars:
                self.pass_check_l.configure(fg='skyblue', text='Password Strength : Good')
            else:
                self.pass_check_l.configure(fg='skyblue', text='Password Strength : Strong')

            __confirm = self.conf_e.get()
            if __confirm == __pass:
                self.conf_e['fg'] = '#5CFF74'
            else:
                self.conf_e['fg'] = '#FF7171'
                self._disable_next()
                return

            __out_path = self.out_path.get()
            if not __out_path:
                self.pass_check_l.configure(fg='#FF7171', text='Specify Output Path')
                self._disable_next()
                return

            if os.path.splitext(__out_path)[1] != self.enc_ext:
                self.pass_check_l.configure(fg='#FF7171', text='Invalid Output Path')
                self._disable_next()
                return

            _dir = os.path.dirname(__out_path)
            if not os.path.isdir(_dir):
                self.pass_check_l.configure(fg='#FF7171', text='Invalid Output Directory')
                self._disable_next()
                return

            if not is_writable(_dir):
                self.pass_check_l.configure(fg='#FF7171', text='Output Dir does not have write access')
                self._disable_next()
                return

            if self.next_b['state'] == 'disabled':
                self.pass_check_l.configure(fg='skyblue', text='All Good !')
                self.next_b['state'] = 'normal'


class ProgressFrame(Frame):
    def __init__(self, master, main_tk, task='enc', cancel_call=lambda _a='Cancel': print(_a), **kwargs):
        self.master = master
        self.main_tk = main_tk
        self.cancel_call = cancel_call

        self.chars_in_fname = 50
        self.task = task  # can be 'enc' or 'dec'

        kwargs['bg'] = bg
        Frame.__init__(self, master, **kwargs)

        self.title_l = Label(self, bg=bg, fg=fg, relief=tl_relief, font=tl_font, bd=tl_bd, text='', anchor='center')
        self.main_l = Label(self, bg=bg, fg=fg, relief=l_relief, font=l_font, bd=l_bd, text='', anchor='w')
        self.progress_bar = HProgressBar(self, from_=0, to=100, value=0.00, height=20, out_width=0, highlightthickness=0)

        self.cancel_b = HoverB(self, text='Cancel', width=6, command=self._cancel_call, bg=b_bg, fg=b_fg, abg=b_abg,
                               afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        # PLACING
        self.title_l.place(relx=0, rely=0.25, relwidth=1, anchor='nw')
        self.main_l.place(relx=0.03, rely=0.45, relwidth=0.8)
        self.progress_bar.place(relx=0.03, rely=0.55, relwidth=0.94)
        self.progress_bar.set(0)

        self.cancel_b.place(relx=0.95, rely=0.95, anchor='se')

    def _cancel_call(self, event=None):
        __in = messagebox.askyesno('Confirm Cancel',
                                   f'{"Encryption" if self.task == "enc" else "Decryption"} in Progress, Are You Sure to Abort',
                                   parent=self.main_tk)
        if __in and self.cancel_call:  # check also if progress not completed , or just make cancel_call = None when progress completed
            self.cancel_call()

    def clear(self):
        self.title_l['text'] = ''
        self.main_l['text'] = ''
        self.progress_bar.set(0)
        self.main_tk.reset_quit_call()
        self.main_tk.unbind('<Escape>')

    def init(self):
        if self.task == 'enc':
            self.title_l['text'] = 'Encryption In Progress .....'
            self.main_l['text'] = ''
        else:
            self.title_l['text'] = 'Decryption In Progress .....'
            self.main_l['text'] = ''
        self.progress_bar.set(0)
        self.main_tk.set_quit_call(self._cancel_call)
        self.main_tk.bind('<Escape>', self._cancel_call)

    def set(self, what, f_name, per):
        if self.task == 'enc':
            if what == 'meta':
                self.main_l['text'] = f'Packing Meta in {format_path(f_name, self.chars_in_fname)}',
            elif what == 'pointer':
                self.main_l['text'] = f'Packing Pointers in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'data':
                self.main_l['text'] = f'Encrypting {format_path(f_name, self.chars_in_fname)}'
        else:
            if what == 'meta':
                self.main_l['text'] = f'Resolving Meta in {format_path(f_name, self.chars_in_fname)}',
            elif what == 'pointer':
                self.main_l['text'] = f'Resolving Pointers in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'data':
                self.main_l['text'] = f'Decrypting {format_path(f_name, self.chars_in_fname)}'
        self.progress_bar.set(per)


class EncUi(Frame):
    """
    Frames : 1.file_in_frame, 2.user_in_frame, 3.progress_frame
    """

    def __init__(self, master, **kwargs):
        self.master = master
        Frame.__init__(self, master, **kwargs)

        self.enc = EncBatch(text_encoding=C.TextEncoding, chunk_size=C.ChunkSize, meta_base=C.MetaBase, meta_encoding=C.MetaEncoding,
                            pointer_base=C.PointerBase, pointer_size=C.PointerSize, name_base=C.NameBase, data_code_base=C.DataTypeBase,
                            file_data_base=C.FileDataBase, dec_status_base=C.DecCodeBase, pointer_dec_separator=C.PointerDecSeparator)
        self.pause = False

        self.file_in_frame = EncFileIn(self, main_tk=self.master, next_call=self.next_file_in,
                                       back_call=self.back_file_in)
        self.user_in_frame = EncUserIn(self, main_tk=self.master, next_call=self.next_user_in,
                                       back_call=self.back_user_in)
        self.progress_frame = ProgressFrame(self, main_tk=self.master,
                                            cancel_call=self.cancel_progress)

        self.file_in_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.file_in_frame.init()

    def _encrypt_thread(self, path_seq, out_path, user_pass):
        self.enc.clear_cache()
        out_path = get_non_existing_path(out_path)
        logger.log('\nEncryption : Configuring encrypted file, Resolving Output Path << %s >>\n' % out_path)

        # 1. encryption key
        enc_key_index = secrets.randbelow(len(self.enc.enc_keys))
        enc_key = self.enc.enc_keys[enc_key_index]

        __no = len(path_seq)
        __f_sizes = []
        out_f_name = os.path.basename(out_path)

        # META DATA
        logger.log('Encryption : Configuring encrypted file, Initialising Meta encoder')
        for _path in path_seq:
            _data_code = self.enc.text_code if is_path_textfile(_path) else self.enc.byte_code
            _f_size = os.path.getsize(_path)

            __f_sizes.append(_f_size)
            self.enc.names.append(os.path.basename(_path))
            self.enc.data_codes.append(str(_data_code))
            self.enc.org_batch_size += _f_size
            self.enc.total_batch_cal_size += _f_size if _data_code == self.enc.text_code else get_new_pos(_f_size,
                                                                                                          self.enc.chunk_size,
                                                                                                          0)

        self.progress_frame.set('meta', out_f_name, 0.00)
        logger.log('Encryption : Configuring encrypted file, Meta Information collected successfully')

        meta_bytes = bytes(
            f'{self.enc.meta_base}{self.enc.p}{self.enc.meta_base}{self.enc.q}{self.enc.meta_base}{self.enc.encrypt_int(enc_key_index, self.enc.primary_enc_key)}' +
            f'{self.enc.meta_base}{self.enc.encrypt_str(self.enc.encrypt_str(user_pass, enc_key), enc_key)}{self.enc.meta_base}' +
            f'{self.enc.encrypt_str(f"{self.enc.name_base}".join(self.enc.names), enc_key)}{self.enc.meta_base}' +
            f'{self.enc.encrypt_str(f"{self.enc.data_code_base}".join(self.enc.data_codes), enc_key)}{self.enc.meta_base}',
            encoding=self.enc.meta_encoding)

        meta_b_size = sys.getsizeof(meta_bytes) - self.enc.void_byte_size
        self.enc.file_pointers.append(str(self.enc.pointer_size + meta_b_size))  # first pointer

        # 4. encrypting data
        try:
            with open(out_path, 'wb+') as b__f:
                b__f.seek(self.enc.pointer_size, 0)
                b__f.write(meta_bytes)
                logger.log('Encryption : Configuring encrypted file, Meta Data Dumped Successfully')

                # encryption
                for count, path in enumerate(path_seq, start=0):
                    if self.pause:
                        break
                    __start_pos = b__f.tell()
                    _name = self.enc.names[count]
                    _f_size = __f_sizes[count]

                    # 3, writing encrypted data
                    with open(path, 'rb') as o__f:
                        if self.enc.data_codes[count] == str(
                                self.enc.text_code):  # text file, no need to reed in chunks
                            logger.log('Encryption : Encrypting << %s >> | DATA TYPE : Text | FILE SIZE : %s Bytes' % (
                                _name, _f_size))
                            chunk = bytes(self.enc.encrypt_str(o__f.read().decode(self.enc.text_encoding), enc_key),
                                          encoding=self.enc.text_encoding)  # main_cli text encryption logic

                            b__f.write(chunk)
                            b__f.write(self.enc.file_data_base)
                            self.enc.read_batch_size += _f_size
                            self.progress_frame.set('data', _name,
                                                    (self.enc.read_batch_size / self.enc.total_batch_cal_size) * 100)
                            logger.log('Encryption : << %s >> encrypted successfully' % _name)
                        else:
                            logger.log('Encryption : Encrypting << %s >> | DATA TYPE : Bytes | FILE SIZE : %s Bytes' % (
                                _name, _f_size))
                            for chunk in yield_byte(o__f, size=self.enc.chunk_size):
                                if self.pause:
                                    break
                                chunk.reverse()  # main_cli bytes encryption logic
                                b__f.write(chunk)
                                self.enc.read_batch_size += self.enc.chunk_size
                                self.progress_frame.set('data', _name,
                                                        (self.enc.read_batch_size / self.enc.total_batch_cal_size) * 100)
                            b__f.write(self.enc.file_data_base)
                            logger.log('Encryption : << %s >> encrypted successfully' % _name)

                        if count != __no - 1 and not self.pause:
                            cal_size = get_new_pos(b__f.tell(), self.enc.chunk_size,
                                                   start=__start_pos)  # calibrating file size
                            b__f.seek(cal_size, 0)
                            self.enc.file_pointers.append(str(cal_size))

                if not self.pause:
                    # 5. writing pointers at beginning of file
                    b__f.seek(0, 0)

                    # saving pointers and decryption codes
                    _dec_code_str = self.enc.dec_status_base + self.enc.dec_status_base.join(
                        ('0', '0', str(round(time.time())))) + self.enc.dec_status_base
                    _pointer_s = self.enc.pointer_base + f"{self.enc.pointer_base}".join(
                        self.enc.file_pointers) + self.enc.pointer_base

                    b__f.write(bytes(_pointer_s + self.enc.pointer_dec_code_sep + _dec_code_str,
                                     encoding=self.enc.meta_encoding))
                    logger.log('Encryption : Dumping Pointers in Encrypted File << %s >>' % out_path)
                    self.progress_frame.set('pointer', out_f_name, 100.00)

            if not self.pause:
                self.progress_frame.cancel_call = None
                logger.log('Encryption : Locking Encrypted File << %s >>' % out_path)
                read_only(out_path)  # need to be cleared before decryption
                logger.log('\nEncryption : Successful, OUTPUT PATH : %s \n' % out_path)
                self.master.show_final_message(self, 'Encryption Successful', f'Output Encrypted File : {format_path(out_path, 50)}',
                                               title_fg="#5CFF74")
            else:
                logger.warning('Cancelled by User, Deleting temp file : %s' % out_path)
                try:
                    os.remove(out_path)
                except Exception as _del_e:
                    logger.error('Could not delete Encrypted File << %s >> Error Code : %s' % (out_path, _del_e))
                self.master.show_final_message(self, 'Encryption Failed', 'User Interruption : Cancelled by User')

        except Exception as enc_e:
            logger.error('Encryption Failed, Error Code<< %s >>' % enc_e)
            self.master.show_final_message(self, 'Encryption failed',
                                           f'Encrypted File : {format_path(out_path, 50)}\n\nError Code : {enc_e}')
        self.pause = False

    def _encrypt_init(self, path_seq, out_path, user_pass):
        self.progress_frame.cancel_call = self.cancel_progress
        logger.log(f'\n-->> Encryption : Process Started')
        __th = Thread(target=self._encrypt_thread,
                      kwargs={'path_seq': path_seq, 'out_path': out_path, 'user_pass': user_pass})
        __th.start()

    def next_file_in(self, event=None):  # Next at file input
        self.user_in_frame.init()
        first_name = get_name(self.file_in_frame.files[0], with_ext=False)

        _name = format_path((first_name + '---' + get_name(self.file_in_frame.files[-1], with_ext=False) if len(self.file_in_frame.files) > 1 else first_name) + C.EncExt, 50)
        self.user_in_frame.out_path.set(os.path.join(os.path.dirname(self.file_in_frame.files[0]), _name))
        self.master.animator.animate_left(self.file_in_frame, self.user_in_frame, relheight=1, y=0)

    def next_user_in(self, event=None):  # Next at user input
        self.user_in_frame.remove_loop_func()
        self.progress_frame.init()
        self.master.animator.animate_left(self.user_in_frame, self.progress_frame, relheight=1, y=0)
        self._encrypt_init(self.file_in_frame.files, self.user_in_frame.out_path.get(),
                           self.user_in_frame.user_pass.get())

    def back_file_in(self, event=None):  # Back at file input
        self.master.to_main_menu(self, clear=False)

    def back_user_in(self, event=None):  # Back at user input
        self.user_in_frame.remove_loop_func()
        self.file_in_frame.init()
        self.master.animator.animate_right(self.user_in_frame, self.file_in_frame, relheight=1, y=0)

    def cancel_progress(self, event=None):
        """ go back to user input frame """
        self.pause = True
        logger.by_user('Encryption Cancelled by USER .....')

    def clear(self):
        # clears all encryption frames
        self.pause = False
        self.file_in_frame.place_forget()
        self.user_in_frame.place_forget()
        self.progress_frame.place_forget()

        self.file_in_frame.clear()
        self.user_in_frame.clear()
        self.progress_frame.clear()

        self.file_in_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


class DecPassCheck(Frame):
    def __init__(self, master, main_tk, chances=C.DecChances, caption='Enter Password',
                 next_call=lambda _a='Pass Correct': print(_a), fail_call=lambda _a='Invalid Pass': print(_a),
                 unauthorized_call=lambda _a='Pass Unauthorized': print(_a),
                 back_call=lambda _a='Back at user pass': print(_a), **kwargs):
        self.master = master
        self.main_tk = main_tk
        self.next_call, self.back_call = next_call, back_call
        self.fail_call, self.unauthorized_call = fail_call, unauthorized_call
        self.cap_var = StringVar(self.main_tk, caption)
        self.correct_pass = ''

        self.chances = self.left_chances = chances

        kwargs['bg'] = bg
        Frame.__init__(self, master, **kwargs)
        self.caption_l = Label(self, bg=bg, fg=fg, relief=l_relief, font=l_font, bd=l_bd, textvariable=self.cap_var,
                               anchor='center')
        self.check_l = Label(self, bg=bg, fg=fg, relief=l_relief, font=l_font, bd=l_bd, text='', anchor='center')
        self.pass_e = Entry(self, bg=e_bg, fg=e_fg, insertbackground=e_insertbg, font=e_font_small, relief=e_relief, bd=e_bd, show='*')
        self.pass_show_b = HoverB(self, image=self.main_tk.pass_hide_im, compound='center', width=30, height=26,
                                  bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg,
                                  font=b_font, relief=b_relief, bd=b_bd)

        self.next_b = HoverB(self, text='Next', width=6, command=self.pass_check, bg=b_bg, fg=b_fg, abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)
        self.back_b = HoverB(self, text='Back', width=6, command=self._back_call, bg=b_bg, fg=b_fg, abg=b_abg,
                             afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        self.pass_show_b.bind('<ButtonPress-1>', self.show_pass_press)
        self.pass_show_b.bind('<ButtonRelease-1>', self.show_pass_release)

        self.caption_l.place(relx=0.05, rely=0.3, relwidth=0.9)
        self.pass_e.place(relx=0.2, rely=0.5, relwidth=0.6)
        self.pass_show_b.place(relx=0.82, rely=0.5)
        self.check_l.place(relx=0.1, rely=0.7, relwidth=0.8)
        self.next_b.place(relx=0.98, rely=0.98, anchor='se')
        self.back_b.place(relx=0.86, rely=0.98, anchor='se')

    def show_pass_press(self, event=None):
        self.pass_e['show'] = ''
        self.pass_show_b['image'] = self.main_tk.pass_show_im

    def show_pass_release(self, event=None):
        self.pass_e['show'] = '*'
        self.pass_show_b['image'] = self.main_tk.pass_hide_im

    def pass_check(self, event=None):
        __pass = self.pass_e.get()
        if __pass:
            if __pass == self.correct_pass:
                self.check_l.configure(fg='#5CFF74', text='Password Valid, Access Authorized')
                self.next_call()
            else:
                self.left_chances -= 1
                if self.left_chances:
                    self.check_l.configure(fg='#FF7171', text='Password Invalid, Attempts Left : %s' % self.left_chances)
                    self.fail_call()
                else:
                    self.check_l.configure(fg='#FF7171', text='Access Unauthorized : All Attempts Exhausted')
                    self.unauthorized_call()
        else:
            self.check_l.configure(fg='#FF7171', text='Enter Password first')

    def _back_call(self, event=None):
        self.back_call()

    def clear(self, reset_quit=True):
        self.cap_var.set('')
        self.correct_pass = ''
        self.check_l['text'] = ''
        self.pass_e.delete(0, 'end')
        self.pass_e.unbind('<Return>')
        self.pass_e.unbind('<Escape>')
        self.left_chances = self.chances
        if reset_quit:
            self.main_tk.reset_quit_call()

    def init(self, caption, correct_pass, left_chances=C.DecChances):
        self.main_tk.set_quit_call(self._back_call)  # quiting is same as failing
        self.cap_var.set(caption)
        self.correct_pass = correct_pass
        self.left_chances = left_chances
        self.check_l.configure(fg='skyblue', text='Decryption Attempts Allowed : %d' % left_chances)
        self.pass_e.bind('<Return>', self.pass_check)
        self.pass_e.bind('<Escape>', self._back_call)
        self.pass_e.focus_set()


class DecUI(Frame):
    def __init__(self, master, **kwargs):
        self.master = master
        self.dec = DecBatch(text_encoding=C.TextEncoding, chunk_size=C.ChunkSize, meta_base=C.MetaBase, meta_encoding=C.MetaEncoding,
                            pointer_base=C.PointerBase, pointer_size=C.PointerSize, name_base=C.NameBase, data_code_base=C.DataTypeBase,
                            file_data_base=C.FileDataBase, dec_status_base=C.DecCodeBase, pointer_dec_separator=C.PointerDecSeparator)
        self.file_path = ''
        self.pause = False

        kwargs['bg'] = bg
        Frame.__init__(self, **kwargs)
        self.pass_check_frame = DecPassCheck(self, self.master, next_call=self.next_call,
                                             unauthorized_call=self.unauthorized_call, fail_call=self.fail_call,
                                             back_call=self.back_call)
        self.progress_frame = ProgressFrame(self, self.master, task='dec', cancel_call=self.cancel_progress)

        self.pass_check_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def init(self, file_path):
        # Place it first
        self.file_path = file_path
        logger.log('\nDecryption : Process Started, INPUT FILE : << %s >>' % file_path)
        clear_read_only(file_path)
        try:
            logger.log('\nDecryption : Setting Header Data of << %s >>' % file_path)
            with open(file_path, 'rb+') as o__f:
                self.dec.set_header(o__f, on_prog_call=dummy)
            read_only(self.file_path)

            f_code, f_no, reset_time = self.dec.dec_data
            logger.log(
                f'\nDecryption : File : {file_path} || LOCK STATUS : {f_code} || Fail Attempts : {f_no} || TimeStamp : {reset_time} ||')

            if f_code == C.DecNormal:
                self.pass_check_frame.init(f'Enter Password of {format_path(file_path, 50)}', self.dec.user_pass,
                                           (C.DecChances - f_no) if f_no < C.DecChances else C.DecChances)
            elif f_code == C.DecFailed:
                if reset_time <= time.time():
                    self.pass_check_frame.init(f'Enter Password of {format_path(file_path, 50)}', self.dec.user_pass,
                                               (C.DecChances - f_no) if f_no < C.DecChances else (
                                                           C.DecChances - f_no % C.DecChances))
                else:
                    __reset_del = format_secs(round(reset_time - time.time()), out='str')
                    logger.error(f'Decryption : Access Unauthorized, Access will Reset After : {__reset_del}')
                    self.master.show_final_message(self, title=f"Access Unauthorized !",
                                                   alt=f"{format_path(file_path, 50)} is Locked\n\nTry again after {__reset_del}")

            elif f_code == C.DecLocked:
                if reset_time <= time.time():
                    if jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h:
                        self.pass_check_frame.init(
                            f'{format_path(file_path, 50)} is Locked due to Repetitive Fail Attempts\n\nEnter Expert Decryption Key to Unlock',
                            jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h, 1)
                    else:
                        logger.error(f'Fatal Error: Failed to verify Expert Decryption Key from server!!')
                        self.master.show_final_message(self, title=f"File Locked",
                                                       alt=f"{format_path(file_path, 50)} is Locked\n\nFatal Error: Expert Decryption key could not be verified from server!!")
                else:
                    __reset_del = format_secs(round(reset_time - time.time()), out='str')
                    logger.error(
                        f'Decryption : Access Unauthorized, Access will Reset After : {__reset_del}')
                    self.master.show_final_message(self, title=f"Access Unauthorized !",
                                                   alt=f"{format_path(file_path, 50)} is Locked\n\nTry again after {__reset_del}")
        except Exception as _dec_init_e:
            logger.error('\n\nIn Decryption While Setting Header Data File Path : << %s >>, Error Code : %s' % (
            file_path, _dec_init_e))
            self.master.show_final_message(self, title=f"Decrypting Failed !",
                                           alt=f"Encrypted File : {format_path(self.file_path, 50)}\n\nError Code : {_dec_init_e}")

    def dump_dec_data(self, dec_data):
        try:
            with open(self.file_path, 'rb+') as o__f:
                o__f.seek(self.dec.dec_data_pos, 0)
                o__f.write(self.dec.get_dec_data_bytes(dec_data))
        except Exception as _dec_dump_e:
            self.master.show_final_message(self, title=f"Decrypting Failed !",
                                           alt=f"Encrypted File : {format_path(self.file_path, 50)}\n\nError Code : {_dec_dump_e}")

    def back_call(self):
        self.fail_call()
        self.master.to_main_menu(self, clear=True)

    def fail_call(self):
        self.dec.dec_data[1] += 1
        if self.dec.dec_data[1] < C.DecChances:
            self.dec.dec_data[0] = C.DecNormal

            clear_read_only(self.file_path)
            self.dump_dec_data(self.dec.dec_data)
            read_only(self.file_path)
        else:
            if self.dec.dec_data[1] % C.DecChances == 0:  # in case of unauthorized fail (back press or quit call)
                self.dec.dec_data[1] -= 1
                self.unauthorized_call(show_error=False)
            else:
                clear_read_only(self.file_path)
                self.dump_dec_data(self.dec.dec_data)
                read_only(self.file_path)
        logger.warning(
            'Invalid Decryption Attempt || LOCK STATUS : %d || Fail Attempts : %d || TimeStamp : %d ||' % tuple(
                self.dec.dec_data))

    def unauthorized_call(self, show_error=True):
        self.dec.dec_data[1] += 1
        self.dec.dec_data[0] = C.DecFailed if self.dec.dec_data[1] < C.MaxFailChances * C.DecChances else C.DecLocked
        __del_reset_time = C.AccessRegainSecs * (self.dec.dec_data[1] // C.DecChances)
        __for_time = format_secs(__del_reset_time, out='str')
        self.dec.dec_data[2] = time.time() + __del_reset_time

        clear_read_only(self.file_path)
        self.dump_dec_data(self.dec.dec_data)
        read_only(self.file_path)
        logger.error(
            f'Invalid Decryption Attempt || LOCK STATUS : {self.dec.dec_data[0]} || Fail Attempts : {self.dec.dec_data[1]} || TimeStamp : {self.dec.dec_data[1]} || Access Reset Time : {__for_time} ||')

        if show_error:
            self.master.show_final_message(self,
                                           title=f"Access Unauthorized !",
                                           alt=f"{format_path(os.path.basename(self.file_path), 50)} has been Locked\n\nTry again after {__for_time}")

    def next_call(self):
        # 1. RESETTING DEC DATA
        logger.log(f'\nFile : {self.file_path} || Access : Authorized\n')
        self.dec.dec_data = [0, 0, time.time()]

        clear_read_only(self.file_path)
        self.dump_dec_data(self.dec.dec_data)

        # 2. Output dir input
        out_dir = filedialog.askdirectory(parent=self.master, initialdir="C;\\",
                                          title='Choose a directory to Decrypt Files')
        if not out_dir:
            _dir, _fname = os.path.split(self.file_path)
            __name = os.path.splitext(_fname)[0]
            out_dir = get_non_existing_path(os.path.join(_dir, format_path(__name, 30) + '(Decrypted)'))

        # 3. To Decrypt
        self.progress_frame.init()
        self.master.animator.animate_left(self.pass_check_frame, self.progress_frame,
                                          last_call=lambda _arg=False: self.pass_check_frame.clear(reset_quit=_arg),
                                          relheight=1, y=0)
        self._decrypt_init(out_dir=out_dir)

    def cancel_progress(self):
        self.pause = True
        logger.by_user(f'Decryption of << {self.file_path} >> Cancelled by User')

    def _decrypt_thread(self, out_dir):
        try:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)

            with open(self.file_path, 'rb+') as e__f:
                e__f.seek(self.dec.file_pointers[0], 0)
                self.dec.read_batch_size = self.dec.file_pointers[0]

                for _name, _d_code, _pointer, _n_pointer in zip(self.dec.org_file_names, self.dec.data_codes, self.dec.file_pointers,
                                                                self.dec._next_pointers):
                    if self.pause:
                        break
                    _f_path = get_non_existing_path(os.path.join(out_dir, _name))
                    _r_size = _n_pointer - _pointer
                    logger.log(
                        f'Decrypting File Name : {_name} || Data Type : {"Text" if _d_code == self.dec.text_code else "Bytes"}')

                    with open(_f_path, 'wb+') as o__f:
                        if _d_code == self.dec.text_code:  # text file
                            chunk = e__f.read(_r_size).split(self.dec.file_data_base)[0]
                            o__f.write(
                                bytes(self.dec.decrypt_str(chunk.decode(self.dec.text_encoding), self.dec.work_dec_key),
                                      encoding=self.dec.text_encoding))

                            self.dec.read_batch_size += _r_size
                            self.progress_frame.set('data', _name,
                                                    (self.dec.read_batch_size / self.dec.total_batch_size) * 100)
                        else:
                            _r_iters = int(_r_size / self.dec.chunk_size)
                            for _iter in range(0, _r_iters):
                                if self.pause:
                                    break
                                chunk = bytearray(e__f.read(self.dec.chunk_size))
                                if _iter == _r_iters - 1:  # last iteration
                                    chunk = chunk.split(self.dec.file_data_base)[0]
                                chunk.reverse()
                                o__f.write(chunk)

                                self.dec.read_batch_size += self.dec.chunk_size
                                self.progress_frame.set('data', _name,
                                                        (self.dec.read_batch_size / self.dec.total_batch_size) * 100)
                if not self.pause:
                    self.progress_frame.cancel_call = None
                    logger.log('\nDecryption : File %s Decrypted Successful, OUTPUT Directory : %s \n' % (
                    self.file_path, out_dir))
                    self.master.show_final_message(self, title=f"Decryption Successful !",
                                                   alt=f"Encrypted File : {format_path(os.path.basename(self.file_path), 50)}\n\nOutput Dir : {out_dir}",
                                                   title_fg='#5CFF74',
                                                   alt_fg='skyblue')

                else:
                    self.master.show_final_message(self, title=f"Decryption Failed !",
                                                   alt=f"Encrypted File : {format_path(self.file_path, 50)}\n\nError Code : User Cancelled the Operation")

            read_only(self.file_path)
        except Exception as __dec_th_e:
            logger.error('Error While Decrypting << %s >> : %s' % (self.file_path, __dec_th_e))
            read_only(self.file_path)
            self.master.show_final_message(self, title=f"Decryption failed !",
                                           alt=f"Encrypted File : {format_path(self.file_path, 50)}\n\nError Code : {__dec_th_e}")

        self.pause = False

    def _decrypt_init(self, out_dir):
        self.progress_frame.cancel_call = self.cancel_progress
        logger.log(f'\n-->> Decryption : Process Started')
        if is_writable(out_dir):
            __th = Thread(target=self._decrypt_thread, kwargs={'out_dir': out_dir})
            __th.start()
        else:
            logger.error('Decryption : Output Directory does not have write access')
            read_only(self.file_path)
            self.master.show_final_message(self, title=f"Decryption failed !",
                                           alt=f"Encrypted File : {format_path(self.file_path, 50)}\n\nError Code : Output Dir Does not have write access")

    def clear(self):
        self.file_path = ''
        self.pause = False
        self.dec.clear_cache()
        self.pass_check_frame.clear()
        self.progress_frame.clear()
        self.progress_frame.place_forget()

        self.pass_check_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


class FinishFrame(Frame):
    """ To show errors and success messages, and go back to main menu frame """

    def __init__(self, master, **kwargs):
        self.master = master

        kwargs['bg'] = bg
        Frame.__init__(self, master, **kwargs)
        self.title_l = Label(self, bg=bg, fg=fg, relief=tl_relief, font=tl_font, bd=tl_bd, text='', anchor='center')
        self.alt_l = Label(self, bg=bg, fg=fg, relief=l_relief, font=l_font, bd=l_bd, text='', anchor='center')

        self.finish_b = HoverB(self, text='Finish', width=6, command=self.to_main_menu, bg=b_bg, fg=b_fg, abg=b_abg,
                               afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg, font=b_font, relief=b_relief, bd=b_bd)

        self.title_l.place(relx=0.5, rely=0.4, anchor='center')
        self.alt_l.place(relx=0.5, rely=0.6, anchor='center')
        self.finish_b.place(relx=0.95, rely=0.95, anchor='se')

    def to_main_menu(self, event=None):
        self.finish_b.unbind('<Return>')
        self.master.to_main_menu(self)

    def show_message(self, title, alt='', title_fg=fg, alt_fg=fg):
        self.title_l.configure(fg=title_fg, text=title)
        self.alt_l.configure(fg=alt_fg, text=alt)
        self.finish_b.bind('<Return>', self.to_main_menu)
        self.finish_b.focus_set()

    def clear(self):
        self.title_l.config(fg=fg, text='')
        self.alt_l.config(fg=fg, text='')


class MainMenu(Frame):
    def __init__(self, master, enc_command, dec_command, **kwargs):
        self.master = master
        self.enc_command, self.dec_command = enc_command, dec_command

        kwargs['bg'] = bg
        Frame.__init__(self, master, **kwargs)

        # Images
        self.b_height = self.master.enc_im.height()

        # Buttons
        self.enc_b = HoverB(self, text='  Encryption  ', image=self.master.enc_im, compound='left', command=self.enc_command,
                            bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg,
                            font=menu_b_font,
                            relief=menu_b_relief, bd=menu_b_bd, height=self.b_height + 20)

        self.dec_b = HoverB(self, text='   Decryption ', image=self.master.dec_im, compound='left', command=self.dec_command,
                            bg=b_bg, fg=b_fg, abg=b_abg, afg=b_afg, hoverbg=b_hoverbg, hoverfg=b_hoverfg,
                            font=menu_b_font, relief=menu_b_relief, bd=menu_b_bd, height=self.b_height + 20)

        self.enc_b.place(relx=0.5, rely=0, anchor='n', relwidth=1, relheight=0.5)
        self.dec_b.place(relx=0.5, rely=1, anchor='s', relwidth=1, relheight=0.5)

        # self.enc_b.place(relx=0.25, rely=0.47, anchor='center', relwidth=0.46)
        # self.dec_b.place(relx=0.75, rely=0.47, anchor='center', relwidth=0.46)

    def clear(self):
        pass

    def init(self):
        pass


class UI(Tk):
    def __init__(self, size=C.UiSize, pos=(0, 0), loop_interval=C.UiLoopInterval, center=True):
        self.width, self.height = size

        self.loop_funcs = []  # functions to be executed in loop
        self.loop_running = False  # whether to loop or not
        self.loop_interval = loop_interval

        Tk.__init__(self)
        self.s_width, self.s_height = self.winfo_screenwidth(), self.winfo_screenheight()
        if center:
            self.x, self.y = round((self.s_width - self.width) / 2), round((self.s_height - self.height) / 2)
        else:
            self.x, self.y = pos
        self.wm_title(C.UiTitle)
        self['bg'] = bg
        self.wm_geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.wm_resizable(0, 0)
        self.wm_iconbitmap(ImPaths.MainIcon)
        self.set_quit_call(self._quit)  # main quit call

        # Images
        self.enc_im = PhotoImage(file=ImPaths.EncIm)
        self.dec_im = PhotoImage(file=ImPaths.DecIm)
        self.pass_show_im = PhotoImage(file=ImPaths.PassShow)
        self.pass_hide_im = PhotoImage(file=ImPaths.PassHide)

        # ...............................        Main Instances       ...........................
        self.animator = FrameAnimator(self, anm_time=C.UiFrameAnimationTime, anm_step=C.UiFrameAnimationStep)
        self.main_menu_frame = MainMenu(self, enc_command=self.anm_to_encryption, dec_command=self.force_to_decryption)
        self.enc_frame = EncUi(self)
        self.dec_frame = DecUI(self)
        self.finish_frame = FinishFrame(self)

    def anm_to_encryption(self):
        self.animator.animate_left(self.main_menu_frame, self.enc_frame, relheight=1, rely=0)

    def force_to_encryption(self, f_paths=None):
        self.enc_frame.clear()
        self.main_menu_frame.place_forget()
        self.enc_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.enc_frame.tkraise()
        if f_paths:
            for f_path in f_paths:
                self.enc_frame.file_in_frame._add_file(f_path)

    def force_to_decryption(self, enc_f_path=''):
        self.main_menu_frame.place(x=0, y=0, relheight=1, relwidth=1)
        if not enc_f_path:
            enc_f_path = filedialog.askopenfilename(initialdir="C;\\", title="Select File to Decrypt",
                                                    filetypes=(('Encrypted file', f'*{C.EncExt}'),), parent=self)
        if enc_f_path:
            if os.path.isfile(enc_f_path):
                if os.path.splitext(enc_f_path)[1] == C.EncExt:
                    self.dec_frame.clear()
                    self.dec_frame.init(enc_f_path)
                    self.main_menu_frame.place_forget()
                    self.dec_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                    self.dec_frame.tkraise()
                else:
                    self.show_final_message(self.main_menu_frame, 'File Load Error',
                                            f'{format_path(enc_f_path, 50)} : Either not Encrypted or Corrupted')
            else:
                self.show_final_message(self.main_menu_frame, 'File Load Error',
                                        f'{format_path(enc_f_path, 50)} : Either Does not Exists')

    def show_final_message(self, prev_frame, title, alt='Press Finish to go back to Main Menu', title_fg='#FF7171',
                           alt_fg='skyblue'):
        """ prev_frame is either encryption or decryption frame """
        self.finish_frame.show_message(title, alt, title_fg, alt_fg)
        self.animator.animate_left(prev_frame, self.finish_frame, last_call=prev_frame.clear, relheight=1, rely=0)

    def to_main_menu(self, prev_frame, clear=True):  # to main menu, clears previous frame
        self.animator.animate_right(prev_frame, self.main_menu_frame, last_call=prev_frame.clear if clear else None,
                                    relheight=1, rely=0)

    def ui_loop(self):
        for _func in self.loop_funcs:
            try:
                _func()
            except Exception as __main_loop_e:
                print(f'Exception in main ui loop, in function {_func.__name__} : {__main_loop_e}')
        if self.loop_running:
            self.after(self.loop_interval, self.ui_loop)

    def add_loop_func(self, func):  # add function to win loop
        if func not in self.loop_funcs:
            self.loop_funcs.append(func)

    def remove_loop_func(self, func):  # remove function from win loop
        if func in self.loop_funcs:
            self.loop_funcs.remove(func)
            if not self.loop_funcs:
                self.pause_ui_loop()

    def run_ui_loop(self):
        if not self.loop_running:
            self.loop_running = True
            self.ui_loop()

    def pause_ui_loop(self):
        self.loop_running = False

    def _quit(self):
        logger.log(f'\nQuitting : Session Ended at {time.ctime()}')
        self.quit()
        self.destroy()
        sys.exit(10)

    def set_quit_call(self, quit_call):  # mainly for progress frame
        self.wm_protocol('WM_DELETE_WINDOW', quit_call)

    def reset_quit_call(self):
        self.wm_protocol('WM_DELETE_WINDOW', self._quit)

    def by_sys(self):
        # by sys Args
        if len(sys.argv) > 1:
            if sys.argv[1] == '--d':
                self.force_to_decryption(sys.argv[2] if len(sys.argv) > 2 else '')
            else:
                self.force_to_encryption(sys.argv[1:])
        else:
            self.main_menu_frame.place(x=0, y=0, relwidth=1, relheight=1)


# .................  Main Driver Code ................
# Checking Resources
_check_code = resources_check()
if not _check_code:
    __e_win = Tk()
    __e_win.withdraw()
    messagebox.showerror('Resources Missing', 'Some of the Resources are Missing, Program is unable to launch',
                         parent=__e_win)
    __e_win.destroy()
    sys.exit()


# Logger
logger = Logger(C.log_file_path)
logger.clear()
logger.log(f'.......................  RC File Encryptor v{C.Version}............................')
logger.log(f'Session : Started at {time.ctime()}')


# MAIN WINDOW
load_ext_fonts()
win = UI(size=(530, 275))
win.by_sys()  # Loading by sys args

win.mainloop()
