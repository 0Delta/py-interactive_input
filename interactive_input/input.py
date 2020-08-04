#!python3
from typing import Callable
import curses
import locale

from . import window
from sys import maxsize


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

    def __str__(self):
        return "NeedAskObj:" + self.value

    def __repr__(self):
        from pprint import pformat
        return "<" + type(self).__name__ + "> " + pformat(vars(self),width=maxsize, compact=True)


def noAction(e: str) -> str:
    return e


def noValidate(e: str) -> bool:
    return True


class Object():
    def __init__(self, *, verbose: str = "", default_wrap: bool = False):
        self.__verbose = verbose
        self.__dictonary = {}
        self.__wrap_mode = default_wrap

    def setVerbose(self, verbose: str):
        self.__verbose = verbose

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

        if overwrite or not (key in self.__dictonary):
            self.__dictonary[key] = needAsk(message, hook, validator, default, message_wrap)
        elif key in self.__dictonary:
            self.__dictonary[key].unfreeze()

        return None

    def freeze(self, key: str = None) -> bool:
        if key is None:
            for key in self.__dictonary:
                self.__dictonary[key].freeze()
        elif key in self.__dictonary:
            self.__dictonary[key].freeze()
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
        for key in self.__dictonary:
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
        for l in self.__verbose.splitlines(False):
            stdscr.addnstr(y, 0, l, max_x)
            y += 1

        stdscr.hline(y, 0, '-', max_x)
        y += 1

        # init subwindows and print messages
        idx = 0
        actidx = 0
        subwins = {}
        meswins = {}
        for key in self.__dictonary:
            if self.__dictonary[key].isFreeze():
                continue
            message = self.__dictonary[key].message

            wrap = self.override_wrap
            if wrap is None:
                wrap = self.__dictonary[key].wrap
            if wrap is None:
                wrap = self.__wrap_mode

            meswins[idx] = window.comwin(stdscr, y, message, wrap=wrap)
            meswins[idx].render()
            y += meswins[idx].h

            stdscr.addstr(y, x, key)
            stdscr.addstr(y, keylen - 2, ':')
            subwins[idx] = {"key": key, "win": window.subwin(stdscr, keylen, y, self.__dictonary[key].validator)}
            if not self.__dictonary[key].value is None:
                subwins[idx]["win"].ins_str(self.__dictonary[key].value)
                subwins[idx]["win"].render()
                if actidx == idx and len(self.__dictonary) >= actidx + 1:
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
        for key in self.__dictonary:
            for idx in subwins:
                if subwins[idx]["key"] == key:
                    self.__dictonary[key].SetVal(subwins[idx]["win"].val)
            ret[key] = self.__dictonary[key].GetVal()
        return ret

    def __str__(self):
        return str(self.__dictonary)
