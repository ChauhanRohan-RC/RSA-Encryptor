from tkinter import Button, Toplevel, Label, Frame, Canvas, Entry, StringVar
import win32gui
import psutil


# ..............................................   Static Functions   .........................
def rgb(*r_g_b):
    return '#%02x%02x%02x' % r_g_b


def rgb_to_hex(*r_g_b):
    return int('%02x%02x%02x' % r_g_b, 16)


class RcDiag(Toplevel):
    """
    returns '' if no value or destroyed by the user
    """

    input_cache = {}

    def __init__(self, master, title_, caption, size=(320, 120), pos=None, entry_size=None, retain_value=False,
                 yoffset=20, command=print, icon=None, **kwargs):
        self.master = master
        self.title_ = title_
        self.size = size
        self.entry_size = entry_size
        self.retain_value = retain_value
        self.yoffset = yoffset
        self.pos = pos
        self.command = command

        self.text = StringVar()
        self.text.set(caption)

        self.value = ""  # variable that contains main_value

        self.temp = StringVar()
        if self.retain_value and self.title_ in self.__class__.input_cache.keys():
            self.temp.set(self.__class__.input_cache[self.title_])

        if self.pos is None:
            self.pos = self.master.winfo_rootx() + round(
                (self.master.winfo_width() - size[0]) / 2), self.master.winfo_rooty() + round(
                (self.master.winfo_height() - size[1]) / 2) - self.yoffset

        Toplevel.__init__(self, self.master, **kwargs)
        self.geometry(
            f'{size[0]}x{size[1]}+{self.pos[0]}+{self.pos[1]}')
        self.resizable(0, 0)
        self.title(self.title_)
        self.overrideredirect(True)
        self['bg'] = self.rgb(90, 90, 90)

        if icon:
            self.iconbitmap(icon)

        self.cap = Label(self, textvariable=self.text, font='comicsans 10 bold', relief="flat", bg=self.rgb(90, 90, 90),
                         fg=self.rgb(240, 240, 240))
        self.e = Entry(self, relief='flat', textvariable=self.temp, font='comicsans 10 bold')

        self.clear_b = Button(self, text="X", command=self.clear_entry, font='Comicsans 10 bold', relief="flat",
                              bg=self.rgb(90, 90, 90), fg=self.rgb(240, 240, 240), bd=0,
                              activebackground=self.rgb(110, 110, 110), activeforeground=self.rgb(255, 255, 255))

        self.b = Button(self, text="OK", command=self.submit, relief="flat", bg=self.rgb(90, 90, 90),
                        bd=0, activebackground=self.rgb(110, 110, 110), activeforeground=self.rgb(255, 255, 255),
                        font='comicsans 10 bold', fg=self.rgb(240, 240, 240))

        if entry_size:
            self.e['width'] = entry_size
        else:
            self.e['width'] = round(size[0] / 8)

        self.cap.place(relx=.01, rely=.1, relwidth=.98)
        self.e.place(relx=.2, rely=.475, relwidth=.55)
        self.clear_b.place(relx=.76, rely=.46, relwidth=.14)
        self.b.place(relx=.42, rely=.75, relwidth=.16)

        self.e.focus_force()
        self.bind('<Return>', self.submit)
        self.bind('<Escape>', lambda event: self.destroy())
        self.e.bind('<FocusOut>', lambda event: self.destroy())

    def __repr__(self):
        return f'RcDiag({self.master}, {self.title}, {self.text})'

    def clear_entry(self, event=None):
        self.e.delete(0, 'end')

    def submit(self, event=None):
        self.value = self.e.get()
        self.command(self.value)

    @staticmethod
    def rgb(*r_g_b):
        return '#%02x%02x%02x' % r_g_b

    def on_success(self, text, fg='white', font='Times 11 bold italic'):
        self.bind('<Return>', lambda event: self.destroy())
        if self.retain_value:
            self.__class__.input_cache[self.title_] = self.value
        _c = Canvas(self, bg=self.rgb(90, 90, 90), relief='flat', bd=0)
        _c.create_text(self.size[0] / 2, self.size[1] / 2,text=text, fill=fg, font=font, anchor='center')
        _c.place(x=0, y=0, relwidth=1, relheight=1)


class WinHandler:
    def __init__(self):
        self.pids = []
        self.req_pid = None
        self.found_hwnds = []

    def get_hwnds(self, win_title, win_class):
        self.found_hwnds.clear()
        win32gui.EnumWindows(self.enum_handler, (win_title, win_class))
        return self.found_hwnds

    @staticmethod
    def get_pid(exe_name):
        exe_name = f'{exe_name}.exe'.lower()
        for __p in psutil.process_iter():
            try:
                if __p.name().lower() == exe_name and __p.status() == psutil.STATUS_RUNNING:
                    return __p.pid, __p.t
            except (PermissionError, psutil.Error, AttributeError):
                pass
        return None

    def enum_handler(self, __hwnd, info_):
        if info_[1] == win32gui.GetClassName(__hwnd) and info_[0] in win32gui.GetWindowText(__hwnd):
            self.found_hwnds.append(__hwnd)

    def close_window(self, win_title, win_class):
        _hwnd_win = self.get_hwnds(win_title, win_class)
        for _hwnd in _hwnd_win:
            win32gui.SendMessage(_hwnd, 16)


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


class HScale(Canvas):
    """ Horizontal Scale, use even dimensions """
    def __init__(self, master, from_=0, to=100, value=0, trough_height=4, slider_radius=12, slider_out_width=2,
                 slider_active_out_width=None, bg='black', trough1_color='skyblue', trough2_color='grey',
                 slider_out_color=None, slider_fill='black', slider_active_out_color=None, slider_active_fill='skyblue',
                 highlightthickness=0, pady=4, motion_call=None, click_call=None, slider_click=True,
                 **kwargs):
        """
        :param from_: starting value
        :param to: ending value
        :param value: absolute value (from from_ -> to)
        :param trough_height: height of trough in pixels
        :param slider_radius: slider outermost radius (in pixels)
        :param slider_out_width: slider outline width, default is same as trough height
        :param slider_active_out_width: slider outline width in active state, default is slider ou width + 2
        :param bg: canvas background
        :param trough1_color: colour of trough to left of slider
        :param trough2_color: colour of trough to right of slider
        :param slider_out_color: slider outline colour
        :param slider_fill: slider fill colour
        :param slider_active_out_color: slider outline colour when active
        :param slider_active_fill: slider fill when active
        :param highlightthickness: of canvas
        :param pady: internal pad in y axis
        :param motion_call: callback when slider is in motion
        :param click_call: callback when scale is clicked
        :param slider_click: whether call the click_call when slider is clicked, default is True
        """

        self.master = master

        # Main logic
        self.from_, self.to = from_, to
        self.range = self.to - self.from_
        self.value = self._parse_val(value) if value is not None else self.from_
        self.slider_click = slider_click
        self.motion_call, self.click_call = motion_call, click_call

        # Dimensions
        self.trough_h = trough_height
        self.slider_or = slider_radius  # slider out most radius
        self.slider_od = self.slider_or * 2  # slider max diameter
        self.slider_ow = slider_out_width if slider_out_width is not None else self.trough_h
        self.slider_aow = slider_active_out_width if slider_active_out_width is not None else self.slider_ow + 2
        self._slider_owh, self._slider_aowh = self.slider_ow / 2, self.slider_aow / 2
        self.slider_r = slider_radius - self._slider_aowh
        self.slider_d = self.slider_r * 2
        self.pady = pady

        self.height = kwargs['height'] = (slider_radius + self.pady) * 2

        # Colors
        self.trough1_c, self.trough2_c = trough1_color, trough2_color
        self.slider_oc = slider_out_color if slider_out_color is not None else self.trough1_c
        self.slider_aoc = slider_active_out_color if slider_active_out_color is not None else self.slider_oc
        self.slider_fill = slider_fill if slider_fill is not None else self.trough1_c
        self.slider_a_fill = slider_active_fill if slider_active_fill is not None else self.trough1_c

        # Constants
        self.trough_y1 = round((self.height - self.trough_h) / 2)
        self.trough_y2 = self.trough_y1 + self.trough_h

        self.trough1_x1 = self._slider_aowh
        self.slider_y1 = self._slider_aowh + self.pady
        self.slider_y2 = self.height - self.slider_y1

        kwargs['highlightthickness'] = highlightthickness
        kwargs['bg'] = bg
        Canvas.__init__(self, self.master, **kwargs)

        self.trough_1 = None
        self.trough_2 = None
        self.slider = None

        self.draw(self.value)

        self.tag_bind(self.slider, '<B1-Motion>', self._motion_handler)
        self.bind('<ButtonPress-1>', self._click_press_handler)
        self.bind('<ButtonRelease-1>', self._click_release_handler)

    @property
    def logic_width(self):
        self.update()
        return self.winfo_width() - self.slider_od

    @property
    def trough2_x2(self):
        self.update()
        return self.winfo_width() - self.trough1_x1

    @property
    def rel_value(self):
        # in 0 to self.range
        __rel = self.value - self.from_
        if __rel < 0:
            return 0
        if __rel > self.range:
            return self.range
        return __rel

    def get_rel_value(self, value):
        value -= self.from_
        if value < 0:
            return 0
        if value > self.range:
            return self.range
        return value

    @property
    def pix(self):
        return self.rel_value * self.pix_per_val

    @property
    def pix_per_val(self):
        return self.logic_width / self.range

    @property
    def trough1_x2(self):
        # since logic width is relative to slider outer diameter
        return self._slider_aowh + (self.rel_value * self.pix_per_val)

    @property
    def trough2_x1(self):
        return self.trough1_x2 + self.slider_d

    def draw(self, value):
        self.value = self._parse_val(value)
        __pix = self.rel_value * self.pix_per_val
        t1_x2 = self._slider_aowh + __pix
        t2_x1 = t1_x2 + self.slider_d

        self.trough_1 = self.create_rectangle(self.trough1_x1, self.trough_y1, t1_x2, self.trough_y2,
                                              fill=self.trough1_c, width=0)
        self.trough_2 = self.create_rectangle(t2_x1, self.trough_y1, self.trough2_x2, self.trough_y2,
                                              fill=self.trough2_c, width=0)

        self.slider = self.create_oval(t1_x2, self.slider_y1, t2_x1, self.slider_y2, width=self.slider_ow,
                                       fill=self.slider_fill, outline=self.slider_oc)

    # ...................................       Logical Methods       ..........................................
    def over_slider(self, *pos) -> bool:
        _x1, _y1, _x2, _y2 = self.coords(self.slider)
        if _x1 < pos[0] < _x2:
            if _y1 < pos[1] < _y2:
                return True
        return False

    # Relative Methods  (efficient, uses relative value -->> 0 - self.range)
    def get_rel_val(self, pix):
        """:return value from 0 to self.range """
        return pix / self.pix_per_val

    def x_to_rel_value(self, x):
        """ x if with relative to canvas left side """
        return self.get_rel_val(x - self.slider_or)

    def _parse_rel_val(self, rel_val):
        if rel_val < 0:
            return 0
        if rel_val > self.range:
            return self.range
        return rel_val

    def get_rel(self):
        return self.value - self.from_

    def set_rel(self, rel_value):
        """ rel_value : relative value (between 0 and self.range)"""
        rel_value = self._parse_rel_val(rel_value)
        __pix = rel_value * self.pix_per_val
        self.value = self.from_ + rel_value
        t1_x2 = self._slider_aowh + __pix
        t2_x1 = t1_x2 + self.slider_d

        self.coords(self.trough_1, self.trough1_x1, self.trough_y1, t1_x2, self.trough_y2)
        self.coords(self.trough_2, t2_x1, self.trough_y1, self.trough2_x2, self.trough_y2)
        self.coords(self.slider, t1_x2, self.slider_y1, t2_x1, self.slider_y2)

    # Absolute Methods (uses absolute value --> self.from_ - self.to)

    def _parse_val(self, val):
        if val < self.from_:
            return self.from_
        if val > self.to:
            return self.to
        return val

    def get_value(self, pix):
        """ :return absolute value """
        return self.from_ + self.get_rel_val(pix)

    def x_to_value(self, x):
        """ :return absolute value """
        return self.from_ + self.x_to_rel_value(x)

    def set(self, value):
        self.value = self._parse_val(value)
        __pix = self.pix
        t1_x2 = self._slider_aowh + __pix
        t2_x1 = t1_x2 + self.slider_d

        self.coords(self.trough_1, self.trough1_x1, self.trough_y1, t1_x2, self.trough_y2)
        self.coords(self.trough_2, t2_x1, self.trough_y1, self.trough2_x2, self.trough_y2)
        self.coords(self.slider, t1_x2, self.slider_y1, t2_x1, self.slider_y2)

    def get(self):
        return self.value

    # ..................................   Methods which control Appearance of Scale   ..............................
    def active_ui(self):
        self.itemconfigure(self.slider, width=self.slider_aow, fill=self.slider_a_fill, outline=self.slider_aoc)

    def normal_ui(self):
        self.itemconfigure(self.slider, width=self.slider_ow, fill=self.slider_fill, outline=self.slider_oc)

    def _motion_handler(self, event):
        self.set_rel(self.x_to_rel_value(event.x))
        if self.motion_call:
            self.motion_call(event)

    def _click_press_handler(self, event):
        self.active_ui()
        if self.slider_click:
            self.set_rel(self.x_to_rel_value(event.x))
            if self.click_call:
                self.click_call(event)
        else:
            if not self.over_slider(event.x, event.y):
                self.set_rel(self.x_to_rel_value(event.x))
                if self.click_call:
                    self.click_call(event)

    def _click_release_handler(self, event):
        self.normal_ui()

    def resize(self, event=None):
        self.set(self.value)

    def hide_slider(self):
        self.itemconfigure(self.slider, fill='', width=0)

    def show_slider(self):
        self.itemconfigure(self.slider, fill=self.slider_fill, width=self.slider_ow)

    def disable(self):
        self.hide_slider()

        self.coords(self.trough_1, self.trough1_x1, self.trough_y1, self.trough1_x1, self.trough_y2)
        self.coords(self.trough_2, self.trough1_x1, self.trough_y1, self.trough2_x2, self.trough_y2)

        self.configure(state='disabled')
        self.unbind('<ButtonPress-1>')
        self.unbind('<ButtonRelease-1>')
        self.tag_unbind(self.slider, '<B1-Motion>')

    def enable(self):
        if self.cget('state') == 'disabled':
            self.configure(state='normal')
            self.tag_bind(self.slider, '<B1-Motion>', self._motion_handler)
            self.bind('<ButtonPress-1>', self._click_press_handler)
            self.bind('<ButtonRelease-1>', self._click_release_handler)

            self.set_rel(self.rel_value)
            self.show_slider()
    # ................................................................................................................
