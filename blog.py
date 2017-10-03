import webapp2

from user import UserHandler
from user.login import LoginHandler
from user.logout import LogoutHandler
from user.signup import SignupHandler
import base

from models import utils
import models

# import profanityfilter



class BlogHandler(UserHandler):
    def render_blogs(self, blogs = []):
        self.render("index.html",
                    user = self.user,
                    blog_entries = blogs)
 
    def get(self):
        if self.user is None:
            self.redirect("/login")
        else:
            blogs = models.Blog.by_user_id(self.user.key.id())
            self.render_blogs(blogs = blogs)


class BlogPageHandler(BlogHandler):
    def get(self, blog_id):
        if self.user is None:
            self.redirect("/login")
        else:
            blog = models.Blog.by_id(blog_id)
            comments = models.Comment.by_blog_id(blog_id)
            self.render("blog_entry.html", blog_entry = blog,
                        comments = comments, user = self.user)


class BlogPostHandler(UserHandler):
    def render_post(self, blog_entry = models.Blog()):
        self.render("post.html", blog_entry = blog_entry,
                    error = "")

    def get(self):
       if self.user is None:
            self.redirect("/login")
       else:
           self.render_post(blog_entry = models.Blog())

    def isValidData(self, title, text):
        if title is None or title == "":
            return False
        return True

    def post(self):
        if self.user is None:
            self.redirect("/login")
        else:
            blog_id = self.request.get('blog_id')
            user_id = self.request.get('user_id')
            title = self.request.get('subject')
            blog_text = self.request.get('content')

            if blog_id is not None and blog_id != '':
                blog_entry = models.Blog.by_id(int(blog_id))
            else:
                blog_entry = models.Blog()

            if user_id is not None and user_id != '':
                user_id = int(user_id)

                if user_id != self.user.key.id():
                    self.abort(401)

            if self.isValidData(title, blog_text):
                blog_entry.title = title
                blog_entry.content = blog_text
                blog_entry.user_id = self.user.key.id()
                blog_entry = blog_entry.put().get()
                self.redirect("/blog/%d" % blog_entry.key.id())
            else:
                self.render_post(
                    blog_entry = blog_entry,
                    error = "You need a valid title and blog content."
                )


class BlogEditHandler(BlogPostHandler):
    def get(self, blog_id):
        blog_id = int(blog_id)
        if self.user is None:
            self.redirect("/login")
        else:
            blog_entry = blog = models.Blog.by_id(blog_id)

            if blog_entry.user_id != self.user.key.id():
                self.abort(401)

            self.render_post(blog_entry = blog_entry)


class BlogDeleteHandler(BlogHandler):
    def get(self, blog_id):
        blog = models.Blog.by_id(blog_id)
        if self.user.key.id() != blog.user_id:
            self.abort(401)
        else:
            models.Blog.delete_by_id(blog_id)
            self.redirect("/")


class BlogLikeHandler(BlogHandler):
    def get(self, blog_id):
        blog_id = int(blog_id)

        blog = models.Blog.by_id(blog_id)

        if blog.user_id == self.user.key.id():
            self.abort(401)
        else:
            models.Blog.add_like(int(blog_id))
            self.redirect("/blog/%d" % blog_id)


class BlogUnlikeHandler(BlogHandler):
    def get(self, blog_id):
        blog_id = int(blog_id)

        blog = models.Blog.by_id(blog_id)

        if blog.user_id == self.user.key.id():
            self.abort(401)
        else:
            models.Blog.remove_like(int(blog_id))
            self.redirect("/blog/%d" % blog_id)


class AddCommentHandler(BlogHandler):
    def post(self):
        if self.user is None:
            self.redirect("/login")
        else:

            blog_id = self.request.get('blog_id')
            user_id = self.request.get('user_id')

            c_text = self.request.get('comment')
            c_user = models.User.get_by_id(int(user_id))

            comment = models.Comment()
            comment.blog_id = int(blog_id)
            comment.user_id = int(user_id)
            comment.comment_text = c_text
            comment.username = c_user.name
            comment.put()

            self.redirect("/blog/%d" % int(blog_id))
        


class EditCommentHandler(BlogHandler):
    def post(self):
        if self.user is None:
            self.redirect("/login")
        else:
            blog_id = long(self.request.get('blog_id'))
            user_id = long(self.request.get('user_id'))
            c_id = long(self.request.get('comment_id'))

            c_text = self.request.get('comment')
            c_user = models.User.get_by_id(int(user_id))

            comment = models.Comment.by_id(c_id)
            if comment.blog_id != blog_id or comment.user_id != user_id:
                self.abort(401)
            else:
                comment.comment_text = c_text
                comment.username = c_user.name
                comment.put()
                self.redirect("/blog/%d" % int(blog_id))


class DeleteCommentHandler(BlogHandler):
    def get(self, comment_id):
        comment = models.Comment.by_id(comment_id)
        if self.user.key.id() != comment.user_id:
            self.abort(401)
        else:
            blog_id = comment.blog_id
            comment.key.delete()
            self.redirect("/blog/%d" % blog_id)


app = webapp2.WSGIApplication([
    ('/', BlogHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/logout', LogoutHandler),
    ('/blog', BlogPostHandler),
    ('/blog/newpost', BlogPostHandler),
    ('/blog/(\d+)', BlogPageHandler),
    ('/blog/edit/(\d+)', BlogEditHandler),
    ('/blog/delete/(\d+)', BlogDeleteHandler),
    ('/blog/like/(\d+)', BlogLikeHandler),
    ('/blog/unlike/(\d+)', BlogUnlikeHandler),
    ('/blog/comment', AddCommentHandler),
    ('/blog/comment/edit', EditCommentHandler),
    ('/blog/comment/delete/(\d+)', DeleteCommentHandler),
], debug=True)

#app.error_handlers[404] = base.handle_404
#app.error_handlers[500] = base.handle_500
