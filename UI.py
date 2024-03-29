import os.path
# .....................................         IMPORTS       ......................................
# Widgets
import time
from threading import Thread
from tkinter import filedialog, messagebox, Frame, LabelFrame, Tk, Listbox, Canvas, Entry, Label, StringVar, PhotoImage

# Constants and resources
from __c import *

# Main Encryptor and Decryptor api
from crypt_api import *
from tkwidgets import FrameAnimator, HScrollScale, VScrollScale, HoverB, HProgressBar

# .............................      Constants     .........................
bg = rgb(10, 10, 10)
fg = rgb(248, 248, 248)
abg = rgb(40, 40, 40)
afg = rgb(32, 218, 255)

# Normal Buttons
b_font = ('product sans', 10)
b_relief = "flat"
b_bd = 0
b_bg = bg
b_fg = fg
b_abg = abg
b_afg = afg
b_hoverbg = abg
b_hoverfg = afg

# Menu Buttons
menu_b_font = ("aquire", 13)
menu_b_relief = "flat"
menu_b_bd = 0

# Title Labels
tl_font = ("product sans", 14)
tl_relief = "flat"
tl_bd = 0

# small Labels
l_font = ("product sans", 10)
l_relief = "flat"
l_bd = 0

# notice Labels
nl_font = ("product sans", 9)
nl_relief = "flat"
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
        self.out_path = StringVar(self.main_tk, generate_enc_batch_file_path(None, non_existing=True))  # Output File path

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
        self.out_path.set(generate_enc_batch_file_path(None, non_existing=True))
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
        _pass = self.user_pass.get()
        if _pass:
            _len, _u, _l, _s, _d = self._validate_pass(_pass)
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
            if __confirm == _pass:
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
                self.pass_check_l.configure(fg='#FF7171', text='Invalid Output File Type')
                self._disable_next()
                return

            _dir = os.path.dirname(__out_path)
            if not os.path.isdir(_dir):
                self.pass_check_l.configure(fg='#FF7171', text='Invalid Output Directory')
                self._disable_next()
                return

            if not is_dir_writable(_dir):
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

    def on_progress(self, what, f_name, percentage):
        msg_short = None
        msg_long = None

        if self.task == 'enc':
            if what == 'path':
                msg_short = 'Creating Encrypted File...'
                msg_long = f'Creating a new encrypted file: {f_name}',
            elif what == 'meta':
                msg_short = 'Encrypting Meta Data...'
                msg_long = f'Encrypting Meta Data in {format_path(f_name, self.chars_in_fname)}',
            elif what == 'pointer':
                msg_short = 'Encrypting Pointers...'
                msg_long = f'Encrypting Pointers in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'dec_status':
                msg_short = 'Validating Integrity...'
                msg_long = f'Validating Encryption Integrity in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'data':
                msg_short = f'Encrypting {format_path(os.path.basename(f_name), self.chars_in_fname)}'
                msg_long = f'Encrypting {f_name}'
        else:
            if what == 'meta':
                msg_short = 'Resolving Meta Data...'
                msg_long = f'Resolving Meta Data in {format_path(f_name, self.chars_in_fname)}',
            elif what == 'pointer':
                msg_short = 'Resolving Pointers...'
                msg_long = f'Resolving Pointers in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'dec_status':
                msg_short = 'verifying Integrity...'
                msg_long = f'Verifying Encryption Integrity in {format_path(f_name, self.chars_in_fname)}'
            elif what == 'data':
                msg_short = f'Decrypting {format_path(os.path.basename(f_name), self.chars_in_fname)}'
                msg_long = f'Decrypting {f_name}'

        self.progress_bar.set(percentage)
        if msg_short:
            self.main_l['text'] = msg_short

        if msg_long:
            logger.log(f'{"Encryption" if self.task == "enc" else "Decryption"} : {msg_long}')


class EncUi(Frame):
    """
    Frames : 1.file_in_frame, 2.user_in_frame, 3.progress_frame
    """

    def __init__(self, master, **kwargs):
        self.master = master
        Frame.__init__(self, master, **kwargs)

        self.pause = False

        self.file_in_frame = EncFileIn(self, main_tk=self.master, next_call=self.next_file_in,
                                       back_call=self.back_file_in)
        self.user_in_frame = EncUserIn(self, main_tk=self.master, next_call=self.next_user_in,
                                       back_call=self.back_user_in)
        self.progress_frame = ProgressFrame(self, main_tk=self.master,
                                            cancel_call=self.cancel_progress)

        self.file_in_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.file_in_frame.init()

    def is_cancelled(self):
        return self.pause

    def cancel_progress(self, event=None):
        """ go back to user input frame """
        self.pause = True
        logger.by_user('Encryption Cancelled by USER .....')

    def _encrypt_thread(self, path_seq, out_path, user_pass):
        logger.log('\nEncryption : Configuring encrypted file, Resolving Output Path << %s >>\n' % out_path)

        fd_seq = [open(p, 'rb') for p in path_seq]
        enc = EncBatch()

        try:
            done = enc.encrypt_batch(fd_seq=fd_seq,
                              pass_word=user_pass,
                              out_batch_file_path=out_path,
                              on_prog_callback=self.progress_frame.on_progress,
                              cancellation_provider=self.is_cancelled)

            if done:
                self.master.show_final_message(self, 'Encryption Successful',
                                               f'Encrypted File : {get_name(enc.b_f_path, True)}',
                                               title_fg="#5CFF74")
            elif self.is_cancelled():
                logger.warning('Encryption cancelled by User, Deleting temp file : %s' % get_name(enc.b_f_path, True))
                try:
                    os.remove(out_path)
                except Exception as _del_e:
                    logger.error('Could not delete Encrypted File << %s >> Error Code : %s' % (get_name(enc.b_f_path, True), _del_e), _del_e)
                finally:
                    self.master.show_final_message(self, 'Encryption Cancelled', 'User Interruption: Cancelled by User')

        except Exception as enc_exc:
            logger.error('Encryption Failed, Error Code << %s >>' % enc_exc, enc_exc)
            self.master.show_final_message(self, 'Encryption failed',
                                           f'Encrypted File : {get_name(enc.b_f_path, True)}\n\nError Code : {enc_exc}')
        finally:
            for fd in fd_seq:
                fd.close()

            self.pause = False

    def _encrypt_init(self, path_seq, out_path, user_pass):
        self.pause = False
        self.progress_frame.cancel_call = self.cancel_progress
        logger.log(f'\n-->> Encryption : Process Started')
        __th = Thread(target=self._encrypt_thread,
                      kwargs={'path_seq': path_seq, 'out_path': out_path, 'user_pass': user_pass})
        __th.start()

    def next_file_in(self, event=None):  # Next at file input
        self.user_in_frame.init()
        self.user_in_frame.out_path.set(generate_enc_batch_file_path(self.file_in_frame.files, non_existing=True))

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
    def __init__(self, master, main_tk, chances=DecChancesPerTry, caption='Enter Password',
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
                    self.fail_call(self.left_chances)
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

    def init(self, caption, correct_pass, left_chances=DecChancesPerTry):
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
        self.dec = DecBatch()
        self.file_path = ''
        self.pause = False

        kwargs['bg'] = bg
        Frame.__init__(self, **kwargs)
        self.pass_check_frame = DecPassCheck(self, self.master,
                                             next_call=self.next_call,
                                             unauthorized_call=self.unauthorized_call,
                                             fail_call=self.fail_call,
                                             back_call=self.back_call)

        self.progress_frame = ProgressFrame(self, self.master, task='dec', cancel_call=self.cancel_progress)
        self.progress_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def is_cancelled(self):
        return self.pause

    def cancel_progress(self):
        self.pause = True
        logger.by_user(f'Decryption of << {self.file_path} >> Cancelled by User')


    def _init_thread(self):
        clear_read_only(self.file_path)

        try:
            with open(self.file_path, 'rb+') as e_f_des:
                self.dec.set_header(e_f_des, on_prog_call=self.progress_frame.on_progress)

                # checking blacklist status
                dec_code, fail_count, regain_timestamp = self.dec.dec_data
                regain_secs = round(regain_timestamp - time.time())
                logger.log(
                    f'\nDecryption : File : {self.file_path} | LOCK STATUS : {dec_code} | Failed Attempts : {fail_count} | Access Regain TimeStamp : {regain_timestamp}')

                if dec_code in (DecFailed, DecLocked) and regain_secs > 0:
                    regain_sec_str = format_secs(regain_secs, out='str')
                    logger.error(f'Decryption: Access Unauthorized. Try again after : {regain_sec_str}')
                    self.master.show_final_message(self, title=f"Access Unauthorized",
                                                   alt=f"{get_name(self.file_path, True)} is Locked\n\nTry again after {regain_sec_str}")

                elif dec_code in (DecNormal, DecFailed):
                    self.pass_check_frame.init(f'Enter Password of {get_name(self.file_path, False)}',
                                               self.dec.user_pass)
                    self.master.animator.animate_left(self.progress_frame, self.pass_check_frame,
                                                      last_call=self.progress_frame.clear,
                                                      relheight=1, y=0)
                elif dec_code == DecLocked:
                    # if file is locked
                    logger.warning(f"\n-->> Decryption: File << {self.file_path} >> is LOCKED\n")
                    logger.log('-> Connecting to server for expert decryption verification...')

                    import jkkguyv523asdasd

                    if jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h:
                        self.pass_check_frame.init(
                            f'{get_name(self.file_path, True)} is Locked due to Repetitive Failed Attempts\n\nEnter Expert Decryption Key to Unlock',
                            jkkguyv523asdasd.dfhds72346nh3434hsd34gsdf23h, 1)
                        self.master.animator.animate_left(self.progress_frame, self.pass_check_frame,
                                                          last_call=self.progress_frame.clear,
                                                          relheight=1, y=0)
                    else:
                        logger.error(f'-> Decryption: FATAL ERROR: Failed to verify Expert Decryption Key from server')
                        self.master.show_final_message(self, title=f"File Locked",
                                                       alt=f"{get_name(self.file_path, True)} is Locked\n\nFatal Error: Expert Decryption key could not be verified from server!!")
        except Exception as init_exc:
            logger.error(
                f'Decryption: Exception while initializing decryptor for file << {self.file_path} >>, Error Code : {init_exc}',
                init_exc)
            self.master.show_final_message(self, title=f"Decrypting Failed",
                                           alt=f"Encrypted File : {get_name(self.file_path, True)}\n\nError Code : {init_exc}\nSee Logs for details")
        finally:
            read_only(self.file_path)


    def init(self, file_path):
        # Place it first

        if not os.path.isfile(file_path):
            logger.error(f'Decryption : File << {file_path} >> does not exist')
            self.master.show_final_message(self, title=f"File not found",
                                           alt=f"{get_name(self.file_path, True)} does not exist!")
            return False

        if not os.path.splitext(file_path)[1] == EncExt:
            logger.error(f'Decryption : File << {file_path} >> is not encrypted')
            self.master.show_final_message(self, title=f"Invalid File",
                                           alt=f"{get_name(self.file_path, True)} is not encrypted")
            return False

        self.file_path = file_path
        logger.log(f'\nDecryption : Process Started, ENCRYPTED FILE : << {file_path} >>')
        th = Thread(target=self._init_thread)
        th.start()

    def commit_dec_data_internal(self) -> bool:
        try:
            self.dec.commit_dec_data_to_path(self.file_path, handle_read_only=True)
            return True
        except Exception as exc:
            logger.error(f"Decryption: Exception while writing decryption status data to file << {self.file_path} >> | Error: {exc}", exc)
            self.master.show_final_message(self, title=f"Decrypting Failed",
                                           alt=f"Encrypted File : {get_name(self.file_path, True)}\n\nError Code : {exc}")
            return False

    def back_call(self):
        # self.fail_call()
        self.master.to_main_menu(self, clear=True)

    def fail_call(self, chances_left):
        logger.warning(f'\n-> Access Unauthorized. Chances Left: {chances_left}')

        # if not self.commit_dec_data_internal():
        #     return False
        #
        # if dec_code == DecFailed and regain_secs > 0:
        #     self.master.show_final_message(self,
        #                                    title=f"Access Unauthorized",
        #                                    alt=f"Too many failed attempts!\n\nTry again after {format_secs(regain_secs, 'str')}")
        #
        # elif dec_code == DecLocked:
        #     self.master.show_final_message(self,
        #                                    title=f"Access Frozen",
        #                                    alt=f"{format_path(os.path.basename(self.file_path), 50)} has been Locked. Expert Decryption Key is required to regain access")
        # else:
        #     return True
        #
        # return False


        # if self.dec.dec_data[1] < C.DecChances:
        #     self.dec.dec_data[0] = C.DecNormal
        #
        #     clear_read_only(self.file_path)
        #     self.dump_dec_data(self.dec.dec_data)
        #     read_only(self.file_path)
        # else:
        #     if self.dec.dec_data[1] % C.DecChances == 0:  # in case of unauthorized fail (back press or quit call)
        #         self.dec.dec_data[1] -= 1
        #         self.unauthorized_call(show_error=False)
        #     else:
        #         clear_read_only(self.file_path)
        #         self.dump_dec_data(self.dec.dec_data)
        #         read_only(self.file_path)

    def unauthorized_call(self):
        dec_code, fail_tries, regain_secs = self.dec.increment_lock_status(None, 1, False)
        regain_secs_str = format_secs(regain_secs, out='str')

        logger.warning(f'\n-> Access Unauthorized | Lock Status : {dec_code} | Failed Attempts : {fail_tries * DecChancesPerTry}' + (
            f" | Try again after {regain_secs_str}" if regain_secs > 0 else ''))

        if not self.commit_dec_data_internal():
            return

        if dec_code == DecFailed and regain_secs > 0:
            self.master.show_final_message(self,
                                           title=f"Access Unauthorized",
                                           alt=f"Too many failed attempts!\n\nTry again after {regain_secs_str}")

        elif dec_code == DecLocked:
            self.master.show_final_message(self,
                                           title=f"Access Frozen",
                                           alt=f"{get_name(self.file_path, True)} has been Locked.\nExpert Decryption Key is required to regain access")


        # self.dec.dec_data[0] = C.DecFailed if self.dec.dec_data[1] < C.MaxFailChances * C.DecChances else C.DecLocked
        # __del_reset_time = C.AccessRegainSecs * (self.dec.dec_data[1] // C.DecChances)
        # __for_time = format_secs(__del_reset_time, out='str')
        # self.dec.dec_data[2] = time.time() + __del_reset_time
        #
        # clear_read_only(self.file_path)
        # self.dump_dec_data(self.dec.dec_data)
        # read_only(self.file_path)
        # logger.error(
        #     f'Invalid Decryption Attempt || LOCK STATUS : {self.dec.dec_data[0]} || Fail Attempts : {self.dec.dec_data[1]} || TimeStamp : {self.dec.dec_data[1]} || Access Reset Time : {__for_time} ||')


    def next_call(self):
        # 1. RESETTING DEC DATA
        logger.log(f'\nDecryption -> File: {self.file_path} | Access : Authorized\n')
        self.dec.update_lock_status(None, 0, False)
        if not self.commit_dec_data_internal():
            return

        # 2. Output dir input
        out_dir = filedialog.askdirectory(parent=self.master, initialdir="C;\\",
                                          title='Choose a directory to Decrypt Files')

        # out_dir = generate_dec_output_dir_path(self.file_path, out_dir_pref=out_dir, non_existing=True)

        # 3. To Decrypt
        self.progress_frame.init()
        self.master.animator.animate_left(self.pass_check_frame, self.progress_frame,
                                          last_call=lambda _arg=False: self.pass_check_frame.clear(reset_quit=_arg),
                                          relheight=1, y=0)
        self._decrypt_init(out_dir=out_dir)


    def _decrypt_thread(self, out_dir):
        try:
            clear_read_only(self.file_path)

            # if out_dir and not os.path.isdir(out_dir):
            #     os.makedirs(out_dir)

            with open(self.file_path, 'rb+') as e_f_des:
                done = self.dec.decrypt_batch(e_f_des, set_header=False, out_dir=out_dir, on_prog_call=self.progress_frame.on_progress, cancellation_provider=self.is_cancelled)

            if done:
                self.progress_frame.cancel_call = None
                logger.log(f'\nDecryption : File << {self.file_path} >> Decrypted Successfully, OUTPUT FOLDER : {self.dec.out_dir} \n')
                self.master.show_final_message(self, title=f"Decryption Successful",
                                               alt=f"Encrypted File : {get_name(self.file_path, True)}\nOutput Folder : {self.dec.out_dir}",
                                               title_fg='#5CFF74',
                                               alt_fg='skyblue')

            elif self.is_cancelled():
                logger.warning('Decryption cancelled by User. Cleaning up...')
                self.master.show_final_message(self, title=f"Decryption Cancelled",
                                               alt=f"Encrypted File : {get_name(self.file_path, True)}\nUser Interruption: Cancelled by User")
        except Exception as dec_exc:
            logger.error(f'Error While Decrypting << {self.file_path} >> : {dec_exc}', dec_exc)
            self.master.show_final_message(self, title=f"Decryption failed",
                                           alt=f"Encrypted File : {get_name(self.file_path, True)}\nError Code : {dec_exc}\nSee Logs for details")
        finally:
            read_only(self.file_path)
            self.pause = False

    def _decrypt_init(self, out_dir):
        self.pause = False
        self.progress_frame.cancel_call = self.cancel_progress
        logger.log(f'\n-->> Decryption : Process Started')
        if is_dir_writable(out_dir):
            __th = Thread(target=self._decrypt_thread, kwargs={'out_dir': out_dir})
            __th.start()
        else:
            logger.error('Decryption : Output Directory does not have write access')
            read_only(self.file_path)
            self.master.show_final_message(self, title=f"Decryption Failed",
                                           alt=f"Encrypted File : {get_name(self.file_path, True)}\n\nError Code : Output dolder does not have write access")

    def clear(self):
        self.file_path = ''
        self.pause = False
        self.dec.clear_cache()
        self.pass_check_frame.clear()
        self.progress_frame.clear()

        self.pass_check_frame.place_forget()
        self.progress_frame.place_forget()
        self.progress_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


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
    def __init__(self, size=C.UiSize, pos=(0, 0), loop_interval=C.UiLoopInterval, frame_animation_enabled=C.UiFrameAnimationEnabled, center=True):
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
        self.animator.enabled = frame_animation_enabled

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
                                            f'{get_name(enc_f_path, True)} : Either not Encrypted or Corrupted')
            else:
                self.show_final_message(self.main_menu_frame, 'File Load Error',
                                        f'{get_name(enc_f_path, True)} : Either Does not Exists')

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
win = UI()
win.by_sys()  # Loading by sys args

win.mainloop()
