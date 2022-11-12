import curses
from curses import wrapper


def main(stdscr):
    stdscr.clear()
    stdscr.addstr(10,10,'hello world',curses.A_DIM)
    stdscr.refresh()
    s = 0
    while s != 1:
        s = stdscr.getch()

wrapper(main)
