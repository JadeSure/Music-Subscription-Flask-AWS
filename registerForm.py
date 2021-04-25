from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, TextField, validators
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField
from wtforms.validators import DataRequired, EqualTo, Length
import email_validator


class RegisterForm(FlaskForm):
    email = StringField('Email: ', [validators.DataRequired(), validators.Email()])
    username = StringField(label='Username: ', validators=[DataRequired()])
    password1 = PasswordField(label='Password: ', validators=[DataRequired(), Length(5, 16, message='password need to longer than 5 chars')])
    password2 = PasswordField(label='Confirm password: ', validators=[DataRequired(),Length(5,16, message='wrong password format'),
                                                                    EqualTo('password1', message='Password Inconsistency')])

    submit = SubmitField(label='Regiter')