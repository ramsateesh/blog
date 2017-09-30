import webapp2

from models import utils
import models

from base import Handler


class UserHandler(Handler):
    USER_COOKIE_KEY = "user_id"

    def login(self, user):
        self.user = user
        user_hash = utils.make_secure_val(user.key.id())
        self.response.set_cookie(UserHandler.USER_COOKIE_KEY, user_hash, path = "/")

    def logout(self):
        self.response.delete_cookie(UserHandler.USER_COOKIE_KEY)

    def read_cookie(self, name):
        cookie = self.request.cookies.get(UserHandler.USER_COOKIE_KEY)
        return utils.get_user_id_from_cookie(cookie)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = self.read_cookie(UserHandler.USER_COOKIE_KEY)
        self.user = None
        if user_id is not None:
            self.user = models.User.by_id(user_id)
            if self.user is None:
                self.redirect("/login")
