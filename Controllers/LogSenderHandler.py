import re,cgi,os, datetime, logging, email, codecs
from email.header import decode_header
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db

# MODELS
from Models.MailOwner import MailOwner
from Models.MailReceived import MailReceived

class LogSenderHandler(InboundMailHandler):
    encodings = [  "utf_8","iso8859_15", "big5", "big5hkscs", "cp037", "cp424", "cp437", "cp500", "cp737", "cp775", "cp850", "cp852", "cp855", "cp856", "cp857", "cp860", "cp861", "cp862", "cp863", "cp864", "cp865", "cp866", "cp869", "cp874", "cp875", "cp932", "cp949", "cp950", "cp1006", "cp1026", "cp1140", "cp1250", "cp1251", "cp1252", "cp1253", "cp1254", "cp1255", "cp1256", "cp1257", "cp1258", "euc_jp", "euc_jis_2004", "euc_jisx0213", "euc_kr", "gb2312", "gbk", "gb18030", "hz", "iso2022_jp", "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_2004", "iso2022_jp_3", "iso2022_jp_ext", "iso2022_kr",  "iso8859_2", "iso8859_3", "iso8859_4", "iso8859_5", "iso8859_6", "iso8859_7", "iso8859_8", "iso8859_9", "iso8859_10", "iso8859_13", "iso8859_14", "johab", "koi8_r", "koi8_u", "mac_cyrillic", "mac_greek", "mac_iceland", "mac_latin2", "mac_roman", "mac_turkish", "ptcp154", "shift_jis", "shift_jis_2004", "shift_jisx0213", "utf_32", "utf_32_be", "utf_32_le", "utf_16", "utf_16_be", "utf_16_le", "utf_7", "utf_8_sig",None,"latin_1","ascii" ]
    def receive(self, mail_message):
        r = re.compile("([a-zA-Z0-9-\._]+)@")
        owner = r.findall(mail_message.to)
        if not owner:
            #no owner so, we use
            r=re.compile("/_ah/mail/([a-zA-Z0-9-\._]+)%")
            owner = r.findall(self.request.path)
        if not owner:
            logging.critical("Can't get user name!! hax attempt ?? : "+self.request.path)
            return
        owner = owner[0]
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