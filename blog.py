#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **k):
    self.response.out.write(*a, **k)
#This defines a function 'Write' which is a shortcut for self.response
  
  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
#A function called render_str which takes a template name and returns a string of that rendered template
  
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))
#Instead of just returning the string it calls 'Write' on it

class BlogPosts(db.Model):
  blog_title = db.StringProperty(required = True) #This is saying that a blog_title comes in the (preset) GAE form string, and it is necessary 
  blog_entry = db.TextProperty(required = True) #For the blog text, using the GAE text property as it could be longer than 2000 characters
  created = db.DateTimeProperty(auto_now_add = True)#Automatically, when we create an instance of BlogPost, will set the 'created' to be the current time

#To define an 'entity' (table) in Google App Engine, you define a class. You can find more info in the Google Datastore docs.
#This is the database for the blog entries. It inherits from db.Model which is included in GAE (see line 21)

class MainPage(Handler):
    def render_front(self, blog_title="", blog_entry=""):
      posts = db.GqlQuery("select * from BlogPosts order by created desc")
      #This means that when we render the front page it shows both the form and what's in our database - Gql is a Google Datastore's sql. In date descending.
      #posts is a cursor - a pointer to the results of the Google query, storing them in the variable posts
      self.render("frontpage.html", blog_title=blog_title, blog_entry=blog_entry, posts=posts)#We're directing to front page, passing in title, entry and current posts
#As MainPage is the root handler, this renders the front page by linking to the html template
#Title, Entry and Error are blank to start with, but we add stuff in as we go
      
    def get(self):
        self.render_front()
#The first get request, asking us to render the front page

class NewPost(Handler):
    def render_newpost(self, blog_title="", blog_entry="", error=""):
        self.render("newpost.html", blog_title=blog_title, blog_entry=blog_entry, error=error)
    
    def get(self):
        self.render_newpost()
      
    def post(self):
      blog_title = self.request.get("subject")
      blog_entry = self.request.get("content")
      
#The post request, so when the form is submitted it will pull through the title and the entry name from the {{variables}} in the html
      
      if blog_title and blog_entry:
        post = BlogPosts(blog_title = blog_title, blog_entry = blog_entry)#This is making a post if successfully inputted. It's attributing a new database entry, in the format we've defined in BlogPost.
        post.put() #This is storing the instance / post in the database
        postid = str(post.key().id())        
        self.redirect('/posts/%s.html' % postid) #This is redirecting to new post page, so we don't get the 'resubmit form' message

      else:
        error = "We need a title and a blog entry, big boy"
        self.render_newpost(blog_title, blog_entry, error = error)
#This shows the error message if you haven't done title AND entry, but will show them after the error because they're passed in.            


class PostHandler(Handler):
    def render_front2(self,post_id):
        p = BlogPosts.get_by_id(int(post_id))
        if p:
          self.render('permalink.html', p = p)
        else:
          self.error(404)
          return

    def get(self, post_id):
        self.render_front2(post_id)
  
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/posts/(\d+)\.html', PostHandler), 
#This the the handlers for both the MainPage (root) and NewPost    

], debug=True)
