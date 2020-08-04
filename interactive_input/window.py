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
        self.__win_y, win_x = parent.getmaxyx()
        self.__px = x
        self.__py = y
        self.__mx = win_x - self.__px - 1 - len(self.R_OVER_CHAR) - len(self.L_OVER_CHAR)
        self.__window = parent.derwin(1, self.__mx + len(self.R_OVER_CHAR) + len(self.L_OVER_CHAR), self.__py, self.__px)
        self.x = 0
        self.__y = 0
        self.__ox = 0
        self.val = ""
        self.__validator = validator

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
        if self.__ox > 0:
            self.__ox -= 1
        return self.val

    def l_over(self) -> bool:
        return self.__ox > 0

    def r_over(self) -> bool:
        return len(self.val) >= self.__ox + self.__mx

    def cur(self) -> int:
        return self.x - self.__ox

    def move_x(self, n: int) -> None:
        self.x += n
        if self.x <= 0:
            self.x = 0
        if self.cur() >= self.__mx:
            self.__ox += self.cur() - self.__mx + 1
        if self.cur() <= 0:
            self.__ox += self.cur()

    def getpos(self) -> (int, int):
        y, x = self.__window.getyx()
        return y + self.__py, x + self.__px

    def validate(self) -> bool:
        return self.__validator is None or self.__validator(self.val)

    def render(self, active: bool = False):
        try:
            mes = self.val[self.__ox:self.__ox + self.__mx]
            if self.__ox > 0:
                x = self.x - self.__ox
            else:
                x = self.x

            if len(mes) < self.__mx:
                mes = mes + " " * (self.__mx - len(mes))

            if not self.validate():
                self.__window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_REVERSE)
            else:
                if active:
                    self.__window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_UNDERLINE)
                else:
                    self.__window.addstr(0, len(self.R_OVER_CHAR), mes)

            if self.l_over():
                self.__window.addstr(0, 0, self.L_OVER_CHAR, curses.A_REVERSE)
            else:
                self.__window.addstr(0, 0, " " * len(self.L_OVER_CHAR))
            if self.r_over():
                self.__window.addstr(0, self.__mx, self.R_OVER_CHAR, curses.A_REVERSE)
            else:
                self.__window.addstr(0, self.__mx, " " * len(self.R_OVER_CHAR))

            if self.__win_y > self.__py + self.__y and self.__py + self.__y > 0:
                # self.__window.mvderwin(self.__py + self.__y, self.__px)
                self.__window.move(0, x + 1)
                self.__window.syncup()
                # self.__window.refresh()
        except BaseException as e:
            pass
            # print(e)

    def __str__(self):
        return self.val


class comwin():
    def __init__(self, stdscr, py: int, message: str, *, wrap: bool = False):
        win_y, win_x = stdscr.getmaxyx()
        self.__py = py
        self.__messages = {}
        self.h = 0

        while len(message) > win_x or message.find('\n') != -1:
            if wrap:
                plf = message.find('\n')
                le = win_x
                if 0 <= plf and plf < win_x:
                    le = plf
                    self.__messages[self.h] = message[:le]
                    message = message[le+1:]
                else:
                    self.__messages[self.h] = message[:le]
                    message = message[le:]
                self.h += 1
            else:
                message.replace('\n', ' ')
                message = message[:win_x-3] + "..."
                break

        self.__messages[self.h] = message
        self.h += 1
        if win_y <= self.__py + self.h:
            stdscr.resize(self.__py + self.h + 1, win_x)

        self.__window = stdscr.derwin(self.h, 0, self.__py, 0)
        # stdscr.addstr("comwin " + str(self.__py) + " " + str(self.h) + " " + str(self.__messages))
        # stdscr.refresh(0, 0, 0, 0, 20, max_x)

    def render(self):
        try:
            for mes in self.__messages:
                self.__window.addstr(mes, 0, self.__messages[mes], curses.A_DIM | curses.A_LOW)
            self.__window.syncup()
        except BaseException as e:
            pass
            # print(e)
        # self.__window.refresh(0, 0, 0, 0, self.h, self.__max_x)
