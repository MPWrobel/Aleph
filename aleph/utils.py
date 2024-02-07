from functools import wraps
from unicodedata import decomposition
from flask import request, render_template


# TODO: Replace with a solution which support alphabets of various languages
def ascii(string):
    output = ''
    for char in string:
        if ord(char) < 128:
            output += char
            continue
        if char == 'Ł':
            output += 'L'
            continue
        if char == 'ł':
            output += 'l'
            continue
        decomposed = decomposition(char)
        output += chr(int(decomposed.split()[0], 16)) if decomposed else '_'
    return output


# BUG: Ź and Ż are treated the same
def unicmp(s1, s2):
    for c1, c2 in zip(s1, s2):
        a1, a2 = ascii(c1), ascii(c2)
        o1, o2 = ord(a1), ord(a2)
        if o1 > o2:
            return 1
        elif o1 < o2:
            return -1
        elif a1 != c1 and a2 == c2:
            return 1
        elif a1 == c1 and a2 != c2:
            return -1
        else:
            continue
    return 0


def choices(choices, no_choice, value_field, text_fields):
    return [*((None, no_choice), (None, '', {'disabled': ''})),
            *((choice[value_field], ' '.join(choice[text_field]
                                             for text_field in text_fields))
              for choice in choices)]


def templated(func, template=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        template_name = f"{request.endpoint.replace('.', '/')}.html"
        response = func(*args, **kwargs)
        if type(response) is dict:
            return render_template(template_name, **response)
        else:
            return response
    return wrapper
