from google.appengine.ext import ndb as db

import utils


class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)


    @classmethod
    def by_id(cls, uid):
        if uid is None:
            return None
        uid = long(uid)
        return User.get_by_id(uid)


    @classmethod
    def by_name(cls, name):
        u = User.query(User.name == name).get()
        return u


    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = utils.make_pw_hash(name, pw)
        return User(name = name,
                    pw_hash = pw_hash,
                    email = email)


    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and utils.valid_pw(name, pw, u.pw_hash):
            return u


class Blog(db.Model):
     title = db.StringProperty(required = True)
     content = db.TextProperty()
     user_id = db.IntegerProperty(required = True)
     created = db.DateTimeProperty(auto_now_add=True)


     @classmethod
     def by_id(cls, uid):
         if uid is None:
             return None
         uid = long(uid)
         return Blog.get_by_id(uid)

     @classmethod
     def by_user_id(cls, user_id):
         if user_id is None:
             return None
         return Blog.query(Blog.user_id == user_id).fetch()


class Like(db.Model):
    blog_id = db.IntegerProperty(required = True)
    user_id = db.IntegerProperty(required = True)
    like = db.BooleanProperty()

    @classmethod
    def by_blog_id_and_user_id(cls, user_id, blog_id):
        if user_id is None or blog_id is None:
            return None
        else:
            return Like.query(ndb.AND(Like.user_id == user_id, Like.blog_id == blog_id)).get()


class Comment(db.Model):
    blog_id = db.IntegerProperty(required = True)
    user_id = db.IntegerProperty(required = True)
    username = db.StringProperty(required = True)
    comment_text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_blog_id(cls, blog_id):
        if blog_id is None:
            return None

        return Comment.query(Comment.blog_id == long(blog_id)).fetch()
