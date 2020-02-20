#!python3
from typing import Callable
import curses
import curses.ascii
import locale


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def testenc(e: str) -> str:
    return "base64ed: " + e


class needAsk():
    def __init__(self, message: str, hook: Callable[[str], str], validator: Callable[[str], bool], value: str = None):
        self.message = message
        self.hook = hook
        self.value = value
        self.validator = validator

    def SetVal(self, val: str) -> None:
        self.value = val

    def GetVal(self) -> str:
        return self.hook(self.value)

    def Validate(self) -> bool:
        return self.validator(self.value)


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

    def render(self, active: bool = False):
        try:
            mes = self.val[self.ox:self.ox + self.mx]
            if self.ox > 0:
                x = self.x - self.ox
            else:
                x = self.x

            if len(mes) < self.mx:
                mes = mes + " " * (self.mx - len(mes))

            if active:
                if self.validator is not None and self.validator(self.val):
                    self.window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_UNDERLINE)
                else:
                    self.window.addstr(0, len(self.R_OVER_CHAR), mes, curses.A_BOLD | curses.A_REVERSE)
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


def noAction(e: str) -> str:
    return e


def noValidate(e: str) -> bool:
    return True


class Object():
    def __init__(self):
        self.dictonary = {}

    def AddQ(self, key: str, *,
             message: str = "",
             default: str = None,
             hook: Callable[[str], str] = None,
             validator: Callable[[str], bool] = None,
             overwrite: bool = False) -> None:

        if message is None or message == "":
            message = key

        if hook is None:
            hook = noAction

        if validator is None:
            validator = noValidate

        if overwrite or not (key in self.dictonary):
            self.dictonary[key] = needAsk(message, hook, validator, default)

        return None

    def Ask(self) -> dict:
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

        # init subwindows and print messages
        idx = 0
        actidx = 0
        subwins = {}
        meswins = {}
        pos_y = 0
        for key in self.dictonary:
            message = self.dictonary[key].message
            if len(message) > max_x:
                message = message[:max_x-3] + "..."
            meswins[idx] = stdscr.derwin(1, win_x - 1, y, 0)
            meswins[idx].addstr(0, 0, message, curses.A_DIM | curses.A_LOW)
            meswins[idx].refresh(0, 0, 0, 0, 0, 0)
            # stdscr.addstr(y, x, message, curses.A_REVERSE)
            y += 1
            if win_y <= y:
                stdscr.resize(y + 1, win_x)
            stdscr.addstr(y, x, key)
            stdscr.addstr(y, keylen - 2, ':')
            subwins[idx] = subwin(stdscr, keylen, y, self.dictonary[key].validator)
            if not self.dictonary[key].value is None:
                subwins[idx].ins_str(self.dictonary[key].value)
                subwins[idx].render()
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

        # first render
        now_y, now_x = subwins[actidx].getpos()
        if pos_y > now_y:
            pos_y = now_y - 1
        if now_y - pos_y > win_y - 1:
            pos_y = now_y - win_y + 1
        subwins[actidx].render(active=True)
        stdscr.move(now_y, now_x)
        stdscr.refresh(pos_y, 0, 0, 0, win_y - 1, win_x - 1)

        clog = []
        while True:
            act = ""    # for debug

            # get key and log
            key = stdscr.getch()
            if len(clog) > 10:
                clog.pop(0)
            clog.append(str(key))

            # now_y, now_x = actwin.getyx()
            now_x = subwins[actidx].x

            # end with Ctrl+X
            if key == curses.ascii.CAN:
                break

            # delete
            elif key in (curses.ascii.BS, curses.ascii.DEL, curses.KEY_BACKSPACE):
                act = "D"
                if now_x > 0:
                    subwins[actidx].del_str(now_x)

            # →
            elif key == curses.KEY_RIGHT:
                act = "→"
                subwins[actidx].move_x(1)
            # ←
            elif key == curses.KEY_LEFT:
                act = "←"
                # if now_x > 0:
                subwins[actidx].move_x(-1)
            # ↓
            elif key in (curses.KEY_DOWN, curses.ascii.NL):
                act = "↓"
                if len(subwins) > actidx+1:
                    actidx += 1
                else:
                    break
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
                # ignore overrange input
                # TODO: Scroll or expand rect
                # if now_x == max_x and now_y == max_y:
                #     pass
                # End with last line enter
                if actidx >= len(subwins) and key in (curses.KEY_ENTER, 10):
                    break
                # overwise add char
                else:
                    act = "P"
                    subwins[actidx].ins_str(chr(key))

            # debug
            if False:
                stdscr.addstr(19, 20, 'idx' + str(actidx) + "/" + str(len(subwins)) + " - " + act)
                stdscr.addstr(20, 20, 'max/min ' + str(max_y) + ':' + str(keylen))
                stdscr.addstr(21, 0, ",".join(clog))
                for subw in subwins:
                    stdscr.addstr(22 + subw, 0, str(subw) + "-" + str(subwins[subw].x) + " : ox" + str(subwins[subw].ox) + " : mx" + str(subwins[subw].mx) + " : len" + str(len(subwins[subw].val)))

            # for idx in meswins:
            #   meswins[idx].refresh()
            for idx in subwins:
                subwins[idx].render()
            subwins[actidx].render(active=True)

            now_y, now_x = subwins[actidx].getpos()
            if pos_y > now_y:
                pos_y = now_y - 1
            if now_y - pos_y > win_y - 1:
                pos_y = now_y - win_y + 1
            stdscr.move(now_y, now_x)
            stdscr.refresh(pos_y, 0, 0, 0, win_y - 1, win_x - 1)

        ret = {}
        idx = 0
        for key in self.dictonary:
            self.dictonary[key].SetVal(subwins[idx].val)
            idx += 1
            ret[key] = self.dictonary[key].GetVal()
        return ret

    def __str__(self):
        return str(self.dictonary)


def ValidTest(e: str) -> bool:
    return e.find('ng') < 0


if __name__ == '__main__':
    test = Object()
    test.AddQ("key", message="loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("key2", message="hoge-fuge", default=None)
    test.AddQ("key3", hook=testenc, validator=ValidTest)
    ret = test.Ask()
    test.AddQ("key4", hook=testenc, default="aaa")
    ret = test.Ask()
    print(ret)
