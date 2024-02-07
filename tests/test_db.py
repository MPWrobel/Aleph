import pytest
import sqlite3

from aleph.db import get_db


def row_to_tuple(row):
    return tuple(dict(row).items())


def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_close_db(app):
    with app.app_context():
        db = get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_parents_fetchchildren(app):
    with app.app_context():
        db = get_db()
        children = db.parents.fetchchildren(1)
    assert tuple(row_to_tuple(child)
                 for child in children) == ((('student_id', 1),
                                             ('first_name',
                                              'Abra'),
                                             ('last_name',
                                              'Letchford'),
                                             ('group_id', 10),
                                             ('parent_id', 1)),)


def test_parents_fetchone(app):
    with app.app_context():
        db = get_db()
        first = db.parents.fetchone(1)
        last  = db.parents.fetchone(100)
    assert row_to_tuple(first) == (('parent_id', 1),
                                   ('first_name', 'Tanitansy'),
                                   ('last_name', 'Letchford'),
                                   ('phone', '599644238'),
                                   ('email', 'tletchford0@fda.gov'))
    assert row_to_tuple(last) == (('parent_id', 100),
                                  ('first_name', 'Ermina'),
                                  ('last_name', 'Ruscoe'),
                                  ('phone', '899918062'),
                                  ('email', 'eruscoe2r@yelp.com'))


def test_students_fetchone(app):
    with app.app_context():
        db = get_db()
        first = db.students.fetchone(1)
        last  = db.students.fetchone(100)
    assert row_to_tuple(first) == (('student_id', 1),
                                   ('first_name', 'Abra'),
                                   ('last_name', 'Letchford'),
                                   ('group_id', 10),
                                   ('parent_id', 1))
    assert row_to_tuple(last) == (('student_id', 100),
                                  ('first_name', 'Yevette'),
                                  ('last_name', 'Ruscoe'),
                                  ('group_id', 1),
                                  ('parent_id', 100))


# TODO: To be implemented
def test_students_fetchsiblings(app):
    ...


def test_students_fetchbyparent(app):
    with app.app_context():
        db = get_db()
        student = db.students.fetchbyparent(1)
    assert row_to_tuple(student) == (('student_id', 1),
                                     ('first_name', 'Abra'),
                                     ('last_name', 'Letchford'),
                                     ('group_id', 10),
                                     ('parent_id', 1))


def test_students_fetchall(app):
    with app.app_context():
        db = get_db()
        students = db.students.fetchall()
    assert len(students) == 100
    assert row_to_tuple(students[0]) == (('student_id', 1),
                                         ('student_name', 'Letchford Abra'),
                                         ('parent_id', 1),
                                         ('parent_name', 'Letchford Tanitansy'),
                                         ('phone', '599644238'),
                                         ('email', 'tletchford0@fda.gov'),
                                         ('group_id', 10),
                                         ('group_name', 'Group 10'),
                                         ('group_level', 'CAE'))
