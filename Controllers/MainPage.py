from google.appengine.ext import webapp
import re,cgi,os, datetime, logging, email, codecs
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../Views/index.html')
        self.response.out.write(template.render(path, template_values))