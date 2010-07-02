from google.appengine.ext import db
import datetime,os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
class DisplayMails(webapp.RequestHandler):
	def get(self):
		owner = self.request.get('mail')
		owdat = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1 and ip = :2", owner,self.request.remote_addr).fetch(1)
		results = []
		if owdat:
			owdat=owdat[0]
			if owdat.expiration>datetime.datetime.now():
				results = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1 ORDER BY date DESC", owner).fetch(10)
		
		for res in results:
			res.id=res.key()
		template_values = {
			'mails': results,
			'owner': owner,
			'owdat': owdat
		}
		path = os.path.join(os.path.dirname(__file__), '../Views/displayMails.html')
		self.response.out.write(template.render(path, template_values))