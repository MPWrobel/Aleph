import sqlite3

from flask import abort, current_app, Flask, g, request, render_template
from functools import wraps
from os import path

from .utils import templated


def init_app(app: Flask):
    def close_db(e=None):
        if 'db' not in g:
            return

        g.db.close()
        del g.db

    app.teardown_appcontext(close_db)


def get_db(login_required=True):
    if login_required and not g.user:
        abort(403)

    if 'db' in g:
        return g.db

    g.db = Database()

    return g.db


def confirm(table, name_column, message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'GET':
                items = []
                for id in request.args.getlist('id'):
                    item = getattr(get_db(), table).fetchone(id)
                    items.append({'id': item['rowid'],
                                  'name': item[name_column]})
                return render_template('bulk_dialog.html',
                                       table=table,
                                       message=message,
                                       items=items)
            return func()
        return wrapper
    return decorator


def fetchone(table):
    def decorator(func):
        @wraps(func)
        @templated
        def wrapper(*args, **kwargs):
            id  = kwargs.get('id')
            row = getattr(get_db(), table).fetchone(id)
            if row is None:
                abort(404)
            return func(row)
        return wrapper
    return decorator


def fetchall(table):
    def decorator(func):
        @wraps(func)
        @templated
        def wrapper(*args, **kwargs):
            rows = getattr(get_db(), table).fetchall(
                query=request.args.get('search'),
                order_by=request.args.get('sort'),
                desc=request.args.get('desc') == "true")
            if rows is None:
                abort(404)
            return func(rows)
        return wrapper
    return decorator


class Database:
    tables     = []
    collations = []

    def __init__(self):
        database_path = path.join(current_app.instance_path,
                                  current_app.config['DATABASE'])
        self.con = sqlite3.connect(database_path)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        for collation in self.collations:
            self.con.create_collation(collation.__name__, collation)

        for Table in self.tables:
            Table.db = self
            setattr(self, Table.__name__.lower(), Table())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @property
    def lastrowid(self):
        return self.cur.lastrowid

    def close(self):
        self.cur.close()
        self.con.close()

    def execute(self, sql, *args, **kwargs):
        return self.cur.execute(sql, args or kwargs)

    def executescript(self, sql_script):
        self.cur.executescript(sql_script)

    def executefile(self, sql_file):
        with open(sql_file) as f:
            self.executescript(f.read())

    def commit(self):
        return self.con.commit()

    def collation(collation):
        Database.collations.append(collation)
        return collation

    def table(cls):
        Database.tables.append(cls)
        return cls


# TODO: Replace with a proper solution like ICU
@Database.collation
def unicmp(s1, s2):
    from .utils import ascii
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


@Database.collation
def natcmp(s1, s2):
    n1, n2 = [], []

    for c1 in s1:
        if c1.isdigit():
            n1.append(c1)
        elif n1:
            break
    for c2 in s2:
        if c2.isdigit():
            n2.append(c2)
        elif n2:
            break

    if n1 and n2:
        s1 = int(''.join(n1))
        s2 = int(''.join(n2))
    else:
        return unicmp(s1, s2)

    if s1 > s2:
        return 1
    elif s1 < s2:
        return -1
    else:
        return 0


class Table:
    view      = None
    columns   = ('',)
    search_by = ''
    sort_by   = ('',)
    natural_sort = False

    def __init__(self):
        self.table = self.__class__.__name__
        self.table_or_view = self.view or self.table

    def commit(self):
        return self.db.commit()

    def insert(self, data):
        bind = ', '.join(f':{column}' for column in self.columns)
        data = {column: data.get(column) for column in self.columns}
        SQL = f"INSERT INTO {self.table} VALUES ({bind})"
        self.db.execute(SQL, **data)

    def update(self, id, data):
        data = {key: val for key, val in data.items() if key in self.columns}
        bind = ', '.join(f"{key} = :{key}" for key in data)
        SQL = f"UPDATE {self.table} SET {bind} WHERE rowid = :rowid"
        self.db.execute(SQL, rowid=id, **data)

    def delete(self, id):
        SQL = f"DELETE FROM {self.table} WHERE rowid = ?"
        return self.db.execute(SQL, id)

    def count(self):
        SQL = f"SELECT COUNT() AS count FROM {self.table_or_view}"
        return self.db.execute(SQL).fetchone()['count']

    def fetchall(self, query=None, order_by=None, desc=False):
        SQL = [f"SELECT * FROM {self.table_or_view}"]
        ARGS = []
        if query:
            SQL.append(f"WHERE {self.search_by} LIKE ?")
            ARGS.append(f'%{query}%')
        if order_by in self.sort_by or (order_by := self.sort_by[0]):
            SQL.append(f"ORDER BY {order_by}")
            if self.natural_sort:
                SQL.append("COLLATE natcmp")
            if (desc):
                SQL.append("DESC")
        return self.db.execute('\n'.join(SQL), *ARGS).fetchall()

    def fetchone(self, id):
        SQL = f"SELECT * FROM {self.table_or_view} WHERE rowid = ?"
        return self.db.execute(SQL, id).fetchone()

    def fetchoneby(self, column, value):
        if column not in self.columns:
            return None
        SQL = f'SELECT * FROM {self.table_or_view} WHERE {column} LIKE ?'
        return self.db.execute(SQL, value).fetchone()

    def fetchallby(self, column, value):
        if column not in self.columns:
            return None
        SQL = f'SELECT * FROM {self.table_or_view} WHERE {column} LIKE ?'
        return self.db.execute(SQL, value).fetchall()
