from user import UserHandler

class LogoutHandler(UserHandler):
    def get(self):
        if self.user is not None:
            self.logout()
        self.redirect("/login")
