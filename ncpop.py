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

def _disp_title(scr, title, t_size):
    if t_size[1] <= len(title):
        title = title[:t_size[1]-1]
    scr.addstr(title + "\n")
    scr.addstr(''.join([ '-' for k in range(len(title)) ]) + "\n")

def _flush_to_endline(scr, y, x):
    _,cap_x = scr.getmaxyx()
    if x < cap_x:
        scr.addstr(y, x, ''.join([ " " for k in range(x, cap_x-1)]))

def _disp_choices(scr, els, sel, t_size):
    y,_ = scr.getyx()
    for k in range(t_size[0]-y):
        if k >= len(els):
            _flush_to_endline(scr, y, 0)
            continue

        c = els[k]
        if t_size[1] < len(c):
            c = c[:t_size[1]-1]

        if k == sel:
            mode = curses.A_STANDOUT
        else:
            mode = curses.A_NORMAL
        scr.addstr(y, 0, c, mode)

        _flush_to_endline(scr, y, len(c))
        y += 1

def _comp_scroll(scr, selected, fst_disp):
    y,x = scr.getyx()
    cap_y,_ = scr.getmaxyx()
    n_disps = cap_y - y
    lst_disp = fst_disp + n_disps - 1

    if selected < fst_disp:
        fst_disp = selected
        lst_disp = fst_disp + n_disps - 1
    elif selected > lst_disp:
        fst_disp = selected - n_disps + 1
        lst_disp = selected

    return fst_disp,lst_disp

def _curse_engine(scr, title, els, worker):
    # encoding
    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    curses.use_default_colors()
    curses.curs_set(0)

    first_disp = 0
    selected = 0

    while True:
        t_size = list(scr.getmaxyx())

        if t_size[0] < 3:
            scr.refresh()
            continue

        # popup title
        scr.move(0,0)
        _disp_title(scr, title, t_size)

        # popup content
        first_disp, last_disp = _comp_scroll(scr, selected, first_disp)
        disp_width = last_disp - first_disp + 1
        _disp_choices(scr, els[first_disp:last_disp+1],
                selected - first_disp, t_size)

        scr.refresh()
        p_key = scr.getch()
        if p_key == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif p_key == curses.KEY_DOWN:
            selected = min(len(els)-1, selected + 1)
        elif p_key == curses.KEY_PPAGE:
            shift = disp_width//2
            selected = max(0, selected - shift)
            first_disp = max(0, first_disp - shift)
        elif p_key == curses.KEY_NPAGE:
            shift = disp_width//2
            selected = min(len(els)-1, selected + shift)
            first_disp = min(max(0,len(els)-disp_width), first_disp + shift)
        elif p_key == curses.KEY_HOME:
            selected = 0
        elif p_key == curses.KEY_END:
            selected = len(els)-1
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
