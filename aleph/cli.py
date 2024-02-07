from click import argument, echo, command, option
from flask import Flask
from pathlib import Path
from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash

from .db import get_db


def init_app(app: Flask):
    app.cli.add_command(init)
    app.cli.add_command(register)


@command('init', help='Initialize the database')
@option('--test-data', '-t', is_flag=True)
def init(test_data):
    echo('Initializing database... ', nl=False)
    db = get_db()
    db.executefile('aleph/schema.sql')
    echo('done')

    if (test_data):
        echo('Loading testing data... ')
        for sql_file in Path('tests/').glob('*.sql'):
            echo(f'\t{sql_file}')
            db.executefile(sql_file)
        echo('done')


@command('user', help='Manage users')
@option('--username', '-u')
@option('--password', '-p')
@argument('action')
def register(action, username, password):
    if action == 'add' and username and password:
        db = get_db()
        try:
            db.users.insert({'username': username,
                             'password': generate_password_hash(password)})
            db.commit()
            echo(f'{username} registered successfully')
        except IntegrityError:
            echo(f'User "{username}" already exists')
    else:
        echo('usage')
