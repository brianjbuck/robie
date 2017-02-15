#!/usr/bin/env python
from datetime import date
import os
from socket import gethostname

filename = 'cbbga11.txt'

# if the OS is Linux and the hostname is "chicolini" this is PRODUCTION machine!
if os.name == 'posix':
	hostname = gethostname()
	if hostname == 'chicolini':
		DSN = """dbname='bracketizer' user='bracketizer' host='192.168.1.100' password='KbKh08xj'"""
		last10URI = '/var/www/bracketizer.com/Rankings/images/last10/'
		seasonURI = '/var/www/bracketizer.com/Rankings/images/season/'
		SOURCE_URL = 'http://kenpom.com/' + filename
		PRODUCTION = True
	else:
		DSN = '../datastore.db3'
		last10URI = '../images/last10/'
		seasonURI = '../images/season/'
		SOURCE_URL = filename
		PRODUCTION = False
else:
	DSN = '..\\datastore.db3'
	last10URI = '..\\images\\last10\\'
	seasonURI = '..\\images\\season\\'
	SOURCE_URL = filename
	PRODUCTION = False

LOGFILE = 'robielog.txt'
MEMCACHED_HOST = ['localhost:11211',]
CACHE_KEYS = [['TSR', 'TSRSOS', 'RPI', 'RPIOLD', 'SOS'], ['ASC', 'DESC'], ['25', '50', '100', 'ALL']]

EMAIL_TO = ['brian@thebuckpasser.com', 'info@bracketizer.com']
EMAIL_FROM = 'info@bracketizer.com'
EMAIL_SUBJECT = 'Robie is Finished For %s' % (date.today())
EMAIL_BODY = 'Robie is Finished'
EMAIL_SERVER = 'localhost'
