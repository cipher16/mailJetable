import re,cgi,os, datetime, logging, email, codecs
from email.header import decode_header
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from django.utils import simplejson

#DATABASE OBJECT
class MailReceived(db.Model):
	subject = db.StringProperty()						#subject of the mail
	source = db.TextProperty()			#mail content + header
	body = db.TextProperty()
	plain = db.TextProperty()
	date = db.DateTimeProperty(auto_now_add=True)		#date of reception
	owner = db.StringProperty()						#name of the owner (string :s)
	sender = db.StringProperty()
	read = db.BooleanProperty()

class MailOwner(db.Model):
	name = db.StringProperty()						#subject of the mail
	date = db.DateTimeProperty(auto_now_add=True)		#date of reception
	expiration = db.DateTimeProperty()
	duration = db.IntegerProperty()

#ACTIONS
class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

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

class DisplayMails(webapp.RequestHandler):
	def get(self):
		owner = self.request.get('mail')
		results = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1 ORDER BY date DESC", owner).fetch(10)
		for res in results:
			res.id=res.key()
		template_values = {
			'mails': results,
			'owner':owner
		}
		path = os.path.join(os.path.dirname(__file__), 'displayMails.html')
		self.response.out.write(template.render(path, template_values))

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
		elif type == "json":#in case we don't have id, we can have new mails
			owner = self.request.get('owner')
			results = db.GqlQuery("SELECT * FROM MailReceived WHERE owner = :1 ORDER BY date ASC",owner)
			jsonArr = []
			for result in results:
				data = [result.date.__str__(),result.sender,result.subject,result.body,result.read,result.key().__str__()]
				jsonArr.append(data)
			self.response.out.write(simplejson.dumps(jsonArr))
			
#Getting & storing mails
class LogSenderHandler(InboundMailHandler):
    encodings = [  "utf_8","iso8859_15", "big5", "big5hkscs", "cp037", "cp424", "cp437", "cp500", "cp737", "cp775", "cp850", "cp852", "cp855", "cp856", "cp857", "cp860", "cp861", "cp862", "cp863", "cp864", "cp865", "cp866", "cp869", "cp874", "cp875", "cp932", "cp949", "cp950", "cp1006", "cp1026", "cp1140", "cp1250", "cp1251", "cp1252", "cp1253", "cp1254", "cp1255", "cp1256", "cp1257", "cp1258", "euc_jp", "euc_jis_2004", "euc_jisx0213", "euc_kr", "gb2312", "gbk", "gb18030", "hz", "iso2022_jp", "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_2004", "iso2022_jp_3", "iso2022_jp_ext", "iso2022_kr",  "iso8859_2", "iso8859_3", "iso8859_4", "iso8859_5", "iso8859_6", "iso8859_7", "iso8859_8", "iso8859_9", "iso8859_10", "iso8859_13", "iso8859_14", "johab", "koi8_r", "koi8_u", "mac_cyrillic", "mac_greek", "mac_iceland", "mac_latin2", "mac_roman", "mac_turkish", "ptcp154", "shift_jis", "shift_jis_2004", "shift_jisx0213", "utf_32", "utf_32_be", "utf_32_le", "utf_16", "utf_16_be", "utf_16_le", "utf_7", "utf_8_sig",None,"latin_1","ascii" ]
    def receive(self, mail_message):
	r = re.compile("([a-zA-Z0-9-\._]+)@")
	owner = r.findall(mail_message.to)[0]
	results = db.GqlQuery("SELECT * FROM MailOwner WHERE name = :1 AND expiration > :2", owner,datetime.datetime.now()).fetch(1)
	if results :
		mailreceived = MailReceived()
		mailreceived.read=False
		#getting subject
		try:
			mailreceived.subject = unicode(decode_header(mail_message.subject).pop()[0],'utf-8',errors='replace')
		except:
			mailreceived.subject = "Charset problem in subject."	
		#getting source			
		try:	
			mailreceived.source = unicode(mail_message.original.as_string(),'utf-8',errors='replace')		
		except:
			mailreceived.source = "Charset problem in source"
		#getting body (trying to get the good charset)
		html_bodies = mail_message.bodies('text/html')
		mailreceived.body=""
		for content_type, body in html_bodies:		
			mailreceived.body =  mailreceived.body+self.decodeBody(body)
		if mailreceived.body == "":
			html_bodies = mail_message.bodies('text/plain')
			for content_type, body in html_bodies:		
				mailreceived.body =  mailreceived.body+self.decodeBody(body)
		#getting sender
		try:
			mailreceived.sender = unicode(decode_header(mail_message.sender).pop()[0],'utf-8',errors='replace');
		except:
			mailreceived.sender = "Charset problem with sender."
		mailreceived.owner  = owner
		mailreceived.put()
		
    def decodeBody(self,body):
	charset = body.charset.__str__()
	if body.charset:
		try:
			t = body.payload.decode(charset)
			if t=="":
				raise Exception("Fucked Up with encodage")
			return t
		except Exception:
			logging.info("Probleme d'encodage : "+charset)
	#if the first doesn't work ... try a "bruteforce" guess
	for enc in self.encodings:
		try:
			t=body.payload.decode(enc)
			if t=="":
				raise Exception("Fucked Up with encodage")
			return t
		except Exception:
			logging.info("Probleme d'encodage : "+enc)
	return "Encoding problems we're unable to read this mail :s Sorry"
		


application = webapp.WSGIApplication(
	[('/', MainPage),
	('/createMail', CreateMail),
	('/displayMails', DisplayMails),
	('/displayContent', DisplayContent),
	(LogSenderHandler.mapping())],
	debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
