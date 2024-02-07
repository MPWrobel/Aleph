import sqlite3

from flask import current_app, Flask, g
from os import path

from .utils import unicmp


def init_app(app: Flask):
    def close_db(e=None):
        if 'db' not in g:
            return

        g.db.close()
        del g.db

    app.teardown_appcontext(close_db)


def get_db():
    if 'db' in g:
        return g.db

    g.db = Database()

    return g.db


class Database:
    tables = []

    def __init__(self):
        database_path = path.join(current_app.instance_path,
                                  current_app.config['DATABASE'])
        self.con = sqlite3.connect(database_path)
        self.con.row_factory = sqlite3.Row
        self.con.create_collation('unicode', unicmp)
        self.cur = self.con.cursor()

        for Table in Database.tables:
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

    def table(cls):
        Database.tables.append(cls)
        return cls


class Table:
    columns = tuple()

    def insert(self, data):
        bind = ', '.join(f':{column}' for column in self.columns)
        data = {column: data.get(column) for column in self.columns}
        SQL = f"INSERT INTO {self.__class__.__name__} VALUES ({bind})"
        self.db.execute(SQL, **data)

    def update(self, id, data):
        data = {key: val for key, val in data.items() if key in self.columns}
        bind = ', '.join(f"{key} = :{key}" for key in data)
        SQL = f"UPDATE {self.__class__.__name__} SET {bind} WHERE rowid = :rowid"
        self.db.execute(SQL, rowid=id, **data)

    def count(self):
        SQL = f"SELECT COUNT() AS count FROM {self.__class__.__name__}"
        return self.db.execute(SQL).fetchone()['count']

    def fetchall(self):
        SQL = f"SELECT * FROM {self.__class__.__name__}"
        return self.db.execute(SQL).fetchall()

    def fetchone(self, id):
        SQL = f"SELECT * FROM {self.__class__.__name__} WHERE rowid = ?"
        return self.db.execute(SQL, id).fetchone()


@Database.table
class Users(Table):
    columns = ('user_id', 'username', 'password')

    def fetchbyusername(self, username):
        SQL = 'SELECT * FROM users WHERE username LIKE ?'
        return self.db.execute(SQL, username).fetchone()


@Database.table
class Parents(Table):
    columns = ('parent_id',
               'first_name', 'last_name',
               'phone', 'email')

    def fetchchildren(self, id):
        SQL = "SELECT * FROM Students WHERE parent_id = ?"
        return self.db.execute(SQL, id).fetchall()

    def fetchnames(self):
        SQL = "SELECT parent_id, first_name, last_name FROM Parents"
        return self.db.execute(SQL).fetchall()


@Database.table
class Students(Table):
    columns = ('student_id',
               'first_name', 'last_name',
               'group_id', 'parent_id')

    def fetchsiblings(self, id):
        SQL = """SELECT Sibling.*, ? AS id FROM StudentsView Student
JOIN StudentsView Sibling ON Student.parent_id = Sibling.parent_id
WHERE Student.student_id = id AND Sibling.student_id != id"""
        return self.db.execute(SQL, id).fetchall()

    # TODO: Add unicode-insensitive search
    def fetchall(self, query=None, order_by=None):
        SQL = ["SELECT * FROM StudentsView"]
        ARGS = []
        if query:
            SQL.append("WHERE student_name LIKE ?")
            ARGS.append(f'%{query}%')
        if order_by in self.columns:
            SQL.append(f"ORDER BY {order_by} COLLATE unicode")
        print(SQL, ARGS)
        return self.db.execute('\n'.join(SQL), *ARGS).fetchall()

    def fetchnames(self):
        SQL = "SELECT student_id, first_name, last_name FROM Students"
        return self.db.execute(SQL).fetchall()

    # TODO: Consider generalizing fetchby methods
    def fetchbyparent(self, id):
        SQL = "SELECT * FROM Students WHERE parent_id = ?"
        return self.db.execute(SQL, id).fetchone()


@Database.table
class Groups(Table):
    def fetchone(self, id):
        SQL = "SELECT * FROM GroupsView WHERE group_id = ?"
        return self.db.execute(SQL, id).fetchone()

    def fetchall(self):
        SQL = "SELECT * FROM GroupsView"
        return self.db.execute(SQL).fetchall()

    # TODO: Rename to fetchgroup and move to Students
    def fetchmembers(self, id):
        SQL = "SELECT * FROM StudentsView WHERE group_id = ?"
        return self.db.execute(SQL, id).fetchall()


@Database.table
class GroupLevels(Table):
    pass


@Database.table
class Payments(Table):
    columns = ('payer', 'title', 'sum', 'date', 'student_id')

    def fetchall(self):
        SQL = """SELECT *
FROM Payments
LEFT JOIN Students ON Payments.student_id = Students.student_id"""
        return self.db.execute(SQL).fetchall()

    def fetchnotassigned(self):
        SQL = "SELECT * FROM Payments WHERE student_id IS NULL"
        return self.db.execute(SQL).fetchall()

    def fetchone(self, id):
        SQL = """SELECT * FROM Payments
LEFT JOIN Students ON Payments.student_id = Students.student_id
WHERE payment_id = ?"""
        return self.db.execute(SQL, id).fetchone()

    def fetchbyparent(self, id):
        SQL = "SELECT * FROM PaymentsView WHERE parent_id = ?"
        return self.db.execute(SQL, id).fetchall()

    def updatestudent(self, payment_id, student_id):
        SQL = "UPDATE Payments SET student_id = ? WHERE payment_id = ?"
        self.db.execute(SQL, student_id, payment_id)
        self.db.commit()
