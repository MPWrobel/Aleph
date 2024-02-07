import re

from markupsafe import Markup


def filter(func):
    def wrapped(string, *args, **kwargs):
        if string is None:
            return
        return func(str(string), * args, **kwargs)
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


def init_app(app):
    app.jinja_env.filters['highlight'] = highlight
    app.jinja_env.filters['phone_number'] = phone_number
    app.jinja_env.filters['nbsp'] = nbsp
