import re

from functools import wraps
from markupsafe import Markup

filters = []


def filter(func):
    @wraps(func)
    def wrapped(string, *args, **kwargs):
        if string is None:
            return
        return func(str(string), * args, **kwargs)
    filters.append(wrapped)
    return wrapped


# TODO: Add support for attributes
@filter
def highlight(string, substring, tag='mark'):
    if not (substring and tag):
        return Markup(string)
    begin_tag = f'<{tag}>'
    end_tag   = f'</{tag}>'
    return Markup(re.sub(f'({substring})', f'{begin_tag}\\1{end_tag}', string,
                         flags=re.IGNORECASE))


@filter
def phone_number(string):
    if len(string) == 9:
        return f'{string[0:3]} {string[3:6]} {string[6:9]}'
    else:
        return string


@filter
def nbsp(string):
    return Markup(string.replace(' ', '&nbsp;'))


@filter
def quotes(string):
    return Markup(f"'{string}'")


def init_app(app):
    for filter in filters:
        app.jinja_env.filters[filter.__name__] = filter
