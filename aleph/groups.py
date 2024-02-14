from flask import Blueprint, request, url_for, flash

from .db import Database, Table, confirm, fetchall, fetchone, get_db
from .forms import GroupForm
from .utils import templated

bp = Blueprint('groups', __name__, url_prefix='/groups')


@Database.table
class Groups(Table):
    view      = 'GroupsView'
    search_by = 'name'
    sort_by   = ('name', 'level', 'members')


@Database.table
class GroupLevels(Table):
    pass


@Database.table
class Teachers(Table):
    pass


@bp.route('')
@fetchall('groups')
def index(groups):
    return {'groups': groups}


@bp.route('<int:id>', methods=('GET', 'PUT'))
@fetchone('groups')
def group(group):
    db = get_db()
    return {'group': group,
            'form': GroupForm(data=group),
            'members': db.students.fetchallby('group_id', group['group_id'])}


@bp.route('add', methods=('GET', 'POST'))
def add():
    return ''


@bp.route('levels')
@templated
def levels():
    db = get_db()
    return {'levels': db.grouplevels.fetchall()}


@bp.route('teachers')
@templated
def teachers():
    db = get_db()
    return {'teachers': db.teachers.fetchall()}


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
