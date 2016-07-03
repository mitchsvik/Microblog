from flask import render_template, redirect, flash, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import RegistrationForm, LoginForm, EditForm
from models import User, ROLE_USER, ROLE_ADMIN
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	posts = []
    
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
        
        db.session.add(user.follow(user))
        db.session.commit()
        
        return redirect(url_for('login'))
        
    flash('Login or Email are already used. Please try another')
    return redirect(url_for('registration'))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

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
            login_user(user = user, remember = session['remember_me'])
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

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.about = form.about.data
        db.session.add(g.user)
        db.session.commit()
        flash('Changes have been saved.')
        return redirect(url_for('user', nickname = g.user.nickname))
    else:
        form.about.data = g.user.about
    return render_template('edit.html', form = form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname = nickname))
   
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname = nickname))
    
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname = nickname))

@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
