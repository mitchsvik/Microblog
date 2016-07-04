from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, Email, EqualTo

class RegistrationForm(Form):
    login = TextField('Login', validators = [Length(min = 4, max = 63)])
    email = TextField('Email', validators = [Length(min = 6, max = 127)])
    password = PasswordField('Password', validators = [Required(), EqualTo('confirm', message = 'Pussword must match')])
    confirm = PasswordField('Repeat password')
    accept_rules = BooleanField('I accept the rules', validators = [Required()], default = False)

class LoginForm(Form):
    login = TextField('Login', validators = [Required()])
    password = PasswordField('Password', validators = [Required()])
    remember_me = BooleanField('Remember me', default = False)

class EditForm(Form):
    about = TextAreaField('About user', validators = [Length(min = 0, max = 199)])

class PostForm(Form):
    post = TextField('Post', validators = [Required()])
