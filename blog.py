import webapp2

from user import UserHandler

from models import utils
import models



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
        blog_id = self.request.get('blog_id')
        title = self.request.get('subject')
        blog_text = self.request.get('content')

        if blog_id is not None:
            blog_entry = model.Blog(id=int(blog_id))
        else:
            blog_entry = models.Blog()

        if self.isValidData(title, blog_text):
            blog_entry.title = title
            blog_entry.content = blog_text
            blog_entry.user_id = self.user.key.id()
            blog_entry = blog_entry.put().get()
            self.redirect("/blog/%d" % blog_entry.key.id())
        else:
            self.render_newpost(blog_entry, "You need a valid title and blog content.")


class BlogEditHandler(BlogPostHandler):
    def get(self, blog_id):
        blog_id = int(blog_id)
        if self.user is None:
            self.redirect("/login")

        blog_entry = blog = models.Blog.by_id(blog_id)

        self.render("blog_edit.html", blog_entry = blog_entry)


class BlogPageHandler(BlogHandler):
    def get(self, blog_id):
        if self.user is None:
            self.redirect("/login")

        blog = models.Blog.by_id(blog_id)
        comments = models.Comment.by_blog_id(blog_id)
        self.render("blog_entry.html", blog_entry = blog,
                    comments = comments, user = self.user)

class AddCommentHandler(BlogHandler):
    def post(self):
        pass


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
