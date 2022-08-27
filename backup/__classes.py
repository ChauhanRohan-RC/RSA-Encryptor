import os
from tkinter import *


# ..............................................   Static Functions   .........................
def rgb(*r_g_b):
    return '#%02x%02x%02x' % r_g_b


def format_path(path, chars=30, start_weight=0.7):
    """
    :param path: file path
    :param chars: no of chars in formatted file path
    :param start_weight: weight of head of file path (excluding extension) in output
    :return: formattedd file path
    """
    if len(path) <= chars:
        return path
    _name, _ext = os.path.splitext(path)
    _len_n = chars - len(_ext)
    _len_n1 = int(_len_n * start_weight)
    return f'{_name[:_len_n1 - 2]}...{_name[-(_len_n - _len_n1 - 1):]}{_ext}'  # -3 for 3 dots


def format_mills(mills, out='tuple'):
    sec_ = mills // 1000
    min_, sec_ = divmod(sec_, 60)
    hr_, min_ = divmod(min_, 60)
    if out == 'tuple':
        return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'
    return f'{hr_:02d} hr {min_:02d} min {sec_:02d} sec'


def format_secs(secs, out='str'):
    min_, sec_ = divmod(secs, 60)
    hr_, min_ = divmod(min_, 60)
    if out == 'tuple':
        return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'
    return f'{hr_:02d} hr {min_:02d} min {sec_:02d} sec'
# ..................................................................................


class Logger:
    def __init__(self, file_path='Log.txt'):
        self.file_path = file_path

    def clear(self):
        with open(self.file_path, 'w+') as l__f:
            l__f.write('')

    def log(self, text):
        with open(self.file_path, 'a+') as l__f:
            l__f.write('\n' + text)

    def warning(self, warning):
        self.log(f'\n -->> WARNING : {warning}\n')

    def error(self, error):
        self.log(f'\n -->> ERROR : {error}\n')

    def by_user(self, message):
        self.log(f'\n --> User Interruption : {message}\n')

    def show_log(self):
        os.startfile(self.file_path)


class HoverB(Button):
    def __init__(self, master, bg='black', fg=rgb(200, 200, 200), abg=rgb(60, 60, 60), afg=rgb(255, 255, 255),
                 hoverbg=rgb(40, 40, 40), hoverfg=rgb(255, 255, 255), relief='flat', bd=0, **kwargs):
        self.master = master
        self.bg, self.fg = bg, fg
        self.abg, self.afg = abg, afg
        self.hoverbg, self.hoverfg = hoverbg, hoverfg

        kwargs.update({'bg': bg, 'fg': fg, 'activeforeground': afg, 'activebackground': abg, 'relief': relief, 'bd': bd})
        Button.__init__(self, master, **kwargs)

        self.bind('<Enter>', self.mouse_enter)
        self.bind('<Leave>', self.mouse_leave)

    def mouse_enter(self, event=None):
        if self['state'] == 'normal':
            self.configure(bg=self.hoverbg, fg=self.hoverfg)

    def mouse_leave(self, event=None):
        self.configure(bg=self.bg, fg=self.fg)


class FrameAnimator:
    """
     1. Frames must have same master
     2. Frame1 : must be placed using Frame.place (got place.forgot after animation)
     3. Frame2 : got filled in X after animation

    """
    def __init__(self, master, anm_time=130, anm_step=0.02):
        self.master = master         # to loop using after method
        self.anm_time = anm_time     # time in ms to complete animation (relwidth from 0 to 1) or (relx from 1 to 0)
        self.anm_step = anm_step     # increment step at each iteration (of relwidth or relx)
        self._max_anm_rel = 1.00 - self.anm_step

        self._anm_time = round(self.anm_time * self.anm_step)  # time for each iteration

        self.last_call = None        # callback when animation completes, got reset after every animation
        self.last_args = None        # args for last call

    def set_new_time(self, anm_time, anm_step=0.02):
        self.anm_time = anm_time
        self.anm_step = anm_step

        self._anm_time = round(self.anm_time * self.anm_step)

    def _animate_left(self, f1, f2, cur_w=0.00):
        if cur_w < self._max_anm_rel:
            cur_w += self.anm_step
            cur_rex = 1 - cur_w
            f1.place_configure(relwidth=cur_rex)                  # decreasing width of frame1
            f2.place_configure(relwidth=cur_w, relx=cur_rex)      # decreasing relx of frame2

            self.master.after(self._anm_time, self._animate_left, f1, f2, cur_w)
        else:
            f1.place_forget()
            f2.place_configure(relwidth=1, relx=0)
            if self.last_call:
                self.last_call(*self.last_args)
                self.last_call = self.last_args = None

    def animate_left(self, frame_1, frame_2, last_call=None, *last_args, **place_kwargs):
        """
           .............       Frame Animation from Right to Left (using relx and relwidth)      ..............
        :param last_call: call when animation completes
        :param frame_1: already placed frame, got forget after animation
        :param frame_2: frame to be placed, got filled after animation in X
        :param place_kwargs : place kwargs for frame2
        """
        place_kwargs['relx'] = 1
        place_kwargs['relwidth'] = 0
        frame_2.place(**place_kwargs)
        frame_2.tkraise()

        self.last_call = last_call
        self.last_args = last_args
        self.master.after(self._anm_time, self._animate_left, frame_1, frame_2, 0.00)

    def _animate_right(self, f1, f2, cur_w=0.00):
        if cur_w < self._max_anm_rel:
            cur_w += self.anm_step

            f1.place_configure(relx=cur_w)         # increasing relx of frame1
            f2.place_configure(relwidth=cur_w)     # increasing relwidth of frame2

            self.master.after(self._anm_time, self._animate_right, f1, f2, cur_w)
        else:
            f1.place_forget()
            f2.place_configure(relwidth=1)
            if self.last_call:
                self.last_call(*self.last_args)
                self.last_call = self.last_args = None

    def animate_right(self, frame_1, frame_2, last_call=None, *last_args, **place_kwargs):
        """
           .............       Frame Animation from Left to Right (using relwidth)      ..............
        :param last_call: call when animation completes
        :param frame_1: already placed frame, got forget after animation
        :param frame_2: frame to be placed, got filled after animation in X
        :param place_kwargs : place kwargs for frame2
        """
        place_kwargs['relx'] = place_kwargs['relwidth'] = 0
        frame_2.place(**place_kwargs)
        frame_2.tkraise()

        self.last_call = last_call
        self.last_args = last_args
        self.master.after(self._anm_time, self._animate_right, frame_1, frame_2, 0.00)

    def _animate_zoom_in(self, f1, f2, cur_w=0):
        if cur_w < self._max_anm_rel:
            cur_w += self.anm_step
            f2.place_configure(relwidth=cur_w, relheight=cur_w)
            self.master.after(self._anm_time, self._animate_zoom_in, f1, f2, cur_w)
        else:
            f1.place_forget()
            f2.place_configure(relwidth=1, relheight=1)
            if self.last_call:
                self.last_call(*self.last_args)
                self.last_call = self.last_args = None

    def animate_zoom_in(self, frame_1, frame_2, last_call=None, *last_args):
        frame_2.place(relx=0.5, rely=0.5, relwidth=0, relheight=0, anchor='center')
        frame_2.tkraise()
        self.last_call = last_call
        self.last_args = last_args
        self.master.after(self._anm_time, self._animate_zoom_in, frame_1, frame_2, 0)

    def _animate_zoom_out(self, f1, f2, cur_w=1.00):
        if cur_w > self.anm_step:
            cur_w -= self.anm_step
            f1.place_configure(relwidth=cur_w, relheight=cur_w)
            self.master.after(self._anm_time, self._animate_zoom_out, f1, f2, cur_w)
        else:
            f2.tkraise()
            f1.place_forget()
            if self.last_call:
                self.last_call(*self.last_args)
                self.last_call = self.last_args = None

    def animate_zoom_out(self, frame_1, frame_2, last_call=None, *last_args):
        frame_2.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        self.last_call = last_call
        self.last_args = last_args
        self.master.after(self._anm_time, self._animate_zoom_out, frame_1, frame_2, 1.00)


class LeftNotification(Frame):
    """ slides to left """
    def __init__(self, master, relwidth, relheight, relx, rely, anm_time=140, anm_step=0.02,
                 bg=rgb(50, 50, 50), fg=rgb(240, 240, 240), abg='black', afg='white', hoverbg='black', hoverfg='white', l_font='comicsans 10',
                 b_font='comicsans 10', click_call=None, *click_args, **kwargs):
        """
        :param frame_kwargs: frame config options
        :param anm_time : animation time in seconds
        :param anm_step : animation step in relwidth
        """
        self.master = master
        self.relwidth, self.relheight = relwidth, relheight
        self.relx, self.rely = relx, rely

        # animation constants
        self.anm_time = anm_time
        self.anm_step = anm_step
        self._anm_time = round(self.anm_time * self.anm_step)

        # Design
        self.bg, self.fg = bg, fg
        self.abg, self.afg = abg, afg
        self.hoverbg, self.hoverfg = hoverbg, hoverfg
        self.l_font, self.b_font = l_font, b_font

        # initial case
        self._relx, self._rely = self.relx + self.relwidth, self.rely
        self._relwidth, self._relheight = 0, self.relheight

        self.state = 0                  # 0 for un docked, 1 for docked, 2 for busy

        self.click_call = click_call
        self.click_args = click_args
        self.temp_click_call = None     # temporary click call for a notification if given

        kwargs['bg'] = self.bg          # overriding kwargs
        Frame.__init__(self, master, **kwargs)

        self.notice = Label(self, bg=self.bg, fg=self.fg, font=self.l_font, relief='flat', bd=0,
                            activebackground=self.abg, activeforeground=self.afg, anchor='center', text='Hello !')
        self.undock_b = Button(self, text='X', width=3, height=1, command=self.clear, bg=self.bg, fg=self.bg, font=self.b_font,
                               relief='flat', bd=0, activebackground=self.abg, activeforeground=self.afg)

        # Placing Widgets
        self.notice.place(relx=0.5, rely=0.5, relwidth=1, anchor='center')
        self.undock_b.place(relx=1, rely=0, anchor='ne')

        # Bindings
        self.bind('<Enter>', self.mouse_enter_call)
        self.bind('<Leave>', self.mouse_leave_call)
        if self.click_call:
            self.bind('<Button-1>', lambda event, _args=self.click_args: self.click_call(*_args))
            self.notice.bind('<Button-1>', lambda event, _args=self.click_args: self.click_call(*_args))

    def mouse_enter_call(self, event):
        self['bg'] = self.hoverbg
        self.notice.configure(bg=self.hoverbg, fg=self.hoverfg)
        self.undock_b.configure(bg=self.hoverbg, fg=self.hoverfg, activebackground=self.hoverbg, activeforeground=self.hoverfg)

    def mouse_leave_call(self, event):
        self['bg'] = self.bg
        self.notice.configure(bg=self.bg, fg=self.fg)
        self.undock_b.configure(bg=self.bg, fg=self.bg)

    def set_new_time(self, anm_time, anm_step=0.02):
        self.anm_time = anm_time
        self.anm_step = anm_step
        self._anm_time = round(self.anm_time * self.anm_step)

    def __dock(self, cur_width=0.00):
        if cur_width < self.relwidth - self.anm_step:
            cur_width += self.anm_step
            self._relx -= self.anm_step
            self.place_configure(relwidth=cur_width, relx=self._relx)
            self.master.after(self._anm_time, self.__dock, cur_width)
        else:
            self.place_configure(relwidth=self.relwidth, relx=self.relx)
            self.state = 1

    def _dock(self, **place_kwargs):
        place_kwargs['relwidth'] = self._relwidth
        place_kwargs['relheight'] = self._relheight
        place_kwargs['relx'] = self._relx
        place_kwargs['rely'] = self._rely

        self.state = 2
        self.place(**place_kwargs)
        self.lift()
        self.master.after(self._anm_time, self.__dock, 0.00)

    def __undock(self, cur_width):
        if cur_width > self.anm_step:
            cur_width -= self.anm_step
            self._relx += self.anm_step
            self.place_configure(relwidth=cur_width, relx=self._relx)
            self.master.after(self._anm_time, self.__undock, cur_width)
        else:
            self.place_configure(relx=self._relx, rely=self._rely, relwidth=self._relwidth, relheight=self._relheight)
            self.place_forget()
            self.state = 0

    def _undock(self):
        self.state = 2
        self.master.after(self._anm_time, self.__undock, self.relwidth)

    def dock(self, **place_kwargs):
        if self.state == 0:     # un docked
            self._dock(**place_kwargs)
        elif self.state == 2:   # busy
            self.master.after(self.anm_time + 10, lambda kwargs: self.dock(**kwargs), place_kwargs)

    def undock(self, event=None):
        if self.state == 1:     # docked
            self._undock()
        elif self.state == 2:   # busy
            self.master.after(self.anm_time + 10, self.undock)

    """ ........................   Main Operational Methods  ............................. """
    def notify(self, message, font='', click_call=None, *click_args):
        if not font:
            font = self.l_font
        if click_call:
            self.temp_click_call = click_call
            self.bind('<Button-1>', lambda __event, _args=click_args: click_call(*_args))
            self.notice.bind('<Button-1>', lambda __event, _args=click_args: click_call(*_args))
        self.notice.configure(font=font, text=message)
        self.dock()

    def clear(self, event=None):
        self.undock()
        self.notice['text'] = ''
        if self.temp_click_call:
            if self.click_call:
                self.bind('<Button-1>', lambda __event, _args=self.click_args: self.click_call(*_args))
                self.notice.bind('<Button-1>', lambda __event, _args=self.click_args: self.click_call(*_args))
            else:
                self.unbind('<Button-1>')
                self.notice.unbind('<Button-1>')
            self.temp_click_call = None


class VScroll(Canvas):
    def __init__(self, master, command=None, bg=rgb(230, 230, 230), fg='skyblue', hoverbg=rgb(210, 210, 210), hoverfg='skyblue', highlightthickness=0, bd=0, **kwargs):
        """ attrs having fg are for slider, bg for trough """
        self.master = master
        self.bg, self.fg = bg, fg
        self.hoverbg, self.hoverfg = hoverbg, hoverfg
        self.command = command

        kwargs.update({'bg': self.bg, 'highlightthickness': highlightthickness, 'bd': bd})

        Canvas.__init__(self, master, **kwargs)
        self.slider = self.create_rectangle(0, 0, 0, 0, fill=self.fg, width=0)
        self.tag_bind(self.slider, '<B1-Motion>', self.motion_call)
        self.bind('<Button-1>', self.click_call)
        self.bind('<Enter>', self.m_enter)
        self.bind('<Leave>', self.m_leave)

    def m_enter(self, event=None) -> None:
        self['bg'] = self.hoverbg
        self.itemconfigure(self.slider, fill=self.hoverfg)

    def m_leave(self, event=None) -> None:
        self['bg'] = self.bg
        self.itemconfigure(self.slider, fill=self.fg)

    def over_slider(self, *pos) -> bool:
        _x, _y, x, y = self.coords(self.slider)
        if _x < pos[0] < x:
            if _y < pos[1] < y:
                return True
        return False

    def set_command(self, command) -> None:
        self.command = command

    def draw(self, first, last) -> None:
        self.update()
        self.coords(self.slider, 0, first * self.winfo_height(), self.winfo_width(), last * self.winfo_height())

    def set(self, first, last) -> None:
        first, last = float(first), float(last)
        self.draw(first, last)

    def click_call(self, event) -> None:
        if self.command:
            if not self.over_slider(event.x, event.y):
                self.command('moveto', event.y / self.winfo_height())

    def motion_call(self, event) -> None:
        if self.command:
            self.command('moveto', event.y / self.winfo_height())


class HScroll(Canvas):
    def __init__(self, master, command=None, bg=rgb(230, 230, 230), fg='skyblue', hoverbg=rgb(210, 210, 210), hoverfg='skyblue', highlightthickness=2, bd=0, **kwargs):
        """ attrs having fg are for slider, bg for trough """
        self.master = master
        self.bg, self.fg = bg, fg
        self.hoverbg, self.hoverfg = hoverbg, hoverfg
        self.command = command

        kwargs.update({'bg': self.bg, 'highlightthickness': highlightthickness, 'bd': bd})

        Canvas.__init__(self, master, **kwargs)
        self.slider = self.create_rectangle(0, 0, 0, 0, fill=self.fg, width=0)
        self.tag_bind(self.slider, '<B1-Motion>', self.motion_call)
        self.bind('<Button-1>', self.click_call)
        self.bind('<Enter>', self.m_enter)
        self.bind('<Leave>', self.m_leave)

    def m_enter(self, event=None):
        self['bg'] = self.hoverbg
        self.itemconfigure(self.slider, fill=self.hoverfg)

    def m_leave(self, event=None):
        self['bg'] = self.bg
        self.itemconfigure(self.slider, fill=self.fg)

    def over_slider(self, *pos):
        _x, _y, x, y = self.coords(self.slider)
        if _x < pos[0] < x:
            if _y < pos[1] < y:
                return True
        return False

    def set_command(self, command):
        self.command = command

    def draw(self, first, last):
        self.coords(self.slider, first * self.winfo_width(), 0, last * self.winfo_width(), self.winfo_height())

    def set(self, first, last):
        first, last = float(first), float(last)
        self.draw(first, last)

    def click_call(self, event):
        if self.command:
            if not self.over_slider(event.x, event.y):
                self.command('moveto', event.x / self.winfo_width())

    def motion_call(self, event):
        if self.command:
            self.command('moveto', event.x / self.winfo_width())


class VScrollScale:
    """ master should be a canvas, width and trough width should be even  """
    def __init__(self, canvas, width=18, rel_height=0.9, relx=0.9, rely=0.05, trough_width=4, trough1_color='orange', trough2_color='skyblue', slider_fill='', slider_active_fill='orange'):
        """
        :param canvas: Canvas to draw the scrollbar
        :param width: Scrollbar width (fixed) in pixels
        :param rel_height: scrollbar height relative to canvas  (resize automatically width canvas height)
        :param relx: scrollbar x relative to canvas
        :param rely: scrollbar y relative to canvas
        :param trough1_color: color of trough left of slider = slider outline color
        :param trough2_color: color of trough right of slider
        :param trough_width: width of trough in pixels = slider outline width
        :param slider_fill: slider fill color when not active
        :param slider_active_fill: slider fill color when active (in motion)
        """
        self.canvas = canvas
        self.width, self.rel_height = width, rel_height
        self.relx, self.rely = relx, rely
        self.trough1_color, self.trough2_color = trough1_color, trough2_color
        self.trough_width = trough_width
        self.slider_fill = slider_fill
        self.slider_active_fill = slider_active_fill
        self.trough_w_half = int(self.trough_width / 2)

        self.slider_radii = int((self.width - self.trough_width) / 2)  # middle of outer and inner raddi
        self.command = None
        self.in_motion = False

        self.fraction = 0.00000001    # (1 - delta)  delta is last - first

        # trough constant x coord relative to self.x
        self.trough_x1 = int((self.width / 2) - self.trough_w_half)
        self.trough_x2 = int((self.width / 2) + self.trough_w_half)

        self.trough1 = self.trough2 = self.slider = None
        self.draw()
        self.canvas.tag_bind(self.slider, '<B1-Motion>', self.motion_call)
        self.canvas.tag_bind(self.slider, '<ButtonPress-1>', self.s_press_call)
        self.canvas.tag_bind(self.slider, '<ButtonRelease-1>', self.s_release_call)
        self.canvas.tag_bind(self.trough1, '<Button-1>', self.click_call)
        self.canvas.tag_bind(self.trough2, '<Button-1>', self.click_call)

    def click_call(self, event) -> None:
        if self.command:
            __ch = self.canvas.winfo_height()
            __pos = (event.y - int(__ch * self.rely)) / (__ch * self.rel_height)
            _min = self.get_min_slider_pos()
            _max = self.get_max_slider_pos()
            if __pos <= _min:
                self.update(_min)
            elif __pos >= _max:
                self.update(_max)
            else:
                self.update(__pos)
            self.command('moveto', __pos * self.fraction)

    def motion_call(self, event) -> None:
        if self.command:
            __ch = self.canvas.winfo_height()
            __pos = (event.y - int(__ch * self.rely)) / (__ch * self.rel_height)
            _min = self.get_min_slider_pos()
            _max = self.get_max_slider_pos()
            if __pos <= _min:
                self.update(_min)
            elif __pos >= _max:
                self.update(_max)
            else:
                self.update(__pos)
            self.command('moveto', __pos * self.fraction)

    def s_press_call(self, event) -> None:
        self.in_motion = True
        self.canvas.itemconfigure(self.slider, fill=self.slider_active_fill)

    def s_release_call(self, event) -> None:
        self.in_motion = False
        self.canvas.itemconfigure(self.slider, fill=self.slider_fill)

    def get_height(self) -> float:
        self.canvas.update()
        return self.canvas.winfo_height() * self.rel_height

    def get_upper_coord(self) -> tuple:
        return int(self.canvas.winfo_width() * self.relx), int(self.canvas.winfo_height() * self.rely)

    def get_abs_x(self, x) -> tuple:
        return x + self.trough_x1, x + self.trough_x2

    def get_min_slider_pos(self) -> float:
        return self.width / (self.get_height() * 2)

    def get_max_slider_pos(self) -> float:
        __h = self.get_height()
        return (__h - (self.width / 2)) / __h

    def draw(self, slider_pos=0.5) -> None:
        __x, __y = self.get_upper_coord()
        __h = self.get_height()
        __s_center_y = __y + (__h * slider_pos)

        _tx1, _tx2 = self.get_abs_x(__x)
        self.trough1 = self.canvas.create_rectangle(_tx1, __y, _tx2, __s_center_y - self.slider_radii, width=0, fill=self.trough1_color)
        self.trough2 = self.canvas.create_rectangle(_tx1, __s_center_y + self.slider_radii, _tx2, __y + __h, width=0, fill=self.trough2_color)
        self.slider = self.canvas.create_oval(__x + self.trough_w_half, __s_center_y - self.slider_radii, __x + self.width - self.trough_w_half, __s_center_y + self.slider_radii, width=self.trough_width, fill=self.slider_fill, outline=self.trough1_color)

    def update(self, slider_pos) -> None:
        __x, __y = self.get_upper_coord()
        __h = self.get_height()
        __s_center_y = __y + (__h * slider_pos)
        _tx1, _tx2 = self.get_abs_x(__x)
        self.canvas.coords(self.trough1, _tx1, __y, _tx2, __s_center_y - self.slider_radii)
        self.canvas.coords(self.trough2, _tx1, __s_center_y + self.slider_radii, _tx2, __y + __h)
        self.canvas.coords(self.slider, __x + self.trough_w_half, __s_center_y - self.slider_radii, __x + self.width - self.trough_w_half, __s_center_y + self.slider_radii)

    def set(self, first, last) -> None:
        if not self.in_motion:
            first, last = float(first), float(last)
            _del = last - first
            _min = self.get_min_slider_pos()
            if _del < 1:
                self.fraction = 1 - _del
                _pos = first * (1 / self.fraction)
                _max = self.get_max_slider_pos()
                if _pos <= _min:
                    self.update(_min)
                elif _pos >= _max:
                    self.update(_max)
                else:
                    self.update(_pos)
            else:
                self.fraction = 1
                self.update(_min)

    def set_command(self, command) -> None:
        self.command = command


class HScrollScale:
    """ master should be a canvas, width and trough width should be even  """
    def __init__(self, canvas, height=18, rel_width=0.9, relx=0.05, rely=0.9, trough_width=4, trough1_color='orange', trough2_color='skyblue', slider_fill='', slider_active_fill='orange'):
        """
        :param canvas: Canvas to draw the scrollbar
        :param height: Scrollbar height (fixed) in pixels
        :param rel_width: scrollbar width relative to canvas (resize automatically width canvas width)
        :param relx: scrollbar x relative to canvas
        :param rely: scrollbar y relative to canvas
        :param trough1_color: color of trough left of slider = slider outline color
        :param trough2_color: color of trough right of slider
        :param trough_width: width of trough in pixels = slider outline width
        :param slider_fill: slider fill color when not active
        :param slider_active_fill: slider fill color when active (in motion)
        """
        self.canvas = canvas
        self.height, self.rel_width = height, rel_width
        self.relx, self.rely = relx, rely
        self.trough1_color, self.trough2_color = trough1_color, trough2_color
        self.trough_width = trough_width
        self.slider_fill = slider_fill
        self.slider_active_fill = slider_active_fill
        self.trough_w_half = int(self.trough_width / 2)

        self.slider_radii = int((self.height - self.trough_width) / 2)  # middle of outer and inner raddi
        self.command = None
        self.in_motion = False

        self.fraction = 0.00001

        # trough constant x coord relative to self.x
        self.trough_y1 = int((self.height / 2) - self.trough_w_half)
        self.trough_y2 = int((self.height / 2) + self.trough_w_half)

        self.trough1 = self.trough2 = self.slider = None
        self.draw()
        self.canvas.tag_bind(self.slider, '<B1-Motion>', self.motion_call)
        self.canvas.tag_bind(self.slider, '<ButtonPress-1>', self.s_press_call)
        self.canvas.tag_bind(self.slider, '<ButtonRelease-1>', self.s_release_call)
        self.canvas.tag_bind(self.trough1, '<Button-1>', self.click_call)
        self.canvas.tag_bind(self.trough2, '<Button-1>', self.click_call)

    def click_call(self, event) -> None:
        if self.command:
            __cw = self.canvas.winfo_width()
            __pos = (event.x - int(__cw * self.relx)) / (__cw * self.rel_width)
            _min = self.get_min_slider_pos()
            _max = self.get_max_slider_pos()
            if __pos <= _min:
                self.update(_min)
            elif __pos >= _max:
                self.update(_max)
            else:
                self.update(__pos)
            self.command('moveto', __pos * self.fraction)

    def motion_call(self, event) -> None:
        if self.command:
            __cw = self.canvas.winfo_width()
            __pos = (event.x - int(__cw * self.relx)) / (__cw * self.rel_width)
            _min = self.get_min_slider_pos()
            _max = self.get_max_slider_pos()
            if __pos <= _min:
                self.update(_min)
            elif __pos >= _max:
                self.update(_max)
            else:
                self.update(__pos)
            self.command('moveto', __pos * self.fraction)

    def s_press_call(self, event) -> None:
        self.in_motion = True
        self.canvas.itemconfigure(self.slider, fill=self.slider_active_fill)

    def s_release_call(self, event) -> None:
        self.in_motion = False
        self.canvas.itemconfigure(self.slider, fill=self.slider_fill)

    def get_width(self) -> float:
        self.canvas.update()
        return self.canvas.winfo_width() * self.rel_width

    def get_upper_coord(self) -> tuple:
        return int(self.canvas.winfo_width() * self.relx), int(self.canvas.winfo_height() * self.rely)

    def get_abs_y(self, y) -> tuple:
        return y + self.trough_y1, y + self.trough_y2

    def get_min_slider_pos(self) -> float:
        return self.height / (2 * self.get_width())

    def get_max_slider_pos(self) -> float:
        __w = self.get_width()
        return (__w - (self.height / 2)) / __w

    def draw(self, slider_pos: float = 0.5) -> None:
        __x, __y = self.get_upper_coord()
        __w = self.get_width()
        __s_center_x = __y + (__w * slider_pos)
        _ty1, _ty2 = self.get_abs_y(__y)
        self.trough1 = self.canvas.create_rectangle(__x, _ty1, __s_center_x - self.slider_radii, _ty2, width=0, fill=self.trough1_color)
        self.trough2 = self.canvas.create_rectangle(__s_center_x + self.slider_radii, _ty1, __x + __w, _ty2, width=0, fill=self.trough2_color)
        self.slider = self.canvas.create_oval(__s_center_x - self.slider_radii, __y + self.trough_w_half, __s_center_x + self.slider_radii, __y + self.height - self.trough_w_half, width=self.trough_width, fill=self.slider_fill, outline=self.trough1_color)

    def update(self, slider_pos: float) -> None:
        __x, __y = self.get_upper_coord()
        __w = self.get_width()
        __s_center_x = __x + (__w * slider_pos)
        _ty1, _ty2 = self.get_abs_y(__y)
        self.canvas.coords(self.trough1, __x, _ty1, __s_center_x - self.slider_radii, _ty2)
        self.canvas.coords(self.trough2, __s_center_x + self.slider_radii, _ty1, __x + __w, _ty2)
        self.canvas.coords(self.slider, __s_center_x - self.slider_radii, __y + self.trough_w_half, __s_center_x + self.slider_radii, __y + self.height - self.trough_w_half)

    def set(self, first: float, last: float) -> None:
        if not self.in_motion:
            first, last = float(first), float(last)
            _del = last - first
            _min = self.get_min_slider_pos()
            if _del < 1:
                self.fraction = 1 - _del
                _pos = first * (1 / self.fraction)
                _max = self.get_max_slider_pos()
                if _pos <= _min:
                    self.update(_min)
                elif _pos >= _max:
                    self.update(_max)
                else:
                    self.update(_pos)
            else:
                self.update(_min)

    def set_command(self, command) -> None:
        self.command = command


class HProgressBar(Canvas):
    """
    Horizontal Progressbar ....................
    NOTE : please call set after any resizing or packing
    """
    def __init__(self, master, from_=0.00, to=100.00, value=None,  out_width=4, trough1_color=rgb(95, 255, 160),
                 trough2_color=rgb(250, 250, 250), out_color=rgb(250, 250, 250), trough1_hover_color=rgb(33, 255, 103),
                 trough2_hover_color=rgb(230, 230, 230), out_hover_color=rgb(220, 220, 220), **kwargs):
        self.master = master
        # Value attrs
        self.from_, self.to = from_, to
        self.range = to - from_
        self.value = value if value is not None else from_

        # Outline attrs
        self.out_width = out_width
        self._out_width = out_width * 2   # since canvas expand its outline

        # Colors
        self.trough1_color, self.trough2_color, self.out_color = trough1_color, trough2_color, out_color

        # Hover Colors
        self.trough1_hover_color, self.trough2_hover_color, self.out_hover_color = trough1_hover_color, trough2_hover_color, out_hover_color

        Canvas.__init__(self, master, **kwargs)
        if self.out_width:
            self.out_rect = self.create_rectangle(0, 0, 0, 0, fill='', width=self._out_width, outline=self.out_color)

        self.trough2 = self.create_rectangle(self.out_width, self.out_width, self.trough2_x2, self.trough_y2, width=0, fill=self.trough2_color)
        self.trough1 = self.create_rectangle(self.out_width, self.out_width, self.trough1_x2, self.trough_y2, width=0, fill=self.trough1_color)

        self.bind('<Enter>', self.m_enter)
        self.bind('<Leave>', self.m_leave)

    @property
    def rel_value(self):
        _rel_val = self.value - self.from_
        if _rel_val < 0:
            return 0
        if _rel_val > self.range:
            return self.range
        return _rel_val

    @property
    def trough_y2(self):
        return self.winfo_height() - self.out_width

    @property
    def trough2_x2(self):
        return self.winfo_width() - self.out_width

    @property
    def in_width(self):
        return self.winfo_width() - self._out_width

    @property
    def trough1_x2(self):
        return self.out_width + ((self.in_width / self.range) * self.rel_value)

    def update_outline(self):
        if self.out_width:
            self.coords(self.out_rect, 0, 0, self.winfo_width(), self.winfo_height())

    def update_trough2(self):
        self.coords(self.trough2, self.out_width, self.out_width, self.trough2_x2, self.trough_y2)

    def update_trough1(self, value=None):
        if value is not None:
            self.value = value
        self.coords(self.trough1, self.out_width, self.out_width, self.trough1_x2, self.trough_y2)

    def set(self, value=None):
        self.update()
        self.update_outline()
        self.update_trough2()
        self.update_trough1(value)

    def update_all(self):
        self.update()
        self.update_outline()
        self.update_trough2()

    def m_enter(self, event=None):
        if self.out_width:
            self.itemconfigure(self.out_rect, outline=self.out_hover_color)
        self.itemconfigure(self.trough2, fill=self.trough2_hover_color)
        self.itemconfigure(self.trough1, fill=self.trough1_hover_color)

    def m_leave(self, event=None):
        if self.out_width:
            self.itemconfigure(self.out_rect, outline=self.out_color)
        self.itemconfigure(self.trough2, fill=self.trough2_color)
        self.itemconfigure(self.trough1, fill=self.trough1_color)


class VProgressBar(Canvas):
    """
    Vertical Progressbar ....................
    NOTE : please call set after any resizing or packing
    """
    def __init__(self, master, from_=0.00, to=100.00, value=None, out_width=4, trough1_color=rgb(95, 255, 160),
                 trough2_color=rgb(250, 250, 250), out_color=rgb(250, 250, 250), trough1_hover_color=rgb(33, 255, 103),
                 trough2_hover_color=rgb(230, 230, 230), out_hover_color=rgb(220, 220, 220), **kwargs):
        self.master = master
        # Value attrs
        self.from_, self.to = from_, to
        self.range = to - from_
        self.value = value if value is not None else from_

        # Outline attrs
        self.out_width = out_width
        self._out_width = out_width * 2  # since canvas expand its outline

        # Colors
        self.trough1_color, self.trough2_color, self.out_color = trough1_color, trough2_color, out_color

        # Hover Colors
        self.trough1_hover_color, self.trough2_hover_color, self.out_hover_color = trough1_hover_color, trough2_hover_color, out_hover_color

        Canvas.__init__(self, master, **kwargs)
        if self.out_width:
            self.out_rect = self.create_rectangle(0, 0, 0, 0, fill='', width=self._out_width, outline=self.out_color)

        self.trough2 = self.create_rectangle(self.out_width, self.out_width, self.trough_x2, self.trough2_y2, width=0, fill=self.trough2_color)
        self.trough1 = self.create_rectangle(self.out_width, self.out_width, self.trough_x2, self.trough1_y2, width=0, fill=self.trough1_color)

        self.bind('<Enter>', self.m_enter)
        self.bind('<Leave>', self.m_leave)

    @property
    def rel_value(self):
        _rel_val = self.value - self.from_
        if _rel_val < 0:
            return 0
        if _rel_val > self.range:
            return self.range
        return _rel_val

    @property
    def trough_x2(self):
        return self.winfo_width() - self.out_width

    @property
    def trough2_y2(self):
        return self.winfo_height() - self.out_width

    @property
    def in_height(self):
        return self.winfo_height() - self._out_width

    @property
    def trough1_y2(self):
        return self.out_width + ((self.in_height / self.range) * self.rel_value)

    def update_outline(self):
        if self.out_width:
            self.coords(self.out_rect, 0, 0, self.winfo_width(), self.winfo_height())

    def update_trough2(self):
        self.coords(self.trough2, self.out_width, self.out_width, self.trough_x2, self.trough2_y2)

    def update_trough1(self, value=None):
        if value is not None:
            self.value = value
        self.coords(self.trough1, self.out_width, self.out_width, self.trough_x2, self.trough1_y2)

    def set(self, value=None):
        self.update()
        self.update_outline()
        self.update_trough2()
        self.update_trough1(value)

    def m_enter(self, event=None):
        if self.out_width:
            self.itemconfigure(self.out_rect, outline=self.out_hover_color)
        self.itemconfigure(self.trough2, fill=self.trough2_hover_color)
        self.itemconfigure(self.trough1, fill=self.trough1_hover_color)

    def m_leave(self, event=None):
        if self.out_width:
            self.itemconfigure(self.out_rect, outline=self.out_color)
        self.itemconfigure(self.trough2, fill=self.trough2_color)
        self.itemconfigure(self.trough1, fill=self.trough1_color)
