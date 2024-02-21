from flask import Blueprint, flash, request, url_for, render_template

from .db import Database, Table, confirm, fetchall, fetchone, get_db
from .forms import StudentForm, ParentForm, validate
from .utils import templated

bp = Blueprint('students', __name__, url_prefix='/students')


@Database.table
class Parents(Table):
    columns = ('parent_id', 'first_name', 'last_name', 'phone', 'email')
    sort_by   = ('last_name', 'first_name')

    def fetchchildren(self, id):
        SQL = "SELECT * FROM StudentsView WHERE parent_id = ?"
        return self.db.execute(SQL, id).fetchall()

    def fetchnames(self):
        SQL = "SELECT parent_id, first_name, last_name FROM Parents"
        return self.db.execute(SQL).fetchall()

    # TODO: Replace with payments.fetchby('parent_id', id)
    def fetchpayments(self, id):
        SQL = "SELECT * FROM PaymentsView WHERE parent_id = ?"
        return self.db.execute(SQL, id).fetchall()


@Database.table
class Students(Table):
    view      = 'StudentsView'
    search_by = 'student_name'
    sort_by   = ('student_name', 'group_name')
    columns   = ('student_id', 'first_name',
                 'last_name', 'group_id', 'parent_id')

    def fetchnames(self):
        SQL = "SELECT student_id, first_name, last_name FROM Students"
        return self.db.execute(SQL).fetchall()


@bp.route('/')
@fetchall('students')
def index(students):
    return {'students': students}


@bp.route('<int:id>', methods=('GET', 'PUT'))
@fetchone('students')
def view(student):
    db = get_db()

    student_form = StudentForm(request.form, data=student, prefix='student')

    parent_id   = (request.args.get('student-parent_id')
                   or student_form.parent_id.data)
    parent_form = ParentForm(request.form,
                             data=db.parents.fetchone(parent_id),
                             prefix='parent')

    if request.method == 'PUT' and validate(student_form, parent_form):
        db.students.update(student['student_id'], student_form.data)
        db.parents.update(parent_id, parent_form.data)
        db.commit()
        student = db.students.fetchone(student['student_id'])
        student_name = f'{student_form.last_name.data} ' \
            f'{student_form.first_name.data}'
        flash(f'Updated <b>{student_name}</b>', 'info')

    return {'student': student,
            'group': db.groups.fetchone(student['group_id']),
            'student_form': student_form, 'parent_form': parent_form,
            'siblings': [child for child in db.parents.fetchchildren(parent_id)
                         if child['student_id'] != student['student_id']],
            'payments': db.parents.fetchpayments(parent_id)}


@bp.route('add', methods=('GET', 'POST'))
@templated
def add():
    db = get_db()

    student_form = StudentForm(request.form, prefix='student')
    parent_id = request.args.get('student-parent_id')
    parent = db.parents.fetchone(parent_id)
    parent_form = ParentForm(request.form, data=parent, prefix='parent')

    if request.method == 'POST' and (
        student_form.validate() and parent_form.validate()
    ):
        if student_form.parent_id.data is None:
            db.parents.insert(parent_form.data)
            student_form.parent_id.data = db.lastrowid
        else:
            db.parents.update(student_form.parent_id.data, parent_form.data)
        db.students.insert(student_form.data)
        db.commit()
        student_name = f'{student_form.last_name.data} ' \
            f'{student_form.first_name.data}'
        flash(f'Added <b>{student_name}</b>', 'info')

    return {'student_form': student_form, 'parent_form': parent_form,
            'group': db.groups.fetchone(student_form.group_id.data)}


@bp.route('delete', methods=('GET', 'DELETE'))
@confirm('students', 'student_name', 'Delete:')
def delete():
    db = get_db()
    for student in [db.students.fetchone(id)
                    for id in request.form.getlist('id')]:
        db.students.delete(student['rowid'])
        flash('Deleted ' f'<b>{student["student_name"]}</b>', 'info')
    db.students.commit()
    return '', {'HX-Redirect': url_for('students.index')}


@bp.route('email')
@templated
def email():
    db = get_db()
    parent = db.parents.fetchone(id)
    return {'parent': parent}


@bp.route('sms')
@templated
def sms():
    db = get_db()
    parent = db.parents.fetchone(id)
    return {'parent': parent}
