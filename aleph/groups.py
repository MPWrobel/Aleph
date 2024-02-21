from flask import Blueprint, request, url_for, flash

from .db import Database, Table, confirm, fetchall, fetchone, get_db
from .forms import GroupForm, TeacherForm, validate
from .utils import templated

bp = Blueprint('groups', __name__, url_prefix='/groups')


@Database.table
class Groups(Table):
    view      = 'GroupsView'
    search_by = 'name'
    sort_by   = ('name', 'level', 'members')
    natural_sort = True


@Database.table
class GroupLevels(Table):
    pass


@Database.table
class Teachers(Table):
    view    = 'TeachersView'
    columns = ('teacher_id', 'first_name', 'last_name')
    sort_by = ('last_name', 'first_name')
    pass


@Database.table
class GroupTeachers(Table):
    pass


@bp.route('')
@fetchall('groups')
def index(groups):
    return {'groups': groups}


@bp.route('<int:id>', methods=('GET', 'PUT'))
@fetchone('groups')
def view(group):
    db = get_db()
    return {'group': group,
            'form': GroupForm(data=group),
            'members': db.students.fetchallby('group_id', group['group_id'])}


@bp.route('add', methods=('GET', 'POST'))
@templated
def add():
    return {'form': GroupForm()}


@bp.route('levels')
@templated
def levels():
    db = get_db()
    return {'levels': db.grouplevels.fetchall()}


@bp.route('teachers', methods=('GET', 'POST', 'PUT', 'DELETE'))
@templated
def teachers():
    db = get_db()
    teacher = db.teachers.fetchone(request.args.get('teacher'))
    group = db.groups.fetchone(request.args.get('group'))
    form = TeacherForm(data=teacher)

    if request.method == 'POST':
        form = TeacherForm(request.form)
        if teacher and group:
            db.groupteachers.insert({'teacher_id': teacher, 'group_id': group})
            db.commit()
            flash('Assigned '
                  f'<b>{teacher["first_name"]} {teacher["first_name"]}</b>',
                  f' to {group["name"]}'
                  'info')
        elif validate(form):
            db.teachers.insert(form.data)
            db.commit()
        form = TeacherForm()
    elif request.method == 'DELETE':
        form = TeacherForm()
        if teacher and group:
            ...
            # db.groupteachers.delete()
        elif teacher:
            db.teachers.delete(teacher['rowid'])
            db.commit()
            flash('Deleted '
                  f'<b>{teacher["first_name"]} {teacher["first_name"]}</b>',
                  'info')

    return {'teachers': db.teachers.fetchall(),
            'form': form,
            'teacher': teacher,
            'group': group}


@bp.route('delete', methods=('GET', 'DELETE'))
@confirm('groups', 'name', 'Delete:')
def delete():
    db = get_db()
    for group in [db.groups.fetchone(id)
                  for id in request.form.getlist('groups')]:
        db.groups.delete(group['rowid'])
        flash('Deleted ' f'<b>{group["name"]}</b>', 'info')
    db.commit()
    return '', {'HX-Redirect': url_for('groups.index')}


@bp.route('print')
@templated
def print():
    db = get_db()
    groups = [dict(group) for group in db.groups.fetchall()]
    for group in groups:
        group['members'] = db.groups.fetchmembers(group['group_id'])
    return {'groups': groups}


@bp.route('sms', methods=('GET', 'POST'))
def sms():
    return ''


@bp.route('email', methods=('GET', 'POST'))
def email():
    return ''
