from google.appengine.ext import db

class MailReceived(db.Model):
    subject = db.StringProperty()                        #subject of the mail
    source = db.TextProperty()            #mail content + header
    body = db.TextProperty()
    plain = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)        #date of reception
    owner = db.StringProperty()                        #name of the owner (string :s)
    sender = db.StringProperty()
    read = db.BooleanProperty()