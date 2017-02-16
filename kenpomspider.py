from datetime import datetime, date, timedelta
import logging
import sys
from time import sleep
from urllib2 import build_opener, HTTPError, URLError

from Mail.Mailer import Mailer
import settings

class KenPomSpider:
    
    def __init__(self, url, logFile):
        self.url = url
        self.logFile = logFile
        self.maxDate = None
        self.data = None
    
    def run(self, doUpdatedCheck=True):
        """Run Until the Games File is Updated. Abort if the Wait is too Long."""
        if not doUpdatedCheck:
            self.open()
        else:
            f = self.fibonacci()
            while True:
                self.open()
                self.setMaxDate()
                
                if self.updated():
                    break
                
                sleepVal = f.next()
                sleep(sleepVal * 60)
                if sleepVal > 250:
                    print "Exiting due to timeout!"
                    mailman = Mailer(self.logFile)
                    mailman.sendMail(to=settings.EMAIL_TO, 
                                        fro=settings.EMAIL_FROM, 
                                        subject="KenPomSpider Timed Out", 
                                        text="KenPomSpider Timed Out", 
                                        server=settings.EMAIL_SERVER)
                    sys.exit(1)
    
    def open(self):
        """Open a File or a Web URL"""
        if self.url[:7] == 'http://' or self.url[:8] == 'https://':
            self.openURL()
        else:
            self.openFile()
    
    def openURL(self):
        """Return the games file data as an array"""
        opener = build_opener()
        opener.addheaders = [('User-agent', 'Robie/Bracketizer.com')]
        try:
            raw = opener.open(self.url)
        except HTTPError, e:
            msg = "Could Not Open URL %s.\nThe Code is: %s "
            print  msg % (self.url, e.code)
            sys.exit()
        except URLError, e:
            msg = "Could Not Open URL %s.\nThe Reason is: %s "
            print msg % (self.url, e.reason)
            sys.exit()
        else:
            self.data = self.cleanDataAsList(raw)
        finally:
            opener.close()
    
    def openFile(self):
        """Return the games file data as an array"""
        try:
            f = open(self.url, 'r')
        except IOError:
            msg = "Could Not Open File %s"
            print msg % (self.url,)
            sys.exit()
        else:
            self.data = self.cleanDataAsList(f.readlines())
        finally:
            f.close()
    
    def cleanDataAsList(self, raw_data):
        """Removes Empty Lines and Those With White Space Chars"""
        return [l.strip() for l in raw_data if l.strip() != '']
    
    def setMaxDate(self):
        """Sets the Last Date in the Games File."""
        lastLine = self.data[-1]
        maxDateData = [int(val) for val in lastLine[:10].split('/')]
        self.maxDate = date(maxDateData[2], maxDateData[0], maxDateData[1])
    
    def updated(self):
        """ Return True if yesterday's games appear in the Games File"""
        return date.today() - timedelta(1) == self.maxDate
    
    def fibonacci(self):
        a, b = 5, 8
        
        # a, b = 1, 1
        while True:
            yield a
            a, b = b, a + b


if __name__ == '__main__':
    
    url = "GamesFiles/cbbga10.txt" #'http://kenpom.com/cbbga10.txt'
    logfileURL = '.'
    spider = KenPomSpider(url, logfileURL)
    spider.run()
    #print spider.data
