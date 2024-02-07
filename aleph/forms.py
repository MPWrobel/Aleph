from wtforms import Form, StringField, EmailField, SelectField
from wtforms.validators import Email, DataRequired

INVALID_PHONE = 'Enter a valid phone number'
EMPTY_FIELD = 'Please fill in required fields'


def int_or_none(val):
    try:
        return int(val)
    except TypeError:
        return None
    except ValueError:
        return None


class StudentForm(Form):
    first_name = StringField('First name', [DataRequired()])
    last_name  = StringField('Last name', [DataRequired()])
    group_id   = SelectField('Group', coerce=int_or_none)
    parent_id  = SelectField('Parent', coerce=int_or_none,
                             render_kw={
                                 'hx-get':    '',
                                 'hx-select': '#parent',
                                 'hx-target': '#parent',
                                 'hx-swap':   'outerHTML'
                             })


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
