from flask import render_template, redirect, flash
from app import app
from forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	user = {'nickname' : 'Mitchsvik'}
	posts = [
		{
			'author' : {'nickname' : 'Mitchsvik'},
			'body' : 'text'
		},
		{
			'author' : {'nickname' : 'User'},
			'body' : 'another text'
		}
	]
	return render_template('index.html', title = user['nickname'],
                           user = user, posts = posts)

@app.route('/login', methods = {'GET', 'POST'})
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        flash('Login = "' + form.login.data + '", password = "' + form.password.data + 
              '", remember_me = ' + str(form.remember_me.data))
        return redirect('/index')
    
    return render_template('login.html', title = 'Sign In',
                           form = form)