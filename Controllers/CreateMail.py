import re,datetime
from google.appengine.ext import db
from google.appengine.ext import webapp

# MODELS
from Models.MailOwner import MailOwner

class CreateMail(webapp.RequestHandler):
    def get(self):
        self.redirect('/')
    def post(self):
        #sanitize owner, get only accepted owner name
        r = re.compile("([a-zA-Z0-9-\._]+)")
        owner = r.findall(self.request.get('mail'))[0]
            
            #verify if account exist 
        results = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1", owner).fetch(1)
        if not results:
            mailOwner = MailOwner()
            mailOwner.name = owner
            mailOwner.ip = self.request.remote_addr #to verify expiration with ip
            duration = int(self.request.get('duration'))    
            mailOwner.duration = duration
            mailOwner.expiration = datetime.datetime.now() + datetime.timedelta(minutes=duration)
            mailOwner.put()
        self.redirect('/displayMails?mail='+owner)