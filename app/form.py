from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired
# from flask_wtf.file import FileField, FileRequired

class IncomeForm(FlaskForm):
    # info
    name = StringField('Name (As On Payslip)', validators=[DataRequired()])
    nric = StringField('NRIC', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])

    # town
    address = StringField('Address', validators=[DataRequired()])
    lease_id = StringField('Lease Reference', validators=[DataRequired()])

    # income
    income = DecimalField('Income', validators=[DataRequired()])
    cpf = DecimalField('CPF', validators=[DataRequired()])

    submit = SubmitField('Submit')