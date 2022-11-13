def parse_int(string):
    s = ''
    f = 0
    for c in string:
        if c.isdigit():
            if c != '0' or f == 1:
                f = 1
                s += c
    return s

def parse_string(string):
    s = ''
    f = 0
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
        