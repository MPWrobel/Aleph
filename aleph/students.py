from flask import abort, Blueprint, flash, request

from .db import get_db
from .forms import StudentForm, ParentForm
from .utils import templated, choices

bp = Blueprint('students', __name__, url_prefix='/students')


@bp.route('/')
@templated
def index():
    db = get_db()
    count = db.students.count()
    query = request.args.get('search')

    students = db.students.fetchall(
        query=query,
        order_by=request.args.get('sort') or 'student_name'
    )

    return {'students': students, 'count': count, 'query': query}


@bp.route('/add', methods=('GET', 'POST'))
@templated
def add():
    db = get_db()

    student_form = StudentForm(request.form, prefix='student')
    student_form.parent_id.choices = choices(
        db.parents.fetchall(),
        'New parent',
        'parent_id', ['first_name', 'last_name'])
    student_form.group_id.choices = choices(
        db.groups.fetchall(),
        'No group',
        'group_id', ['name'])

    parent_id = request.args.get('student-parent_id')
    parent = db.parents.fetchone(parent_id)
    parent_form = ParentForm(request.form, data=parent, prefix='parent')

    if request.method == 'POST' and (
        student_form.validate() and parent_form.validate()
    ):
        db.parents.insert(parent_form.data)
        student_form.parent_id.data = db.lastrowid
        db.students.insert(student_form.data)
        db.commit()
    else:
        for errors in student_form.errors.values():
            flash(errors[0], 'error')
        for errors in parent_form.errors.values():
            flash(errors[0], 'error')

    return {'student': student_form, 'parent': parent_form}


@bp.route('/<int:id>/delete', methods=('GET', 'DELETE'))
@bp.route('/delete', methods=('GET', 'DELETE'))
@templated
def delete(id=None):
    db = get_db()
    student = db.students.fetchone(id)
    students = [db.students.fetchone(id)
                for id in request.args.getlist('students')]
    return {'student': student, 'students': students}


@bp.route('/<int:id>/', methods=('GET', 'PUT'))
@templated
def student(id):
    db = get_db()

    student = db.students.fetchone(id)
    if student is None:
        abort(404)

    student_form = StudentForm(request.form, data=student, prefix='student')
    student_form.parent_id.choices = choices(
        db.parents.fetchall(),
        'New parent',
        'parent_id', ['first_name', 'last_name'])
    student_form.group_id.choices = choices(
        db.groups.fetchall(),
        'No group',
        'group_id', ['name'])

    parent_id = request.args.get('student-parent_id') or student_form.parent_id.data
    parent = db.parents.fetchone(parent_id)

    parent_form = ParentForm(request.form, data=parent, prefix='parent')

    if request.method == 'PUT' and (
        student_form.validate() and parent_form.validate()
    ):
        db.students.update(id, student_form.data)
        db.parents.update(parent_id, parent_form.data)
        db.commit()

    siblings = db.students.fetchsiblings(id)
    payments = db.payments.fetchbyparent(student['parent_id'])

    return {'student': student_form, 'parent': parent_form,
            'siblings': siblings, 'payments': payments}


@bp.route('/<int:id>/email')
@templated
def email(id):
    db = get_db()
    parent = db.parents.fetchone(id)
    return {'parent': parent}


@bp.route('/<int:id>/sms')
@templated
def sms(id):
    db = get_db()
    parent = db.parents.fetchone(id)
    return {'parent': parent}
