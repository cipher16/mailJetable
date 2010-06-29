import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp

class CleanCronTask(webapp.RequestHandler):
    def get(self):
        #delete expired account & linked mail ... no join in GQL :s
        results = db.GqlQuery("SELECT * FROM MailOwner WHERE expiration < :1",datetime.datetime.now())
        for result in results:
            data = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1",result.name).fetch(1000)
            db.delete(data)#delete mail
            result.delete() #deleting expired users