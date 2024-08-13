from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import Customer


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'),
                             validators=[DataRequired(), Email()])
    phone = StringField(_l('Phone'),
                             validators=[DataRequired()])
    New_password = PasswordField(_l('New Password'))
    New_password2 = PasswordField(
        _l('Repeat New Password'), validators=[EqualTo('New_password')])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(Customer).where(
                Customer.username == username.data))
            if user is not None:
                raise ValidationError(_('Please use a different username.'))
            

class ContactForm(FlaskForm):
    name = StringField(_l('Full Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired()])
    msg = TextAreaField(_l('How can we help you?'),
                             validators=[Length(min=0, max=250)])
    submit = SubmitField(_l('SEND MESSAGE'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class AddDomainForm(FlaskForm):
    domain_url = StringField(_l('Domain URL'), validators=[DataRequired()])
    domain_username = StringField(_l('Domain User Name'), validators=[DataRequired()])
    domain_password = StringField(_l('Domain Password'), validators=[DataRequired()])
