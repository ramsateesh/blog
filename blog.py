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


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('')
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def handle_exception(self, exception, debug):
        # Log the error.
        logging.exception(exception)

        # Set a custom message.
        self.response.write('An error occurred.')

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)


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


class BlogHandler(UserHandler):
    def render_blogs(self, blogs = []):
        self.render("index.html",
                    username = self.user.name,
                    blog_entries = blogs)
 
    def get(self):
        if self.user is None:
            self.redirect("/login")
        else:
            blogs = models.Blog.by_user_id(self.user.key.id())
            self.render_blogs(blogs = blogs)


class BlogPostHandler(UserHandler):
    def get(self):
       if self.user is None:
            self.redirect("/login")
       self.render("newpost.html", blog_entry = models.Blog())

    def isValidData(self, title, text):
        if title is None or title == "":
            return False
        return True

    def post(self):
        if self.user is None:
            self.redirect("/login")
        title = self.request.get('subject')
        blog_text = self.request.get('content')
        blog_entry = models.Blog()
        if self.isValidData(title, blog_text):
            blog_entry.title = title
            blog_entry.content = blog_text
            blog_entry.user_id = self.user.key.id()
            blog_entry = blog_entry.put().get()
            self.redirect("/blog/%d" % blog_entry.key.id())
        else:
            self.render_newpost(blog_entry, "You need a valid title and blog content.")


class BlogPageHandler(BlogHandler):
    def get(self, blog_id):
        if self.user is None:
            self.redirect("/login")

        blog = models.Blog.by_id(blog_id)
        comments = models.Comment.by_blog_id(blog_id)
        self.render("blog_entry.html", blog_entry = blog,
                    comments = comments, user = self.user)


class LoginHandler(UserHandler):
    def render_login(self,
                     valid_username=True,
                     valid_password = True,
                     invalid_credentials = False,
                     form_validated = False,
                     user_not_found = False):
        self.render("login.html",
                    user_not_found = user_not_found,
                    valid_username = valid_username,
                    valid_password = valid_password,
                    invalid_credentials = invalid_credentials,
                    form_validated = form_validated)

    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        valid_username = utils.valid_username(username)
        valid_password = utils.valid_password(password)

        user = models.User.by_name(username)

        if user is None:
            self.render_login(user_not_found = True,
                              form_validated = True)
        elif utils.valid_pw(username, password, user.pw_hash):
            self.login(user)
            self.redirect("/")
        else:
            self.render_login(valid_username = valid_username,
                              valid_password = valid_password,
                              invalid_credentials = True,
                              form_validated = True)

class LogoutHandler(UserHandler):
    def get(self):
        if self.user is not None:
            self.logout()
        self.redirect("/login")


class SignupHandler(UserHandler):
    SIGNUP_PAGE = "signup.html"

    def render_signup(self, valid_username=False,
                      matching_passwords = False,
                      valid_password = False,
                      valid_email = False,
                      username = None,
                      email = None):
        self.render(SignupHandler.SIGNUP_PAGE,
                    valid_username = valid_username,
                    matching_passwords = matching_passwords,
                    valid_password = valid_password,
                    valid_email = valid_email,
                    username = username,
                    email = email)

    def get(self):
        if self.user is not None:
            self.redirect("/")
        else:
            self.render_signup()

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

           self.redirect('/')
        else:
            self.render_signup(valid_username = valid_username,
                               valid_password = valid_password,
                               matching_passwords = matching_passwords,
                               valid_email = valid_email,
                               username = username,
                               email = email)


app = webapp2.WSGIApplication([
    ('/', BlogHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/logout', LogoutHandler),
    ('/newpost', BlogPostHandler),
    ('/blog/(\d+)', BlogPageHandler),
], debug=True)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
