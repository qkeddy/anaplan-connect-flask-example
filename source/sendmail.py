import smtplib  # Import smtplib for the actual sending function
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import getvar
import logging

# Setup Logger
localTime = time.strftime("%Y%m%d", time.localtime())
logFile = '%s-MIS.LOG' % localTime
fullPathLogFile = '%s/%s' % (getvar.logFilePath, logFile)
logFileLevel = logging.INFO  # Options: INFO, WARNING, DEBUG, INFO, ERROR, CRITICAL

logging.basicConfig(filename=fullPathLogFile,
					filemode='a',  # Append to Log
					format='%(asctime)s  :  %(levelname)s  :  %(message)s',
					level=logFileLevel)


def send_thankyou(email, firstName, lastName, company):
	# Set Email Parameters
	fromEmail = 'test@gmail.com'
	toEmail = email
	smtpUser = 'test@gmail.com'
	smtpPass = 'xxxx'
	emailSubject = 'test'

	# Setup Email
	emailMsg = MIMEMultipart('alternative')
	emailMsg['From'] = fromEmail
	emailMsg['To'] = toEmail
	emailMsg['Subject'] = emailSubject


	# Create the body of the message (a plain-text and an HTML version).
	text = "Hi %s %s\nThank you for visiting our booth!\nPlease let us know if you or anyone at %s have any questions or would like to inquire about our services.\n\nHere is a link to our company:\nhttps://gmailgroup.com" % (firstName, lastName, company)
	html = """\
	<html>
	  <head></head>
	  <body>
		<p>Hi %s %s,<br>
		   <br>
		   Thank you for visiting our booth!<br>
		   <br>
		   Please let us know if you or anyone at %s may have any questions or would like to inquire more about our services.
		   <br>
		   <br>
		   <br>user user
		   <br><a href="mailto:user@gmailgroup.com">user@gmailgroup.com</a>
		   <br>(619) 901-0003<br>
		   <br>
		   <br>
		   <br><a href="mailto:user@gmailgroup.com">user@gmailgroup.com</a>
		   <br>(650) 787-7137<br>
		   <br>
		   <br>Web: <a href="http://gmailgroup.com">http://gmailgroup.com</a>
		</p>
	  </body>
	</html>
	""" % (firstName, lastName, company)

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	emailMsg.attach(part1)
	emailMsg.attach(part2)

	# SMTP_SSL Example
	server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
	server_ssl.ehlo() # optional, called by login()
	server_ssl.login(smtpUser, smtpPass)

	# ssl server doesn't support or need tls, so don't call server_ssl.starttls()
	try:
		server_ssl.sendmail(fromEmail, toEmail, emailMsg.as_string())

	except:
		logging.info('Error caught - sendmail')

	server_ssl.close()
	print 'successfully sent the mail'