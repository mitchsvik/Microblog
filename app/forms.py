from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(Form):
    login = StringField('Login', validators=[Length(min=4, max=63)])
    email = StringField('Email', validators=[Length(min=6, max=127)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Password must match')])
    confirm = PasswordField('Repeat password')
    accept_rules = BooleanField('I accept the rules', validators=[DataRequired()], default=False)


class LoginForm(Form):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)


class EditForm(Form):
    about = TextAreaField('About user', validators=[Length(min=0, max=199)])


class PostForm(Form):
    post = StringField('Post', validators=[DataRequired()])


class SearchForm(Form):
    search = StringField('Search', validators=[DataRequired()])
