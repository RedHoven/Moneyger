import curses
import unicodedata

def is_printable_character(ch):
    # Check if the character is a printable letter, number, or symbol
    return unicodedata.category(ch).startswith('L') or \
           unicodedata.category(ch).startswith('N') or \
           unicodedata.category(ch).startswith('P') or \
           ch == ' '

def parse_wide_character(key):
    if isinstance(key, int):
        # Filter out command keys
        if curses.KEY_MIN <= key <= curses.KEY_MAX:
            return ''

        # Convert the integer keycode to a character
        return chr(key)

    elif isinstance(key, str):
        # Filter out non-printable characters
        if not is_printable_character(key):
            return ''

    # Return the valid wide character
    return key

def parse_int(string):
    s = ''
    f = 0
    for c in string:
        if c.isdigit():
            if c != '0' or f == 1:
                f = 1
                s += c
    return s

def parse_string_to_int(string):
    s = ''
    for c in string:
        if c.isdigit():
            s += c
    return s

def parse_string(string):
    s = ''
    for char in string:
        if ord(char) >= 65 and ord(char) <= 90:
            s += char
        elif ord(char) >= 97 and ord(char) <= 122:
            s += char
    return s

def update_sum_text(text, string, remove=False):
    if text != '' or parse_int(string) != '':
        new_text = parse_int(text + string)
        if remove:
            new_text = new_text[:-1]

        if len(new_text) < 3:
            zeros = '0' * (4 - len(new_text))
            new_text = zeros + new_text
        text = new_text[:-2] + '.' + new_text[-2:]
    return text

def update_text(text,string,remove=False):
    new_text = text
    new_text = parse_string(text + string)
    if remove:
        new_text = new_text[:-1]
    return new_text

def update_date(text,string,remove=False):
    if string == '-' or parse_string_to_int(string) != '':
        text = text+string
    elif remove and text != '':
        text = text[:-1]
    return text

def update_plain_text(text,string,remove=False):
    if remove and text != '':
        text = text[:-1]
    elif remove and text == "":
        pass
    else:
        text = text+string
    return text