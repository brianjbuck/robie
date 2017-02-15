from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
import smtplib

class Mailer:
	
	def __init__(self, errorLogURI):
		self.errorLogURI = errorLogURI
	
	def sendMail(self, to, fro, subject, text, files=[], server="localhost"):
		"""Sends an email message to the specified recipient.
		
		@param to list reqired A list of recipients.
		@param fro string required A 'correct-looking' email address.
		@param subject string required The subject line.
		@param text string The body of the email message.
		@param files list Attachments, if any.
		@param server string The SMTP server that will send the email
		"""
		
		assert type(to) == list
		assert type(files) == list

		msg = MIMEMultipart()
		msg['From'] = fro
		msg['To'] = COMMASPACE.join(to)
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = subject

		msg.attach( MIMEText(text) )

		for file in files:
			part = MIMEBase('application', "octet-stream")
			part.set_payload( open(file,"rb").read() )
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
			msg.attach(part)

		smtp = smtplib.SMTP(server)
		#try:
		smtp.sendmail(fro, to, msg.as_string())
		#except:
		#log = open(self.errorLogURI, 'a')
		#	e = "Error: %s\n" % (to[0])
		#	log.write(e)
		#	log.close()
		#else:
		#	smtp.close()
		#finally:
		#	smtp.close()