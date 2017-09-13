import os
import re

import logging

import webapp2
import jinja2

from models import utils
import models

from google.appengine.ext import ndb as db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


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
        self.user = models.User.by_id(user_id)

class WelcomeHandler(UserHandler):
    def get(self):
        if self.user is None:
            self.redirect("/signup")
        else:
            self.render("welcome.html", username = self.user.name)


class HomePageHandler(UserHandler):
    def get(self):
        if self.user is None:
            self.redirect("/signup")
        else:
            self.redirect("/welcome")

class LogoutHandler(UserHandler):
    def get(self):
        if self.user is not None:
            self.logout()
        self.redirect("/signup")


class SignupHandler(UserHandler):
    SIGNUP_PAGE = "signup.html"
    def get(self):
        self.render(SignupHandler.SIGNUP_PAGE)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        valid_username = utils.valid_username(username)
        matching_passwords = False
        if password == verify:
            matching_passwords = True
        valid_password = utils.valid_password(password)
        valid_email = utils.valid_email(email)

        if(valid_username and
           matching_passwords and
           valid_password and
           valid_email):
           usr = models.User.register(username, password, email)
           usr = usr.put().get()

           self.login(usr)

           self.redirect('/welcome')
        else:
            self.render(SignupHandler.SIGNUP_PAGE,
                        valid_username = valid_username,
                        valid_password = valid_password,
                        matching_passwords = matching_passwords,
                        valid_email = valid_email,
                        username = username,
                        email = email)


app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/logout', LogoutHandler),
], debug=True)
