import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'very-strong-key-yep'

POSTS_PER_PAGE = 3

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
