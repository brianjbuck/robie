from datetime import date, datetime, timedelta
import itertools
import os
import sqlite3 as db
from sys import argv, exit, stdout
from time import time, ctime, sleep

from kenpomspider import KenPomSpider
from robie import Robie
import settings

def getStartAndEndDates(l):
	startDateVals = [int(val) for val in l[0][:10].split('/')]
	endDateVals = [int(val) for val in l[-1][:10].split('/')]

	return (
		date(startDateVals[2], startDateVals[0], startDateVals[1]),
		date(endDateVals[2], endDateVals[0], endDateVals[1])
		)

def dateFromString(s):
	d = [int(val) for val in s.split('/')]
	return date(d[2], d[0], d[1])

def enumerateDates(t):
	r = (t[1] + timedelta(days=1) - t[0]).days
	return [t[0] + timedelta(days=i) for i in range(r)]

def filterSchedule(d, data):
	return [line for line in data if dateFromString(line[:10]) <= d]

def currPrevNext(connectionStr):
	curr = None
	prev = None
	next = None
	
	SELECT_QRY = """SELECT DISTINCT rankingsDate FROM Ranking ORDER BY rankingsDate ASC;"""
	INSERT_QRY = """INSERT INTO CurrPrevNext (prev, curr, next) VALUES (?, ?, ?);"""
	connection = db.connect(connectionStr)
	connection.row_factory = db.Row
	cursor = connection.cursor()
	cursor.execute(SELECT_QRY)
	recordset = [row['rankingsDate'] for row in cursor]
	for i in range(len(recordset)):
		if i == 0:
			prev = None
			curr = recordset[i]
			next = recordset[i + 1]
		elif (i + 1) < len(recordset):
			prev = recordset[i - 1]
			curr = recordset[i]
			next = recordset[i + 1]
		elif i == len(recordset) - 1:
			prev = recordset[i - 1]
			curr = recordset[i]
			next = None
		cursor.execute(INSERT_QRY, (prev, curr, next))
	connection.commit()
	cursor.close()
	connection.close()

def getLineCount():
    with open('out.csv', 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def csv2SQL(connectionStr):
	counter = 1
	lineCount = getLineCount()
	QRY = """INSERT INTO Ranking
		(id, teamID, rpi, rpiAdj, sos, tsr, rpiRank, rpiAdjRank, sosRank, tsrRank, avgOppRPI, avgOppRPIAdj, avgOppSOS, avgOppTSR, avgOppRPIRank, avgOppRPIADJRank, avgOppSOSRank, avgOppTSRRank, winLossStr, lastNGames, lastNGamesRecord, wins, losses, record, wp, awp, owp, oowp, rankingsDate, seasonID, datecreated, dateupdated)
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
	
	connection = db.connect(connectionStr)
	cursor = connection.cursor()
	cursor.execute('PRAGMA temp_store = MEMORY;')
	cursor.execute('PRAGMA synchronous=OFF')
	cursor.execute('PRAGMA journal_mode = MEMORY;')
	
	f = open('out.csv', 'r')
	for line in f:
		vals = str(counter) + ',' + line.strip()
		cursor.execute(QRY, tuple([val.replace("'", '') for val in vals.split(',')]))
		counter += 1
		if counter % 1200 == 0:
			percent = float(counter) / float(lineCount) * 100.0 
			stdout.write('\t%d Percent Complete.\r' % int(percent))
			stdout.flush()
		#connection.commit()
	f.close()
	connection.commit()
	cursor.close()
	connection.close()

def cleanUpBeforeRun(connectionStr, gamesFilePath):
	# try to remove the outfile so it doesn't get too big
	try:
		os.remove(os.path.join(os.getcwd(), 'out.csv'))
	except OSError:
		pass
	try:
		os.remove(os.path.join(os.getcwd(), gamesFilePath, 'temp.txt'))
	except OSError:
		pass
	connection = db.connect(connectionStr)
	cursor = connection.cursor()
	print "\tCleaning ..."
	cursor.execute('DELETE FROM Ranking;')
	cursor.execute('DELETE FROM CurrPrevNext;')
	cursor.execute('DELETE FROM ScheduleResults;')
	cursor.execute('DELETE FROM Season;')
	print "\tVacuuming ..."
	cursor.execute("VACUUM")
	cursor.close()
	connection.commit()
	connection.close()

def createSeasonData(dates, ID):
	startDate = dates[0]
	endDate = dates[1]
	season = str(startDate.year) + '-' + str(endDate.year)
	return {'seasonID': ID, 'season': season, 'seasonStartDate': startDate.isoformat(), 'seasonEndDate': endDate.isoformat()}

def saveSeasons(seasons, connectionStr):
	QRY = """INSERT INTO Season (ID, season, seasonStartDate, seasonEndDate) VALUES (?, ?, ?, ?);"""
	connection = db.connect(connectionStr)
	cursor = connection.cursor()
	for season in seasons:
		cursor.execute(QRY, (season['seasonID'], season['season'], season['seasonStartDate'], season['seasonEndDate']))
	connection.commit()
	cursor.close()
	connection.close()

if __name__ == '__main__':
	
	path = 'GamesFiles'
	connectionStr = '../datastore.db3'
	seasons = []
	
	print "Performing Pre-run Tasks ..."
	cleanUpBeforeRun(connectionStr, path)
	
	startTime = time()
	startedAt = ctime()
	
	for dirpath, dirnames, filenames in os.walk(path):
		pass
	filenames.sort()
	seasonID = 0
	
	for filename in filenames[:1]:
		filename = 'cbbga11.txt'
		seasonID += 1
		dataFile = open(os.path.join(path, filename), 'r')
		data = [line.strip() for line in dataFile.readlines() if line.strip() != '']
		dataFile.close()
		dates = enumerateDates(getStartAndEndDates(data))
		seasons.append(createSeasonData(getStartAndEndDates(data), seasonID))
		for d in dates:
			t2 = time()

			# push everything into a temp file
			# and read from that
			toWrite = filterSchedule(d, data)
			f = open(os.path.join(path, 'temp.txt'), 'w')
			print d, len(toWrite)
			f.writelines('\n'.join(toWrite))
			f.close()

			print "Parsing ..."
			# parse the team schedules

			spider = KenPomSpider(os.path.join(path, 'temp.txt'), settings.LOGFILE)
			spider.run(False)

			print "Initializing ..."
			robie = Robie()
			robie.load(spider.data)
			print "Calculating ..."
			robie.calculate()
			print "Saving to Outfile ..."
			#robie.save()
			robie.rankingsToCSV(robie.teams, d, seasonID)
			endTime = time()
			elapsed = "\nTime elapsed %.2f s" % (endTime - t2)
			print "\t%s" % (elapsed,)
	
	print "Saving to Database ..."
	csv2SQL(connectionStr)
	print "\tSaving CurrPrevNext Data ..."
	currPrevNext(connectionStr)
	print "\tSaving Season Data ..."
	saveSeasons(seasons, connectionStr)
	
	print "Clearing Memcached ..."
	from memcache import Client
	MEMCACHED_HOST = ['localhost:11211',]
	cartesian = itertools.product(*settings.CACHE_KEYS) #[(a,b,c) for a in ['TSR', 'TSRSOS', 'RPI', 'RPIOLD', 'SOS'] for b in ['ASC', 'DESC'] for c in ['25', '50', '100', 'ALL']]
	keys = ['_'.join(item) for item in cartesian]
	mc = Client(MEMCACHED_HOST)
	mc.delete_multi(keys)
	
	finishedAt = ctime()
	endTime = time()
	elapsed = "\nTime elapsed %.2f s" % (endTime - startTime)
	
	print "Finished", elapsed
