from flask import render_template
from app import app

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
	return render_template("index.html", title = user['nickname'],
										 user = user,
										 posts = posts)