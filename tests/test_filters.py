from aleph import filters


def test_highlight():
    assert filters.highlight(None, None) is None
    assert filters.highlight('', 'World') == ''
    assert filters.highlight('Hello, World!', None) == 'Hello, World!'
    assert filters.highlight('Hello, World!', '', None) == 'Hello, World!'
    assert filters.highlight('Hello, World!', 'World', '') == 'Hello, World!'
    assert filters.highlight('Hello, World!', 'World', None) == 'Hello, World!'
    assert filters.highlight('Hello, World!', 'World') == 'Hello, <mark>World</mark>!'
    assert filters.highlight('Hello, World!', 'World', 'b') == 'Hello, <b>World</b>!'
    assert filters.highlight('Hello, World!', 'Hello, World!') == '<mark>Hello, World!</mark>'


def test_phone_number():
    assert filters.phone_number(None) is None
    assert filters.phone_number('') == ''
    assert filters.phone_number('663972275') == '663 972 275'
