from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# MODELS
from Models.MailOwner import MailOwner
from Models.MailReceived import MailReceived
# CONTROLLERS
from Controllers.MainPage import MainPage
from Controllers.DisplayContent import DisplayContent
from Controllers.CreateMail import CreateMail
from Controllers.DisplayMails import DisplayMails
from Controllers.LogSenderHandler import LogSenderHandler

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
