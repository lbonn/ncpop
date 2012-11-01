import curses
import locale
import os
import shlex
import signal
import sys

def _curse_mode(scr):
    curses.noecho()
    curses.cbreak()
    scr.keypad(1)

def _uncurse_mode(scr):
    curses.echo()
    curses.nocbreak()
    scr.keypad(0)

def _launch_work(scr, el, worker):
    # screen in normal mode
    scr.clear()
    scr.refresh()
    scr.move(0,0)
    _uncurse_mode(scr)

    ret = worker(el)

    # back to curse mode
    _curse_mode(scr)
    return ret == 0

def _disp_title(scr, title):
    scr.addstr(title + "\n")
    scr.addstr(''.join([ '-' for k in range(len(title)) ]) + "\n")

def _disp_choices(scr, els, sel):
    for k,c in enumerate(els):
        if k == sel:
            mode = curses.A_STANDOUT
        else:
            mode = curses.A_NORMAL
        scr.addstr(c + "\n",mode)

def _curse_engine(scr, title, els, worker):
    # encoding
    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    curses.use_default_colors()
    curses.curs_set(0)

    selected = 0

    while True:
        scr.move(0,0)
        _disp_title(scr, title)
        _disp_choices(scr, els, selected)
        scr.refresh()
        p_key = scr.getch()
        if p_key == curses.KEY_UP:
            if selected != 0:
                selected -= 1
        elif p_key == curses.KEY_DOWN:
            if selected != len(els)-1:
                selected += 1
        elif p_key == ord('q'):
            return 0
        elif p_key == ord('\n'):
            if _launch_work(scr, els[selected], worker):
                return 0
            else:
                scr.getch()
                scr.clear()

def _sigint_handler(signal, frame):
    sys.exit(0)

# ----

def exec_in_term(app, term_cmd):
    self_invoc = shlex.split("python3 {0} -go".format(app))

    term_i = shlex.split(term_cmd)
    cmd = term_i[0]
    args = term_i + ["-e"] + self_invoc
    os.execve(cmd, args, os.environ)

def popup(argv, title, els, worker):
    signal.signal(signal.SIGINT, _sigint_handler)
    curses.wrapper(_curse_engine, title, els, worker)
