#!python3
from typing import Callable
import curses
import curses.ascii
import locale


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class needAsk():
    def __init__(self,
                 message: str,
                 hook: Callable[[str], str],
                 validator: Callable[[str], bool],
                 value: str = None,
                 wrap: bool = None):
        self.message = message
        self.hook = hook
        self.value = value
        self.validator = validator
        self.__freeze = False
        self.wrap = wrap

    def SetVal(self, val: str) -> None:
        self.value = val

    def GetVal(self) -> str:
        return self.hook(self.value)

    def Validate(self) -> bool:
        return self.validator(self.value)

    def freeze(self) -> None:
        self.__freeze = True

    def isFreeze(self) -> bool:
        return self.__freeze

    def unfreeze(self) -> None:
        self.__freeze = False


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


def noAction(e: str) -> str:
    return e


def noValidate(e: str) -> bool:
    return True


class Object():
    def __init__(self, *, verbose: str = "", default_wrap: bool = False):
        self.verbose = verbose
        self.dictonary = {}
        self.wrap_mode = default_wrap

    def setVerbose(self, verbose: str):
        self.verbose = verbose

    def AddQ(self, key: str, *,
             message: str = "",
             default: str = None,
             hook: Callable[[str], str] = None,
             validator: Callable[[str], bool] = None,
             message_wrap: bool = None,
             overwrite: bool = False) -> None:

        if message is None or message == "":
            message = key

        if hook is None:
            hook = noAction

        if validator is None:
            validator = noValidate

        if overwrite or not (key in self.dictonary):
            self.dictonary[key] = needAsk(message, hook, validator, default, message_wrap)
        elif key in self.dictonary:
            self.dictonary[key].unfreeze()

        return None

    def freeze(self, key: str = None) -> bool:
        if key is None:
            for key in self.dictonary:
                self.dictonary[key].freeze()
        elif key in self.dictonary:
            self.dictonary[key].freeze()
        else:
            return False
        return True

    def Ask(self, *, override_wrap: bool = None) -> dict:
        self.override_wrap = override_wrap
        return curses.wrapper(self.__ask)

    def __ask(self, stdscr) -> dict:
        win_y, win_x = stdscr.getmaxyx()
        stdscr = curses.newpad(win_y, win_x)
        # calc key max length
        keylen = 0
        for key in self.dictonary:
            if keylen < len(key):
                keylen = len(key)
        keylen += 3

        # setup
        stdscr.clear()
        x = 0
        y = 0

        # get window size max
        max_x = win_x - 1 - keylen

        # print verbose
        for l in self.verbose.splitlines(False):
            stdscr.addnstr(y, 0, l, max_x)
            y += 1

        stdscr.hline(y, 0, '-', max_x)
        y += 1

        # init subwindows and print messages
        idx = 0
        actidx = 0
        subwins = {}
        meswins = {}
        for key in self.dictonary:
            if self.dictonary[key].isFreeze():
                continue
            message = self.dictonary[key].message

            wrap = self.override_wrap
            if wrap is None:
                wrap = self.dictonary[key].wrap
            if wrap is None:
                wrap = self.wrap_mode

            meswins[idx] = comwin(stdscr, y, message, wrap=wrap)
            meswins[idx].render()
            y += meswins[idx].h

            stdscr.addstr(y, x, key)
            stdscr.addstr(y, keylen - 2, ':')
            subwins[idx] = {"key": key, "win": subwin(stdscr, keylen, y, self.dictonary[key].validator)}
            if not self.dictonary[key].value is None:
                subwins[idx]["win"].ins_str(self.dictonary[key].value)
                subwins[idx]["win"].render()
                if actidx == idx and len(self.dictonary) >= actidx + 1:
                    actidx += 1
            idx += 1
            y += 1
            if win_y <= y:
                stdscr.resize(y + 1, win_x)
        if actidx >= len(subwins):
            actidx = len(subwins)-1
        max_y = y - 1   # calc printable size

        # enable scroll
        stdscr.scrollok(True)
        stdscr.idlok(True)
        stdscr.keypad(True)

        def checkValid():
            for idx in subwins:
                if not subwins[idx]["win"].validate():
                    return False
            return True

        def render():
            pos_y = 0
            now_y, now_x = subwins[actidx]["win"].getpos()
            if pos_y > now_y:
                pos_y = now_y - 1
            if now_y - pos_y > win_y - 1:
                pos_y = now_y - win_y + 1
            subwins[actidx]["win"].render(active=True)
            stdscr.move(now_y, now_x)
            stdscr.refresh(pos_y, 0, 0, 0, win_y - 1, win_x - 1)

        # first render
        render()

        clog = []
        while True:
            act = ""    # for debug

            # get key and log
            key = stdscr.getch()
            if len(clog) > 10:
                clog.pop(0)
            clog.append(str(key))

            # now_y, now_x = actwin.getyx()
            now_x = subwins[actidx]["win"].x

            # end with Ctrl+X
            if key == curses.ascii.CAN:
                if not checkValid():
                    curses.beep()
                    curses.flash()
                    continue
                break

            # delete
            elif key in (curses.ascii.BS, curses.ascii.DEL, curses.KEY_BACKSPACE):
                act = "D"
                if now_x > 0:
                    subwins[actidx]["win"].del_str(now_x)

            # →
            elif key == curses.KEY_RIGHT:
                act = "→"
                subwins[actidx]["win"].move_x(1)
            # ←
            elif key == curses.KEY_LEFT:
                act = "←"
                # if now_x > 0:
                subwins[actidx]["win"].move_x(-1)
            # ↓
            elif key == curses.KEY_DOWN:
                act = "↓"
                if len(subwins) > actidx+1:
                    actidx += 1
                else:
                    continue
            # Enter
            elif key in (curses.KEY_ENTER, curses.ascii.NL):
                act = "E"
                if len(subwins) > actidx+1:
                    actidx += 1
                elif checkValid():
                    break
                else:
                    curses.beep()
                    curses.flash()
                    continue
            # ↑
            elif key in (curses.KEY_UP, curses.ascii.VT):
                act = "↑"
                if actidx > 0:
                    actidx -= 1

            # alt
            elif key == 27:
                pass

            # Other
            else:
                act = "P"
                subwins[actidx]["win"].ins_str(chr(key))

            # debug
            if False:
                stdscr.addstr(19, 20, 'idx' + str(actidx) + "/" + str(len(subwins)) + " - " + act)
                stdscr.addstr(20, 20, 'max/min ' + str(max_y) + ':' + str(keylen))
                stdscr.addstr(21, 0, ",".join(clog))
                # for subw in subwins:
                #   stdscr.addstr(22 + subw, 0, str(subw) + "-" + str(subwins[subw].x) + " : ox" + str(subwins[subw].ox) + " : "
                #   + "mx" + str(subwins[subw].mx) + " : len" + str(len(subwins[subw].val)))

            # for idx in meswins:
            #   meswins[idx].refresh()
            for idx in subwins:
                subwins[idx]["win"].render()
            subwins[actidx]["win"].render(active=True)

            render()

        ret = {}
        idx = 0
        for key in self.dictonary:
            for idx in subwins:
                if subwins[idx]["key"] == key:
                    self.dictonary[key].SetVal(subwins[idx]["win"].val)
            ret[key] = self.dictonary[key].GetVal()
        return ret

    def __str__(self):
        return str(self.dictonary)
