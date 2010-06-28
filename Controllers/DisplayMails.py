from google.appengine.ext import db
import re,cgi,os, datetime, logging, email, codecs
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
class DisplayMails(webapp.RequestHandler):
	def get(self):
		owner = self.request.get('mail')
		owdat = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1", owner).fetch(1)
		results = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1 ORDER BY date DESC", owner).fetch(10)
		if owdat:
			owdat=owdat[0]
		
		for res in results:
			res.id=res.key()
		template_values = {
			'mails': results,
			'owner': owner,
			'owdat': owdat
		}
		path = os.path.join(os.path.dirname(__file__), '../Views/displayMails.html')
		self.response.out.write(template.render(path, template_values))