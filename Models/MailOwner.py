from google.appengine.ext import db

class MailOwner(db.Model):
    name = db.StringProperty()                        #subject of the mail
    date = db.DateTimeProperty(auto_now_add=True)        #date of reception
    expiration = db.DateTimeProperty()
    duration = db.IntegerProperty()