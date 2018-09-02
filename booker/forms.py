from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from booker.models import User


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('This email is already taken.')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddressForm(FlaskForm):
    address = StringField(
        'Current location',
        validators=[DataRequired()]
    )
    submit = SubmitField('Schedule booker!')
