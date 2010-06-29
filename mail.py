from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# CONTROLLERS
from Controllers.MainPage import MainPage
from Controllers.DisplayContent import DisplayContent
from Controllers.CreateMail import CreateMail
from Controllers.DisplayMails import DisplayMails
from Controllers.LogSenderHandler import LogSenderHandler
from Controllers.CleanCronTask import CleanCronTask

application = webapp.WSGIApplication(
	[('/', MainPage),
	('/createMail', CreateMail),
	('/displayMails', DisplayMails),
	('/displayContent', DisplayContent),
	('/clean', CleanCronTask),
	(LogSenderHandler.mapping())],
	debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
