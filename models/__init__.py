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
        u = User.query().filter('name =', name).fetch()
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
