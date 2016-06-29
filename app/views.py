from flask import render_template, redirect, flash, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import RegistrationForm, LoginForm
from models import User, ROLE_USER, ROLE_ADMIN

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
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
	return render_template('index.html', title = 'Home',
                           user = user, posts = posts)

@app.route('/registration', methods = {'GET', 'POST'})
def registration():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        return try_to_register(login = form.login.data, email = form.email.data, password = form.password.data)
    
    return render_template('registration.html', title = 'Registration',
                          form = form)

def try_to_register(login = None, email = None, password = None):
    if User.query.filter_by(nickname = login).first() == None and User.query.filter_by(email = email).first() == None:
        user = User(nickname = login, email = email, password = password, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
        
    flash('Login or Email are already used. Please try another')
    return redirect(url_for('registration'))

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
    
@app.route('/login', methods = {'GET', 'POST'})
def login():                               
    if g.user is not None and g.user.is_authenticated: 
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return try_login(login = form.login.data, password = form.password.data)
    
    return render_template('login.html', title = 'Sign In',
                           form = form)

def try_login(login = None, password = None):
    user = User.query.filter_by(nickname = login).first()
    if user is not None:
        if user.password == password:
            remember_me = False
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)
            
            print user
            login_user(user = user, remember = remember_me)
            return redirect(request.args.get('next') or url_for('index'))
        
    flash('Invalid login. Please try again')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_fol('index'))
    posts = [
        {'author' : user, 'body': 'Test post 1'},
        {'author' : user, 'body': 'Test post 2'}
    ]
    return render_template('user.html', user = user, posts = posts)
