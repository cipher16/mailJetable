import re,cgi,os, datetime, logging, email, codecs
from google.appengine.ext import db
from google.appengine.ext import webapp

# MODELS
from Models.MailOwner import MailOwner
from Models.MailReceived import MailReceived

class CreateMail(webapp.RequestHandler):
    def get(self):
        self.redirect('/')
    def post(self):
        #sanitize owner, get only accepted owner name
        r = re.compile("([a-zA-Z0-9-\._]+)")
        owner = r.findall(self.request.get('mail'))[0]
        
        #delete expired account & linked mail ... no join in GQL :s
        results = db.GqlQuery("SELECT * FROM MailOwner WHERE expiration < :1",datetime.datetime.now())
        for result in results:
            data = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1",result.name).fetch(1000)
            db.delete(data)#delete mail
            result.delete() #deleting expired users
            
            #verify if account exist 
        results = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1", owner).fetch(1)
        if not results:
            mailOwner = MailOwner()
            mailOwner.name = owner
            duration = int(self.request.get('duration'))    
            mailOwner.duration = duration
            mailOwner.expiration = datetime.datetime.now() + datetime.timedelta(minutes=duration)
            mailOwner.put()
        self.redirect('/displayMails?mail='+owner)