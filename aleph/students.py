from flask import Blueprint, request

from .db import get_db
from .utils import templated

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
