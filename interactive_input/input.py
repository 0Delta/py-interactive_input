#!python3
from typing import Callable
import curses
import curses.ascii
import locale


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def testenc(e: str) -> str:
    return "base64ed: " + e


class Object():
    def __init__(self):
        self.dictonary = {}

    def noAction(e: str) -> str:
        return e

    class __needAsk():
        def __init__(self, message: str, hook: Callable[[str], str], value: str = None):
            self.message = message
            self.hook = hook
            self.value = value

        def SetVal(self, val: str) -> None:
            self.value = val

        def GetVal(self) -> str:
            return self.hook(self.value)

    def AddQ(self, key: str, *,
             message: str = "",
             default: str = None,
             hook: Callable[[str], str] = noAction,
             overwrite: bool = False) -> None:

        if message is None or message == "":
            message = key

        if overwrite or not (key in self.dictonary):
            self.dictonary[key] = self.__needAsk(message, hook, default)

        return None

    def Ask(self) -> dict:
        return curses.wrapper(self.__ask)

    def __ask(self, stdscr) -> dict:
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
        _, max_x = stdscr.getmaxyx()
        max_x -= 1 + keylen

        # init subwindows and print messages
        actidx = 0
        subwins = []
        for key in self.dictonary:
            stdscr.addstr(y, x, self.dictonary[key].message, curses.A_REVERSE)
            y += 1
            stdscr.addstr(y, x, key)
            stdscr.addstr(y, keylen - 2, ':')
            subwins.append(stdscr.derwin(1, max_x - keylen, y, keylen))
            if not self.dictonary[key].value is None:
                subwins[actidx].addstr(0, 0, self.dictonary[key].value)
                actidx += 1
            y += 1
        if actidx >= len(subwins):
            actidx = len(subwins)-1
        max_y = y - 1   # calc printable size

        stdscr.refresh()

        clog = []
        while True:
            actwin = subwins[actidx]

            act = ""    # for debug

            # get key and log
            key = stdscr.getch()
            if len(clog) > 10:
                clog.pop(0)
            clog.append(str(key))

            now_y, now_x = actwin.getyx()

            # end with Ctrl+X
            if key == curses.ascii.CAN:
                break

            # delete
            elif key in (curses.ascii.BS, curses.ascii.DEL, curses.KEY_BACKSPACE):
                act = "D"
                if now_x > 0:
                    actwin.delch(now_y, now_x-1)
                    actwin.move(now_y, now_x-1)

            # →
            elif key == curses.KEY_RIGHT:
                act = "→"
                if now_x < max_x:
                    actwin.move(now_y, now_x+1)
            # ←
            elif key == curses.KEY_LEFT:
                act = "←"
                if now_x > keylen:
                    actwin.move(now_y, now_x-1)
            # ↓
            elif key in (curses.KEY_DOWN, curses.ascii.NL):
                act = "↓"
                if len(subwins) > actidx+1:
                    actidx += 1
                    actwin = subwins[actidx]
                else:
                    break
            # ↑
            elif key in (curses.KEY_UP, curses.ascii.VT):
                act = "↑"
                if actidx > 0:
                    actidx -= 1
                    actwin = subwins[actidx]

            # Other
            else:
                # ignore overrange input
                # TODO: Scroll or expand rect
                if now_x == max_x and now_y == max_y:
                    pass
                # End with last line enter
                elif now_y == max_y and key in (curses.KEY_ENTER, 10):
                    break
                # overwise add char
                else:
                    act = "P"
                    actwin.addch(now_y, now_x, key)

            # get cursole position
            now_y, now_x = actwin.getyx()
            # debug
            if False:
                stdscr.addstr(19, 20, 'idx' + str(actidx) + "/" + str(len(subwins)) + " - " + act)
                stdscr.addstr(20, 20, 'max/min ' + str(max_y) + ':' + str(keylen))
                stdscr.addstr(21, 20, 'now ' + str(now_y) + ':' + str(now_x))
                stdscr.addstr(22, 0, ",".join(clog))
                stdscr.refresh()

            actwin.move(now_y, now_x)
            actwin.refresh()

        rets = []
        for actwin in subwins:
            ret = b''
            i = 0
            while i < max_x:
                # INFO: in_wch is not exist in python3.8
                #       Need wait merge issue for non-ascii support
                #       https://bugs.python.org/issue39214
                c = (actwin.inch(0, i) & 0xFF)
                if c in (0, 32):
                    break
                ret += c.to_bytes(1, "big")
                i += 1
            rets.append(ret.decode(code, errors="replace"))

        ret = {}
        idx = 0
        for key in self.dictonary:
            self.dictonary[key].SetVal(rets[idx])
            idx += 1
            ret[key] = self.dictonary[key].GetVal()
        return ret

    def __str__(self):
        return self.dictonary


if __name__ == '__main__':
    test = Object()
    test.AddQ("key")
    test.AddQ("key2", message="hoge-fuge")
    test.AddQ("key3", hook=testenc)
    ret = test.Ask()
    test.AddQ("key4", hook=testenc, default="aaa")
    ret = test.Ask()
    print(ret)
