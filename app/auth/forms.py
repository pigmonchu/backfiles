from flask_babel import _
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from app.auth.models import User


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_('Password'), validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    class Meta:
        csrf = False

    password = PasswordField(_('Password'), validators=[DataRequired()])
    last_name = StringField(_('Last name'))
    first_name = StringField(_('Name'), validators=[DataRequired()])
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    rpt_pass = PasswordField(_('Repeat password'), validators=[DataRequired(), EqualTo('password')])

    def validate_email(self, value):
        user = User.query.filter_by(email=value.data).first()
        if user is not None:
            raise ValidationError(_('User already exists. Please Log in.'))
