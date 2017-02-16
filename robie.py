import csv
from datetime import date, datetime, timedelta
import itertools
import os
import settings
from sys import argv, exit
from time import time, ctime, sleep

from memcache import Client

from DateFormat import DateFormat
from kenpomspider import KenPomSpider
from Mail.Mailer import Mailer

if settings.PRODUCTION:
    import psycopg2 as db
else:
    import sqlite3 as db
from Team import Team

class Robie:
    teams = {}
    settings = None
    
    ### QUERIES ###
    TEAMS_QRY = """
        SELECT teamID, teamName, kenpomName
        FROM Team
        WHERE division = 1
        ORDER BY teamName ASC;
        """
    
    ID_MAP_QRY = """
        SELECT teamID, teamName, kenpomName FROM Team WHERE division = 1
        """
    ### QUERIES ###
    
    def __init__(self):
        # load settings here
        self.settings = settings
        self.idMap = {}
        self.idMapKenPom = {}
        self.schedules = {}
        self.genIdMap()
        self.teams = {}
        self.opponents = {}
    
    def execQuery(self, qry):
        if db.paramstyle == 'qmark':
            qry.replace('%s', '?')
        connection = db.connect(self.settings.DSN)
        cursor = connection.cursor()
        cursor.execute(qry)
        recordset = cursor.fetchall()
        cursor.close()
        connection.close()
        return recordset
    
    def load(self, data):
        recordset = self.execQuery(self.TEAMS_QRY)
        self.parse(data)
        
        for row in recordset:
            if row[2] in self.schedules:
                teamID, teamName, kenpomName = row[0], row[1], row[2]
                team = Team()
                team['ID'] = teamID
                team['teamID'] = teamID
                team['teamName'] = teamName
                team['kenpomName'] = kenpomName
                team['schedule'] = self.schedules[kenpomName]
                team['opponents'] = self.opponents[teamID]
                self.teams[teamID] = team   
    
    def dateFromString(self, s):
        d = [int(val) for val in s.split('/')]
        return date(d[2], d[0], d[1])
    
    def split(self, line):
        return {
            'gameDate': self.dateFromString(line[:11].strip()),
            'team1': line[11:34].strip(),
            'score1': line[34:38].strip(),
            'team2': line[38:60].strip(),
            'score2': line[60:64].strip(),
            'options': line[64:69].strip(),
            'location': line[69:].strip()
            }
    
    def initSchedule(self, key):
        if not self.schedules.has_key(key):
            self.schedules[key] = []
    
    def pushOpponent(self, team, opponent):
        if not self.opponents.has_key(team):
                self.opponents[team] = []
        if opponent:
            self.opponents[team].append(opponent)
        
    def parse(self, data):
        for line in data:
            items = self.split(line)
            
            gameDate = items['gameDate']
            team1 = items['team1']
            team2 = items['team2']
            score1 = items['score1']
            score2 = items['score2']
            options = items['options']
            location = items['location']
            
            
            
            #### debug
            #if team1 == 'Kentucky' or team2 == 'Kentucky':
            #   text = ""
            #   try:
            #       f = open('debug.txt', 'r')
            #       text = f.read()
            #       f.close()
            #   except:
            #       pass
            #   f = open('debug.txt', 'a')
            #   if not DateFormat(gameDate, 'mm/dd/yyyy') in text:
            #       f.write(line + '\n')
            #   f.close()
            
            self.initSchedule(team1)
            self.initSchedule(team2)
            
            teamID = self.getTeamID(team2)
            oppID = self.getTeamID(team1)
            self.pushOpponent(teamID, oppID)
            self.pushIntoSchedule(
                gameDate,
                oppID,
                team1,
                score1,
                team2,
                score2,
                'WIN' if int(score1) < int(score2) else 'LOSS',
                options,
                'AWAY' if location.find(',') == 1 else location
                )
            
            teamID = self.getTeamID(team1)
            oppID = self.getTeamID(team2)
            self.pushOpponent(teamID, oppID)
            self.pushIntoSchedule(
                gameDate,
                oppID,
                team2,
                score2,
                team1,
                score1,
                'WIN' if int(score1) > int(score2) else 'LOSS',
                options,
                'HOME' if location.find(',') == 1 else location
                )
            #
            #if team1 == 'Kentucky':
            #   print team1, team2, score1, score2, 'Win' if int(score1) > int(score2) else 'Loss'
            #   raw_input('')
            #if team2 == 'Kentucky':
            #   print team1, team2, score1, score2, 'Win' if int(score2) > int(score1) else 'Loss'
            #   raw_input('')
    
    def pushIntoSchedule(self, gameDate, oppID, oppName, oppScore, teamName, teamScore, result, options, location):
        game = {
            'gameDate': gameDate,
            'oppName': oppName,
            'oppID': oppID,
            'location': location,
            'result': result,
            'score': str(teamScore) + ' - ' + str(oppScore),
            'options': options
            }
        self.schedules[teamName].append(game)
        
    def genIdMap(self):
        recordset = self.execQuery(self.ID_MAP_QRY)
        
        for row in recordset:
            self.idMap[row[1]] = row[0]
            self.idMapKenPom[row[2]] = row[0]
    
    def getTeamID(self, name):
        if self.idMap.has_key(name):
            return self.idMap[name]
        elif self.idMapKenPom.has_key(name):
            return self.idMapKenPom[name]
        else:
            return None

    def calculate(self):
        print "    RPI ..."
        #self.RPI()
        self.RPI2()
        print "    TSR ..."
        self.TSR()
        print "    Averaging ..."
        self.avgOppData()
        print "    Sorting ..."
        self.sortAndRank('tsr')
        self.sortAndRank('rpi')
        self.sortAndRank('rpiAdj')
        self.sortAndRank('sos')
        self.sortAndRank('avgOppTSR')
        self.lastNGames(10)
        self.winLossStr()
        #if self.teams.has_key(129):
        #   print self.teams[129]['teamName'], self.teams[129]['lastNGames'], self.teams[129]['winLossStr'], self.teams[129]['tsrRank'], self.teams[129]['tsr'], self.teams[129]['rpiRank'], self.teams[129]['rpi']
    
    def save(self):
        connection = db.connect(self.settings.DSN)
        cursor = connection.cursor()
        
        if db.paramstyle == 'qmark':
            paramstyle = 'qmark'
        else:
            paramstyle = 'format'
        
        for team in self.teams.itervalues():
            self.saveRankings(team, cursor, paramstyle)
            self.saveSchedule(team, cursor, paramstyle)
        self.updateCurrPrevNext(cursor, paramstyle)
        cursor.close()
        print "    Committing Changes ..."
        connection.commit()
        connection.close()
    
    def updateCurrPrevNext(self, cursor, paramstyle):
        select = """
            SELECT DISTINCT a.rankingsDate AS curr,
            (SELECT MAX(rankingsDate) FROM Ranking WHERE rankingsDate < a.rankingsDate) AS prev,
            (SELECT MIN(rankingsDate) FROM Ranking WHERE rankingsDate > a.rankingsDate) AS next
            FROM Ranking AS a
            WHERE a.rankingsDate = (SELECT MAX(rankingsDate) FROM Ranking)
            """
        
        insert = """
            INSERT INTO CurrPrevNext (
                id,
                curr,
                prev,
                next )
            VALUES (
                %s,
                %s,
                %s,
                %s )
            """
        
        updateNext = """
            UPDATE CurrPrevNext SET next = %s
            WHERE curr = %s
            """
        
        getMaxID = """
            SELECT MAX(id) FROM CurrPrevNext
            """
        
        if paramstyle == 'qmark':
            insert = insert.replace('%s', '?')
            updateNext = updateNext.replace('%s', '?')
        
        cursor.execute(select)
        curr, prev, next = cursor.fetchone()
        cursor.execute(getMaxID)
        maxID = cursor.fetchone()[0]
        if not maxID:
            maxID = 0
        cursor.execute(insert, (maxID + 1, curr, prev, next))
        cursor.execute(updateNext, (curr, prev))
    
    def rankingsToCSV(self, teams, rankingsDate, seasonID):
        writer = open('out.csv', 'a')
        now = datetime.now()
        for teamID in self.teams:
            team = self.teams[teamID]
            rpi = team['rpi']
            rpiAdj = team['rpiAdj']
            sos = team['sos']
            tsr = team['tsr']
            rpiRank = team['rpiRank']
            rpiAdjRank = team['rpiAdjRank']
            sosRank = team['sosRank']
            tsrRank = team['tsrRank']
            avgOppRPI = team['avgOppRPI']
            avgOppRPIAdj = team['avgOppRPIAdj']
            avgOppSOS = team['avgOppSOS']
            avgOppTSR = team['avgOppTSR']
            avgOppRPIRank = team['avgOppRPIRank']
            avgOppRPIADJRank = team['avgOppRPIAdjRank']
            avgOppSOSRank = team['avgOppSOSRank']
            avgOppTSRRank = team['avgOppTSRRank']
            winLossStr = team['winLossStr']
            lastNGames = team['lastNGames']
            lastNGamesRecord = team['lastNGamesRecord']
            wins = sum([1 for x in team['winLossStr'].split('|') if x == 'W']) #wins = team['wins']
            losses = sum([1 for x in team['winLossStr'].split('|') if x == 'L']) #losses = team['losses']
            record = str(wins) + '-' + str(losses)
            wp = team['wp']
            awp = team['awp']
            owp = team['owp']
            oowp = team['oowp']
            line = "%d,%f,%f,%f,%f,%d,%d,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,'%s','%s','%s',%d,%d,'%s',%f,%f,%f,%f,%s,%d,%s,%s\n" % (teamID, rpi, rpiAdj, sos, tsr, rpiRank, rpiAdjRank, sosRank, tsrRank, avgOppRPI, avgOppRPIAdj, avgOppSOS, avgOppTSR, avgOppRPIRank, avgOppRPIADJRank, avgOppSOSRank, avgOppTSRRank, winLossStr, lastNGames, lastNGamesRecord, wins, losses, record, wp, awp, owp, oowp, (rankingsDate + timedelta(1)).isoformat(), seasonID, str(now), str(now))
            writer.write(line)
        writer.close()
            
    
    def saveRankings(self, team, cursor, paramstyle):
        insertStmt = """
            INSERT INTO Ranking (
                id,
                teamID,
                RPI,
                RPIADJ,
                SOS,
                TSR,
                RPIRank,
                RPIADJRank,
                SOSRank,
                TSRRank,
                avgOppRPI,
                avgOppRPIADJ,
                avgOppSOS,
                avgOppTSR,
                avgOppRPIRank,
                avgOppRPIADJRank,
                avgOppSOSRank,
                avgOppTSRRank,
                winLossStr,
                lastNGames,
                lastNGamesRecord,
                wins,
                losses,
                record,
                wp,
                awp,
                owp,
                oowp,
                rankingsDate,
                seasonid,
                dateCreated,
                dateUpdated )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        
        if paramstyle == 'qmark':
            insertStmt = insertStmt.replace('%s', '?')
        
        rankingsDate = date.today()
        
        teamID = team['teamID']
        rpi = team['rpi']
        rpiAdj = team['rpiAdj']
        sos = team['sos']
        tsr = team['tsr']
        rpiRank = team['rpiRank']
        rpiAdjRank = team['rpiAdjRank']
        sosRank = team['sosRank']
        tsrRank = team['tsrRank']
        avgOppRPI = team['avgOppRPI']
        avgOppRPIAdj = team['avgOppRPIAdj']
        avgOppSOS = team['avgOppSOS']
        avgOppTSR = team['avgOppTSR']
        avgOppRPIRank = team['avgOppRPIRank']
        avgOppRPIADJRank = team['avgOppRPIAdjRank']
        avgOppSOSRank = team['avgOppSOSRank']
        avgOppTSRRank = team['avgOppTSRRank']
        winLossStr = team['winLossStr']
        lastNGames = team['lastNGames']
        lastNGamesRecord = team['lastNGamesRecord']
        wins = sum([1 for x in team['winLossStr'].split('|') if x == 'W']) #wins = team['wins']
        losses = sum([1 for x in team['winLossStr'].split('|') if x == 'L']) #losses = team['losses']
        record = str(wins) + '-' + str(losses)
        wp = team['wp']
        awp = team['awp']
        owp = team['owp']
        oowp = team['oowp']
        cursor.execute('select max(id) from season')
        seasonid = cursor.fetchone()[0]
        cursor.execute('select max(id) from ranking')
        id = cursor.fetchone()[0]
        if not id:
            id = 0
        params = (
            id + 1,
            teamID,
            rpi,
            rpiAdj,
            sos,
            tsr,
            rpiRank,
            rpiAdjRank,
            sosRank,
            tsrRank,
            avgOppRPI,
            avgOppRPIAdj,
            avgOppSOS,
            avgOppTSR,
            avgOppRPIRank,
            avgOppRPIADJRank,
            avgOppSOSRank,
            avgOppTSRRank,
            winLossStr,
            lastNGames,
            lastNGamesRecord,
            wins,
            losses,
            record,
            wp,
            awp,
            owp,
            oowp,
            rankingsDate,
            seasonid,
            datetime.now(),
            datetime.now())
        
        cursor.execute(insertStmt, params)
    
    def saveSchedule(self, team, cursor, paramstyle):
        insertStmt = """
            INSERT INTO ScheduleResults (
                id,
                teamID,
                oppID,
                oppName,
                location,
                gameDate,
                result,
                score,
                options,
                seasonid,
                dateCreated,
                dateUpdated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        
        chkStmt = """
            SELECT gameDate
            FROM ScheduleResults
            WHERE teamID = %s
            AND seasonID = %s;
            """
        
        if paramstyle == 'qmark':
            insertStmt = insertStmt.replace('%s', '?')
            chkStmt = chkStmt.replace('%s', '?')
        
        cursor.execute('select max(id) from season')
        seasonID = cursor.fetchone()[0]
        
        teamID = team['teamID']
        
        cursor.execute(chkStmt, (teamID, seasonID))
        prevDates = [str(row[0]) for row in cursor]
        
        for game in team['schedule']:
            oppID = game['oppID']
            oppName = game['oppName']
            location = game['location']
            gameDate = game['gameDate']
            result = game['result']
            score = game['score']
            options = game['options']
            dateCreated = datetime.now()
            
            # only insert the game if it is not already there.
            if not DateFormat(gameDate, 'yyyy-mm-dd') in prevDates:
                cursor.execute('select max(id) from scheduleresults')
                id = cursor.fetchone()[0]
                if not id:
                    id = 0
                params = (id + 1, teamID, oppID, oppName, location, gameDate, result, score, options, seasonID, dateCreated, dateCreated)
                cursor.execute(insertStmt, params)
    
    def clearCache(self):
        # clean up any cached values from the previous day
        cartesian = itertools.product(*self.settings.CACHE_KEYS) #Cartesian(self.settings.CACHE_KEYS)
        keys = ['_'.join(item) for item in cartesian]
        mc = Client(self.settings.MEMCACHED_HOST)
        mc.delete_multi(keys)
    
    def sendMail(self, body=''):
        if len(body):
            msgBody = body
        else:
            msgBody = self.settings.EMAIL_BODY
        
        mailman = Mailer(self.settings.LOGFILE)
        mailman.sendMail(to=self.settings.EMAIL_TO,
            fro=self.settings.EMAIL_FROM,
            subject=self.settings.EMAIL_SUBJECT,
            text=msgBody,
            server=self.settings.EMAIL_SERVER)
    
    def calcRPI(self, wp, owp, oowp):
        return (0.25 * wp) + (0.5 * owp) + (0.25 * oowp)
    
    def calcSOS(self, owp, oowp):
        return ((2.0 / 3.0) * owp) + ((1.0 / 3.0) * oowp)
    
    def isD1(self, teamID, teamIDs):
        return teamID in teamIDs
    
    def RPI2(self):
        for team in self.teams:
            schedule = self.teams[team]['schedule']
            opponents = self.teams[team]['opponents']
            wp = self.calcWP(schedule)
            awp = self.calcAdjWP(schedule)
            owp = self.calcOWP(opponents)
            oowp = 0.0
            for oppID in opponents:
                opponents = self.teams[oppID]['opponents'] if self.teams.has_key(oppID) else None
                if opponents:
                    oowp = self.calcOWP(opponents)
            
            self.teams[team]['rpiAdj'] = self.calcRPI(awp, owp, oowp)
            self.teams[team]['rpi'] = self.calcRPI(wp, owp, oowp)
            self.teams[team]['sos'] = self.calcSOS(owp, oowp)
            self.teams[team]['wp'] = wp
            self.teams[team]['awp'] = awp
            self.teams[team]['owp'] = owp
            self.teams[team]['oowp'] = oowp
    
    def calcAdjWP(self, schedule):
        hwc = rwc = nwc = hlc = rlc = nlc = 0
        
        for game in schedule:
            result = game['result']
            location = game['location']
            
            if result == 'WIN':
                if location == 'HOME':
                    hwc += 1
                elif location == 'AWAY':
                    rwc += 1
                else:
                    nwc += 1
            elif result == 'LOSS':
                if location == 'HOME':
                    hlc += 1
                elif location == 'AWAY':
                    rlc += 1
                else:
                    nlc += 1
        
        # Adjusted Win Count
        awc = (float(hwc) * 0.6) + (nwc) + (rwc * 1.4)
        # Adjusted Loss Count
        alc = (float(hlc) * 1.4) + (nlc) + (rlc * 0.6)
        # Adjusted Win Percentage
        return float(awc) / float(awc + alc) if awc + alc > 0 else 0.0
        
    
    def calcWP(self, schedule):
        wc = len([game for game in schedule if game['result'] == 'WIN' and game['oppID'] in self.teams])
        lc = len([game for game in schedule if game['result'] == 'LOSS' and game['oppID'] in self.teams])
        return float(wc) / float(wc + lc) if wc > 0 else 0.0
    
    def calcOWP(self, opponents):
        # wincount/losscount
        wc = 0
        lc = 0
        for oppID in opponents:
            schedule = self.teams[oppID]['schedule'] if self.teams.has_key(oppID) else None
            if schedule:
                wc += len([game for game in schedule if game['result'] == 'WIN'])
                lc += len([game for game in schedule if game['result'] == 'LOSS'])
        # put into the if? not sure what the results will be if the returned value is 0.0 for non division 1 teams
        return float(wc) / float(wc + lc) if wc > 0 else 0.0
    
    def RPI(self):
        wCount = 0
        lCount = 0
        owCount = 0
        olCount = 0
        oowCount = 0
        oolCount = 0
        homeWinCount = 0
        homeLossCount = 0
        roadWinCount = 0
        roadLossCount = 0
        neutralWinCount = 0
        neutralLossCount = 0
        adjustedWinCount = 0
        adjustedLossCount = 0
        tIterCounter = 0
        wp = 0.0
        wpAdj = 0.0
        owp = 0.0
        oowp = 0.0
        
        # Optimizations:
        get = dict.get
        upper = str.upper
        isD1 = self.isD1
        
        teamIDs = self.teams.keys()
        
        # do the rpi, ripAdj, and sos calcs all at once so we don't have to waste time
        # doing the exact same calculations three times. also, by getting wp, owp and
        # oowp all in one big nested loop we prevent having to do multiple loops over
        # the exact same data and thus save time. i know, its ugly but processor ticks
        # are everything, right? plus if this gets added to a live web application where
        # people can do there own calcs on the fly then we want to cut down on time.
        
        for team in self.teams:
            schedule = self.teams[team]['schedule']
            
            # loop over the current team's schedule
            for gameL1 in schedule:
                oppID = gameL1['oppID']
                location = gameL1['location']
                result = gameL1['result']
                
                if (self.isD1(oppID, teamIDs)):
                    if(result.upper() == 'WIN'):
                        if(location.upper() == 'HOME'):
                            wCount += 1
                            homeWinCount += 1
                        elif(location.upper() == 'AWAY'):
                            wCount += 1
                            roadWinCount += 1
                        else:
                            wCount += 1
                            neutralWinCount += 1
                    elif(result.upper() == 'LOSS'):
                        if(location.upper() == 'HOME'):
                            lCount += 1
                            homeLossCount += 1
                        elif(location.upper() == 'AWAY'):
                            lCount += 1
                            roadLossCount += 1
                        else:
                            lCount += 1
                            neutralLossCount += 1
                    
                    oppSchedule = self.teams[oppID]['schedule']
                else:
                    continue
                
                # loop over the current team's opponents' schedules
                for gameL2 in oppSchedule:
                    ooppID = gameL2['oppID']
                    
                    if (self.isD1(ooppID, teamIDs)):
                        if(gameL2['result'].upper() == 'WIN'):
                            owCount += 1
                        else:
                            olCount += 1
                        
                        ooppSchedule = self.teams[oppID]['schedule']
                    else:
                        continue
                    
                    # loop over the current team's opponents' opponents schedules
                    for gameL3 in ooppSchedule:
                        tIterCounter += 1
                        
                        if (self.isD1(gameL3['oppID'], teamIDs)):
                            if(gameL3['result'].upper() == 'WIN'):
                                oowCount += 1
                            else:
                                oolCount += 1
                        else:
                            continue
            
            # now that we have the totals for this team process the values
            # and then reset to zero in preparation for the next team
            
            # be sure to avoid divide by zero errors
            wp = float(wCount) / float(wCount + lCount) if wCount + lCount > 0 else 0.0
            owp = float(owCount) / float(owCount + olCount) if owCount + olCount > 0 else 0.0
            oowp = float(oowCount) / float(oowCount + oolCount) if oowCount + oolCount > 0 else 0.0
            
            # Adjusted Win Count
            awc = (float(homeWinCount) * 0.6) + (neutralWinCount) + (roadWinCount * 1.4)
            # Adjusted Loss Count
            alc = (float(homeLossCount) * 1.4) + (neutralLossCount) + (roadLossCount * 0.6)
            # Adjusted Win Percentage
            awp = float(awc) / float(awc + alc) if awc + alc > 0 else 0.0
            
            wCount = 0
            lCount = 0
            owCount = 0
            olCount = 0
            oowCount = 0
            oolCount = 0
            homeWinCount = 0
            homeLossCount = 0
            roadWinCount = 0
            roadLossCount = 0
            neutralWinCount = 0
            neutralLossCount = 0
            awc = 0.0
            alc = 0.0
            
            self.teams[team]['rpiAdj'] = self.calcRPI(awp, owp, oowp)
            self.teams[team]['rpi'] = self.calcRPI(wp, owp, oowp)
            self.teams[team]['sos'] = self.calcSOS(owp, oowp)
            self.teams[team]['wp'] = wp
            self.teams[team]['awp'] = awp
            self.teams[team]['owp'] = owp
            self.teams[team]['oowp'] = oowp
    
    def TSR(self):
        startVals = {}
        endVals = {}
        isEqual = {}
        startVal = 75.0
        iterations = 10
        base = 25.0
        bonus = 1.4
        penalty = 0.6
        breakOut = False
        tIterCounter = 0
        equal = {}
        
        mid = base / bonus
        high = base
        low = (base / bonus) * penalty
        
        # bonuses/penalties for winning/losing at home/road/neutral sites
        # it is assumed that home wins are easier to get than road wins
        # so the least points are awarded for winning at home while the
        # most points are awarded for winning on the road. The opposite is
        # true regarding losses. A team is penalized the most points for
        # losing at home while penalized the fewest for losing on the road.
        # Neutral wins/losses are in between home/road wins/losses amounts.
        factorHomeWin = low
        factorHomeLoss = high
        factorRoadWin = high
        factorRoadLoss = low
        factorNeutralWin = mid
        factorNeutralLoss = mid
        totalTSR = 0.0
        oppTSR = 0.0
        totalGames = 0
        
        # initialize starting values
        for key in self.teams:
            startVals[key] = startVal
            equal[key] = False
        
        for x in range(iterations):
            for team in self.teams:
                currTeam = self.teams[team]['teamID']           
                schedule = self.teams[team]['schedule']
                
                for game in schedule:
                    
                    tIterCounter += 1
                    oppID = game['oppID']
                    score = game['score'].split(' - ')
                    
                    if (self.isD1(oppID, self.teams)):
                        currTeamTSR = startVals[currTeam]
                        oppTSR = startVals[oppID]
                        
                        if(game['result'].upper() == 'WIN'):
                            if(game['location'].upper() == 'HOME'):
                                thisFactor = factorHomeWin
                            elif(game['location'].upper() == 'AWAY'):
                                thisFactor = factorRoadWin
                            else:
                                thisFactor = factorNeutralWin
                            totalTSR += (oppTSR + thisFactor)
                        else:
                            if(game['location'].upper() == 'HOME'):
                                thisFactor = factorHomeLoss
                            elif(game['location'].upper() == 'AWAY'):
                                thisFactor = factorRoadLoss
                            else:
                                thisFactor = factorNeutralLoss
                            totalTSR += (oppTSR - thisFactor)
                    # set the bonus/penalty for winning/losing to a DII/DIII team
                    else:
                        if(game['result'].upper() == 'WIN'):
                            # approx 50
                            totalTSR += (40.0 + factorHomeWin)
                        elif(game['result'].upper() == 'LOSS'):                     
                            #  equals 15 or in other words, bad news
                            totalTSR += (40.0 - factorHomeLoss)
                    totalGames += 1
                
                endVals[currTeam] = totalTSR / float(totalGames)
                
                totalTSR = 0
                totalGames = 0
                
                if (round(startVals[currTeam], 4) == round(endVals[currTeam], 4)):
                    equal[currTeam] = True
                    
                    if not False in equal.values():
                        #pass
                        breakOut = True
            
            startVals = endVals
            if (breakOut):
                break
        
        # convert the values before returning.
        for key, value in startVals.iteritems():
            self.teams[key]['tsr'] = value / 100.0
    
    def avgOppData(self):
        teamIDs = self.teams.keys()
        
        for teamID in teamIDs:
            schedule = self.teams[teamID]['schedule']
            totalTSR = 0
            totalTSRRank = 0
            totalRPI = 0
            totalRPIRank = 0
            totalRPIAdj = 0
            totalRPIAdjRank = 0
            totalSOS = 0
            totalSOSRank = 0
            numGames = float(len(schedule))
            
            for game in schedule:
                
                oppID = game['oppID']
                
                if (not self.isD1(oppID, teamIDs)):
                    continue
                
                totalTSR += self.teams[oppID]['tsr']
                totalTSRRank += self.teams[oppID]['tsrRank']
                totalRPI += self.teams[oppID]['rpi']
                totalRPIRank += self.teams[oppID]['rpiRank']
                totalRPIAdj += self.teams[oppID]['rpiAdj']
                totalRPIAdjRank += self.teams[oppID]['rpiAdjRank']
                totalSOS += self.teams[oppID]['sos']
                totalSOSRank += self.teams[oppID]['sosRank']
            
            self.teams[teamID]['avgOppTSR'] = totalTSR / numGames
            self.teams[teamID]['avgOppTSRRank'] = totalTSRRank / numGames
            self.teams[teamID]['avgOppRPI'] = totalRPI / numGames
            self.teams[teamID]['avgOppRPIRank'] = totalRPIRank / numGames
            self.teams[teamID]['avgOppRPIAdj'] = totalRPIAdj / numGames
            self.teams[teamID]['avgOppRPIAdjRank'] = totalRPIAdjRank / numGames
            self.teams[teamID]['avgOppSOS'] = totalSOS / numGames
            self.teams[teamID]['avgOppSOSRank'] = totalSOSRank / numGames
    
    def sortAndRank(self, key):
        def sortOrder(t1, t2):
            return cmp(t2[1], t1[1])
        
        pairs = [(teamID, self.teams[teamID][key]) for teamID in self.teams.keys()]
        pairs.sort(sortOrder)
        counter = 0
        for pair in pairs:
            counter += 1
            self.teams[pair[0]][key + 'Rank'] = counter
    
    def lastNGames(self, n):
        for team in self.teams:
            schedule = self.teams[team]['schedule']
            
            # get only the last n games in the schedule
            # unless there are less than n games in the schedule
            if len(schedule) <= n:
                games = schedule
            else:
                games = schedule[len(schedule) - n:]
            
            lastNGames = [game['result'][0] for game in games]
            
            self.teams[team]['lastNGames'] = '|'.join(lastNGames)
            wins = str(self.teams[team]['lastNGames'].count('W'))
            losses = str(self.teams[team]['lastNGames'].count('L'))
            
            self.teams[team]['lastNGamesRecord'] =  wins + '-' + losses
    
    def winLossStr(self):
        for team in self.teams:
            schedule = self.teams[team]['schedule']
            results = [game['result'][0] for game in schedule]
            self.teams[team]['winLossStr'] = '|'.join(results)


if __name__ == '__main__':
    startTime = time()
    startedAt = ctime()
    print "Fetching ..."
    # parse the team schedules
    url = "GamesFiles/cbbga11.txt"
    logfileURL = "robielog.txt"
    spider = KenPomSpider(url, logfileURL)
    spider.run(False)
    
    # if the check was specified, test that the parsed values were updated from the previous day
    if len(argv) > 1:
        if argv[1] == '-c':
            if spider.fileUpdated():
                schedules = spider.schedules
        else:
            print "Error! Unknown Option: %s\nUsage: robie.py [option] ... [-c (check)]" % argv[1]
            exit(1)
    
    print "Initializing ..."
    robie = Robie()
    print "Parsing ..."
    robie.load(spider.data)
    #for team in robie.teams:
    #   out = (robie.teams[team]['teamName'], len(robie.opponents[team]), robie.teams[robie.opponents[team][0]]['teamName'], robie.teams[robie.opponents[team][-1]]['teamName'])
    #   #print "Team: %s\n Schedule Length: %d\n First Opponent: %s\n Last Opponent: %s" % out
    #assert False
    print "Calculating ..."
    robie.calculate()
    print "Saving ..."
    robie.save()
    print "Resetting Cached Values ..."
    robie.clearCache()
    print "Sending Mail ..."
    
    finishedAt = ctime()
    endTime = time()
    elapsed = "\nTime elapsed %.2f s" % (endTime - startTime)
    message = "Robie Finished Processing for %s\n\n%s\n\nStarted At: %s\nFinished At: %s" % (date.today(), elapsed, startedAt, finishedAt)
    robie.sendMail(message)
    print "Finished"
