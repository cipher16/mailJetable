from google.appengine.ext import db

class MailOwner(db.Model):
    name = db.StringProperty()                        #subject of the mail
    ip = db.StringProperty()                          #ip of creator (just to ensure that mail will not be read by others peeps)
    date = db.DateTimeProperty(auto_now_add=True)     #date of reception
    expiration = db.DateTimeProperty()
    duration = db.IntegerProperty()