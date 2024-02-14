from wtforms import Form, StringField, EmailField, SelectField
from wtforms.validators import Email, DataRequired

from .db import get_db

INVALID_PHONE = 'Enter a valid phone number'
EMPTY_FIELD = 'Please fill in required fields'


def validate(*forms):
    for form in forms:
        if not form.validate():
            return False
    return True


def int_or_none(val):
    try:
        return int(val)
    except TypeError:
        return None
    except ValueError:
        return None


def choices(choices, no_choice, value_field, text_fields):
    return [*((None, no_choice), (0, '', {'disabled': ''})),
            *((choice[value_field], ' '.join(choice[text_field]
                                             for text_field in text_fields))
              for choice in choices)]


class StudentForm(Form):
    first_name = StringField('First name', [DataRequired()])
    last_name  = StringField('Last name', [DataRequired()])
    group_id   = SelectField('Group', coerce=int_or_none)
    parent_id  = SelectField('Parent', coerce=int_or_none,
                             render_kw={
                                 'hx-get':    '',
                                 'hx-push-url': 'false',
                                 'hx-select': '#parent',
                                 'hx-target': '#parent',
                                 'hx-swap':   'outerHTML'
                             })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db = get_db()
        self.parent_id.choices = choices(
            db.parents.fetchall(),
            'New parent',
            'parent_id', ['first_name', 'last_name'])
        self.group_id.choices = choices(
            db.groups.fetchall(),
            'No group',
            'group_id', ['name'])


class ParentForm(Form):
    first_name = StringField('First name', [DataRequired()])
    last_name  = StringField('Last name', [DataRequired()])
    email      = EmailField('Email', [DataRequired(), Email()])
    phone      = StringField('Phone', [DataRequired()],
                             render_kw={'x-mask': '999 999 999'})

    def filter_phone(form, field):
        if field is None:
            return
        return field.replace(' ', '')


class GroupForm(Form):
    name     = StringField('Name', [DataRequired()])
    level_id = SelectField('Level', coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db = get_db()
        self.level_id.choices = [(level['level_id'], level['name'])
                                 for level in db.grouplevels.fetchall()]
