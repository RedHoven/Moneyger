import curses

def main(stdscr):
    stdscr.clear()
    stdscr.addstr("Press keys to see their keycodes. Press 'q' to quit.\n")
    stdscr.refresh()

    while True:
        key = stdscr.get_wch()

        if isinstance(key, str):
            # For printable characters, display the keqycode as an integer
            stdscr.addstr(f"Key: {key}, Keycode: {ord(key)}\n")
        elif isinstance(key, int):
            # For special keys, display the key as a string and the keycode
            stdscr.addstr(f"Special Key: {curses.keyname(key)}, Keycode: {key}\n")

        stdscr.refresh()

        if key == 'q':
            break

curses.wrapper(main)

# import curses

# def main(stdscr):
#     stdscr.clear()
#     stdscr.addstr("Press keys to see their raw byte strings. Press 'q' to quit.\n")
#     stdscr.refresh()

#     while True:
#         key = stdscr.get_wch()
        
#         # Check if the key is a byte string
#         if isinstance(key, bytes):
#             # Convert the bytes to a printable string
#             key_str = repr(key)[2:-1]
#             stdscr.addstr(f"Key: {key_str}\n")
#         else:
#             stdscr.addstr(f"Key: {key}\n")

#         stdscr.refresh()

#         if key == 'q':
#             break

# curses.wrapper(main)
