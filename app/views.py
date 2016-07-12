from flask import render_template, redirect, flash, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import RegistrationForm, LoginForm, EditForm, PostForm, SearchForm
from models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
    form = PostForm()
    if form.validate_on_submit(): 
        post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post published!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', title = 'Home', 
                           form = form, posts = posts)


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
        g.search_form = SearchForm()

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
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_fol('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
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

@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    results = Post.query.whoosh_search(g.search_form.search.data, MAX_SEARCH_RESULTS).all()
    return render_template('search.html', query = g.search_form.search.data, results = results) 

@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
