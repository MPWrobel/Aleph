import csv
import json
import re

from flask import Blueprint, request, render_template, redirect

from .db import Database, Table, fetchall, get_db
from .utils import templated

bp = Blueprint('payments', __name__, url_prefix='/payments')


@Database.table
class Payments(Table):
    view = 'PaymentsView'
    search_by = 'title'
    sort_by   = ('date', 'payment_id')
    columns = ('payment_id', 'payer', 'title', 'sum', 'date', 'student_id')

    def fetchnotassigned(self):
        SQL = "SELECT * FROM Payments WHERE student_id IS NULL"
        return self.db.execute(SQL).fetchall()

    def fetchone(self, id):
        SQL = """SELECT * FROM Payments
LEFT JOIN Students ON Payments.student_id = Students.student_id
WHERE payment_id = ?"""
        return self.db.execute(SQL, id).fetchone()

    def updatestudent(self, payment_id, student_id):
        SQL = "UPDATE Payments SET student_id = ? WHERE payment_id = ?"
        self.db.execute(SQL, student_id, payment_id)
        self.db.commit()


@bp.route('/')
@fetchall('payments')
def index(payments):
    db = get_db()
    names = json.dumps([
        {'value': student['student_id'], 'text': student['student_name']}
        for student in db.students.fetchall()
    ])

    return {'payments': payments,  'names': names}


@bp.route('/<int:payment_id>', methods=('GET', 'PUT'))
def payment(payment_id):
    db = get_db()

    if request.method == 'PUT' and (student_id := request.form.get('student_id')):
        db.payments.updatestudent(payment_id, student_id)

    payment = db.payments.fetchone(payment_id)
    return (render_template('payments/payment.html',
                            payment=payment),
            {'HX-Trigger-After-Swap': json.dumps({
                'updateStudentInput': {
                    'payment_id': payment_id,
                    'student_id': payment['student_id']
                }
            })})


@bp.route('/import', methods=('GET', 'POST'))
@templated
def import_file():
    if request.method == 'POST' and (file := request.files.get('file')):
        db = get_db()
        parents = db.parents.fetchnames()
        students = db.students.fetchnames()

        header = file.readline().decode('UTF-8')
        header = header.replace('Nazwa kontrahenta', 'payer')
        header = header.replace('Tytuł operacji', 'title')
        header = header.replace('Data księgowania', 'date')
        header = header.replace('Kwota', 'sum')
        content = file.read().decode('UTF-8').splitlines()
        content.append(header)
        content.reverse()

        for row in csv.DictReader(content, delimiter='|'):
            row['sum'] = int(float(row['sum']) * 100)

            for student in students:
                regex = f'.*{student["first_name"]}.*{student["last_name"]}.*'\
                        f'|.*{student["last_name"]}.*{student["first_name"]}.*'
                if re.search(regex, row['title'], re.IGNORECASE):
                    row['student_id'] = student['student_id']
                    break
            else:
                for parent in parents:
                    regex = f'.*{parent["first_name"]}.*{parent["last_name"]}.*'\
                            f'|.*{parent["last_name"]}.*{parent["first_name"]}.*'
                    if re.search(regex, row['payer'], re.IGNORECASE):
                        student = db.students.fetchoneby('parent_id', parent['parent_id'])
                        row['student_id'] = student['student_id']
                        break

            db.payments.insert(row)

        db.commit()
        return redirect('/payments')
    return {}
