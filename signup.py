from user import UserHandler

import from models import utils
import models


class SignupHandler(UserHandler):
    SIGNUP_PAGE = "signup.html"

    def render_signup(self, valid_username=False,
                      matching_passwords = False,
                      valid_password = False,
                      valid_email = False,
                      username = "",
                      email = "",
                      user_exists = False,
                      form_validated = False):
        self.render(SignupHandler.SIGNUP_PAGE,
                    valid_username = valid_username,
                    matching_passwords = matching_passwords,
                    valid_password = valid_password,
                    valid_email = valid_email,
                    username = username,
                    email = email, user_exists = user_exists,
                    form_validated = form_validated)

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

        user = models.User.by_name(username)
        user_exists = user is None

        if(valid_username and
           matching_passwords and
           valid_password and
           valid_email and (user is None)):
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
                               email = email,
                               form_validated = True,
                               user_exists = user_exists)
