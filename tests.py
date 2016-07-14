#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Post
from datetime import datetime

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_follow(self):
        user1 = User(nickname = 'mitchsvik', password = 'STRONG', email = 'mithsvik@gmail.com')
        user2 = User(nickname = 'john', password = 'qwerty', email = 'white@mail.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        assert user1.unfollow(user2) == None
        
        u = user1.follow(user2)
        db.session.add(u)
        db.session.commit()
        
        assert user1.follow(user2) == None
        assert user1.is_following(user2)
        assert user1.followed.count() == 1
        assert user1.followed.first().nickname == 'john'
        assert user2.followers.count() == 1
        assert user2.followers.first().nickname == 'mitchsvik'
        
        u = user1.unfollow(user2)
        
        assert u != None
        
        db.session.add(u)
        db.session.commit()
        
        assert user1.is_following(user2) == False
        assert user1.followed.count() == 0
        assert user2.followers.count() == 0
        
    def test_delete_post(self):
        u = User(nickname = 'mitchsvik', email = 'mitchsvik@gmail.com')
        p = Post(body = 'test', author = u, timestamp = datetime.utcnow())
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        
        p = Post.query.get(1)
        db.session.delete(p)
        db.session.commit()
        
if __name__ == '__main__':
    unittest.main()
