#!python3
from typing import Callable
import curses
import curses.ascii


class subwin():
    """

    px int:
        subwindow X position.

    py int:
        subwindow Y position.

    mx int:
        max length of printable value.

    window window:
        window object.

    x int:
        real cursole position.

    ox int:
        count of hidden value at left side.

    val str:
        value data
    """

    L_OVER_CHAR = "<"
    R_OVER_CHAR = ">"

    def __init__(self, parent, x: int, y: int, validator: Callable[[str], bool] = None):
        self.win_y, win_x = parent.getmaxyx()
        self.px = x
        self.py = y
        self.mx = win_x - self.px - 1 - len(self.R_OVER_CHAR) - len(self.L_OVER_CHAR)
        self.window = parent.derwin(1, self.mx + len(self.R_OVER_CHAR) + len(self.L_OVER_CHAR), self.py, self.px)
        self.x = 0
        self.y = 0
        self.ox = 0
        self.val = ""
        self.validator = validator

    def ins_str(self, insert_string):
        insert_string = str(insert_string)
        dist = len(self.val) - self.x
        if dist <= 0:
            self.val += (" " * (dist * -1))
        self.val = self.val[:self.x] + insert_string + self.val[self.x:]
        self.move_x(len(insert_string))
        return self.val

    def del_str(self, del_point):
        if len(self.val) >= del_point:
            self.val = self.val[:del_point-1] + self.val[del_point:]
        self.move_x(-1)
        if self.ox > 0:
            self.ox -= 1
        return self.val

    def l_over(self) -> bool:
        return self.ox > 0

    def r_over(self) -> bool:
        return len(self.val) >= self.ox + self.mx

    def cur(self) -> int:
        return self.x - self.ox

    def move_x(self, n: int) -> None:
        self.x += n
        if self.x <= 0:
            self.x = 0
        if self.cur() >= self.mx:
            self.ox += self.cur() - self.mx + 1
        if self.cur() <= 0:
            self.ox += self.cur()

    def getpos(self) -> (int, int):
        y, x = self.window.getyx()
        return y + self.py, x + self.px

    def validate(self) -> bool:
        return self.validator is None or self.validator(self.val)

    def render(self, active: bool = False):
        try:
            mes = self.val[self.ox:self.ox + self.mx]
            if self.ox > 0:
                x = self.x - self.ox
            else:
                x = self.x

            if len(mes) < self.mx:
                mes = mes + " " * (self.mx - len(mes))

            if not self.validate():
                self.window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_REVERSE)
            else:
                if active:
                    self.window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_UNDERLINE)
                else:
                    self.window.addstr(0, len(self.R_OVER_CHAR), mes)

            if self.l_over():
                self.window.addstr(0, 0, self.L_OVER_CHAR, curses.A_REVERSE)
            else:
                self.window.addstr(0, 0, " " * len(self.L_OVER_CHAR))
            if self.r_over():
                self.window.addstr(0, self.mx, self.R_OVER_CHAR, curses.A_REVERSE)
            else:
                self.window.addstr(0, self.mx, " " * len(self.R_OVER_CHAR))

            if self.win_y > self.py + self.y and self.py + self.y > 0:
                # self.window.mvderwin(self.py + self.y, self.px)
                self.window.move(0, x + 1)
                self.window.syncup()
                # self.window.refresh()
        except BaseException as e:
            print(e)

    def __str__(self):
        return self.val


class comwin():
    def __init__(self, stdscr, py: int, message: str, *, wrap: bool = False):
        win_y, win_x = stdscr.getmaxyx()
        self.py = py
        self.messages = {}
        self.h = 0

        while len(message) > win_x or message.find('\n') != -1:
            if wrap:
                plf = message.find('\n')
                le = win_x
                if 0 <= plf and plf < win_x:
                    le = plf
                    self.messages[self.h] = message[:le]
                    message = message[le+1:]
                else:
                    self.messages[self.h] = message[:le]
                    message = message[le:]
                self.h += 1
            else:
                message.replace('\n', ' ')
                message = message[:win_x-3] + "..."
                break

        self.messages[self.h] = message
        self.h += 1
        if win_y <= self.py + self.h:
            stdscr.resize(self.py + self.h + 1, win_x)

        self.window = stdscr.derwin(self.h, 0, self.py, 0)
        # stdscr.addstr("comwin " + str(self.py) + " " + str(self.h) + " " + str(self.messages))
        # stdscr.refresh(0, 0, 0, 0, 20, max_x)

    def render(self):
        try:
            for mes in self.messages:
                self.window.addstr(mes, 0, self.messages[mes], curses.A_DIM | curses.A_LOW)
            self.window.syncup()
        except BaseException as e:
            print(e)
        # self.window.refresh(0, 0, 0, 0, self.h, self.max_x)
