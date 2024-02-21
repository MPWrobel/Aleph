from functools import wraps
from unicodedata import decomposition
from flask import request, render_template


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


def templated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        path = request.endpoint.split('.')
        template_name = f"{'/'.join(path)}.html"
        response = func(*args, **kwargs)
        if type(response) is dict:
            return render_template(template_name, path=path, **response)
        else:
            return response
    return wrapper
