# Blog
Source code for a Blogger

# Pre-requisites

GIT (sudo apt-get install git -y)
GCP (https://cloud.google.com/appengine/docs/standard/python/quickstart)

# Install

1. git clone https://github.com/ramsateesh/blog.git
2. cd blog
3. gcloud app deploy index.yaml
4. gcloud app deploy

# Install locally

Step 4 of above section should be replaced with 'dev_server.py .'

# Access the Blogger

Locally you can access the blogger at http://localhost:8080/

## Signup 

Click on http://localhost:8080/signup

## Login

Click on http://localhost:8080/login

## Logout

Click on http://localhost:8080/logout

## New Blog Post

To publish a new post click on [New Post]http://localhost:8080/blog/newpost

## Edit Blog Post

To Edit any blog that you published

1. GO TO http://localhost:8080/
2. click on Edit link against the blog Title

## Delete Blog Post

To delete any blog post click on 
```
http://localhost:8080/blog/delete/<<blog id>>
```

## Comments

Comments can be added to any blog.  Editing the comment or deleting it can be done by the owner of the Comment.

## Like/Unlike

You can like or unlike the blog post that you didnot publish.
```
http://localhost:8080/blog/{like|unlike}/<<blog id>>
```

### License

`Blog` is a sample Blogger website. I love open source software!  You can do what ever you want to do with this source code.

