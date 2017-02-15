import sqlite3

counter = 1
QRY = """INSERT INTO Ranking VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""

connection = sqlite3.connect('../datastore.db3')
cursor = connection.cursor()

f = open('out.csv', 'r')
for line in f:
	vals = str(counter) + ',' + line.strip()
	cursor.execute(QRY, tuple(vals.split(',')))
	counter += 1
	if counter % 200 == 0:
		connection.commit()
		print '\t%d Records Complete.' % counter

connection.commit()
cursor.close()
connection.close()