from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
import datetime

class DisplayContent(webapp.RequestHandler):
    def get(self):
        type = self.request.get('type')
        if self.request.get('id') !="":
            id = db.Key(self.request.get('id'))
            results = db.GqlQuery("SELECT * FROM MailReceived WHERE __key__ = :1", id).fetch(1)
            if results:
                if type== "body":#no switch in python that sux
                    self.response.out.write(results[0].body)
                elif type == "source": 
                    self.response.out.write('<br />\n'.join(results[0].source.split('\n')))
                elif type == "plain":
                    self.response.out.write(results[0].plain)
                elif type == "delete":
                    owner = self.request.get('owner')
                    results[0].delete()
                    self.redirect("/displayMails?mail="+owner)
                elif type == "json":
                    owner = self.request.get('owner')
                    results = db.GqlQuery("SELECT * FROM MailReceived WHERE date > :1 AND owner = :2 ORDER BY date ASC", results[0].date,owner)
                    jsonArr = []
                    for result in results:
                        data = [result.date.__str__(),result.sender,result.subject,result.body,result.read,result.key().__str__()]
                        jsonArr.append(data)
                    self.response.out.write(simplejson.dumps(jsonArr))
                elif type == "read":
                    results[0].read=True
                    results[0].put() #set mail as read
            else:
                owner = self.request.get('owner')
                if owner:
                    self.redirect("/displayMails?mail="+owner)
                else:
                    self.redirect("/")
        elif type == "expiration":
            #in case of someone trying to test all pseudo to retrieve mails, check IP
            owner = self.request.get('owner')
            if owner:
                results = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1 and ip = :2 and expiration > :3",owner,self.request.remote_addr,datetime.datetime.now()).fetch(1)
                if not results:
                    jsonArr = ['false']#account valid and authorized
                else:
                    jsonArr = ['true']
            self.response.out.write(simplejson.dumps(jsonArr))
        elif type == "json":#in case we don't have id, we can have new mails
            owner = self.request.get('owner')
            results = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1 ORDER BY date ASC",owner)
            jsonArr = []
            for result in results:
                data = [result.date.__str__(),result.sender,result.subject,result.body,result.read,result.key().__str__()]
                jsonArr.append(data)
            self.response.out.write(simplejson.dumps(jsonArr))