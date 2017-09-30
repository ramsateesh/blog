from user import UserHandler

from models import utils
import models


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
