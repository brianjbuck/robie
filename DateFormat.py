# --------------------------------------------------------------------------------------------------------------
#	API:			DateFormat(). DateFormatting for python Datetime/Date objects.
#	AUTHOR: 		Brian Buck 
#	CREATED:		9/15/2007
#	VERSION:		1.0
#	DESCRIPTION:	Formats a date object into a string using a custom mask that is
#					easy and intuitive to use instead of the built-in python routines.
#					Based on the ColdFusion DateFormat() method.
#
#	HISTORY:		1.0 - Original Script.
#
#
#	LICENSE:		THIS IS AN OPEN SOURCE API. YOU ARE FREE TO USE THIS API IN ANY APPLICATION,
#               	TO COPY IT OR MODIFY THE FUNCTIONS FOR YOUR OWN NEEDS, AS LONG THIS HEADER INFORMATION
#              	 	REMAINS IN TACT AND YOU DON'T CHARGE ANY MONEY FOR IT. USE THIS API AT YOUR OWN
#               	RISK. NO WARRANTY IS EXPRESSED OR IMPLIED, AND NO LIABILITY ASSUMED FOR THE RESULT OF
#               	USING THIS API.
#
#               	THIS API IS LICENSED UNDER THE CREATIVE COMMONS ATTRIBUTION-SHAREALIKE LICENSE.
#               	FOR THE FULL LICENSE TEXT PLEASE VISIT: http://creativecommons.org/licenses/by-sa/2.5/
#
#-----------------------------------------------------------------------------------------------------------------

import datetime

def DateFormat(d, mask='short'):
	"""
	d = Date/DateTime object
	mask =  *  d: Day of the month as digits; no leading zero for single-digit days.
			* dd: Day of the month as digits; leading zero for single-digit days.
			* ddd: Day of the week as a three-letter abbreviation.
			* dddd: Day of the week as its full name.
			* m: Month as digits; no leading zero for single-digit months.
			* mm: Month as digits; leading zero for single-digit months.
			* mmm: Month as a three-letter abbreviation.
			* mmmm: Month as its full name.
			* yy: Year as last two digits; leading zero for years less than 10.
			* yyyy: Year represented by four digits.

			The following masks tell how to format the full date and cannot be combined with other masks:
			* short: equivalent to m/d/yy
			* medium: equivalent to mmm d, yyyy
			* long: equivalent to mmmm d, yyyy
			* full: equivalent to dddd, mmmm d, yyyy
	"""
	
	if (not isinstance(d, datetime.date)) and (not isinstance(d, datetime.datetime)):
		raise TypeError("Argument 1 must be of type datetime.date or datetime.datetime")
	
	year = d.year
	month = d.month
	day = d.day
	
	months = monthsOfYear()
	weekdays = daysOfWeek()
	
	mask = mask.lower()
	
	if mask == 'short':
		formattedDate = str(month) + '/' + str(day) + '/' + str(year)[2:]
		return formattedDate
	elif mask == 'medium':
		formattedDate = months[month][:3] + ' ' + str(day) + ', ' + str(year)
		return formattedDate
	elif mask == 'long':
		formattedDate = months[month] + ' ' + str(day) + ', ' + str(year)
		return formattedDate
	elif mask == 'full':
		formattedDate = weekdays[d.weekday()] + ', ' + months[month] + ' ' + str(day) + ', ' + str(year)
		return formattedDate
	
	# user defined date mask
	else:
		temp = ''
		last = mask[0]
		curr = ''
		tokens = []
		
		for i in range(len(mask)):
			curr = mask[i]
			
			if curr == last:
				temp += curr
				last = curr
			else:
				last = curr
				tokens.append(temp)
				temp = curr
		
		# don't leave off the last token
		tokens.append(temp)
		
		# substitute tokens with values
		tokens = [resolveTokens(d, token) for token in tokens]
		
		return ''.join(tokens)

def resolveTokens(d, token):
	
	months = monthsOfYear()
	weekdays = daysOfWeek()
	
	if token == 'd':
		return str(d.day)
	elif token == 'dd':
		return str(d.day).zfill(2)
	elif token == 'ddd':
		return weekdays[d.weekday()][:3]
	elif token == 'dddd':
		return weekdays[d.weekday()]
	elif token == 'm':
		return str(d.month)
	elif token == 'mm':
		return str(d.month).zfill(2)
	elif token == 'mmm':
		return months[d.month][:3]
	elif token == 'mmmm':
		return months[d.month]
	elif token == 'yy':
		return str(d.year)[2:]
	elif token == 'yyyy':
		return str(d.year)
	else:
		return token

def monthsOfYear():
	return {1: 'January',
			2: 'February',
			3: 'March',
			4: 'April',
			5: 'May',
			6: 'June',
			7: 'July',
			8: 'August',
			9: 'September',
			10: 'October',
			11: 'November',
			12: 'December' }

def daysOfWeek():
	return {0: 'Monday',
			1: 'Tuesday',
			2: 'Wednesday',
			3: 'Thursday',
			4: 'Friday',
			5: 'Saturday',
			6: 'Sunday' }

if __name__ == '__main__':
	today = datetime.datetime.today()
	
	print 'short:\t\t\t%s' % (DateFormat(today, 'short'), )
	print 'medium:\t\t\t%s' % (DateFormat(today, 'medium'), )
	print 'long:\t\t\t%s' % (DateFormat(today, 'long'), )
	print 'full:\t\t\t%s' % (DateFormat(today, 'full'), )
	print 'mm-dd-yyyy:\t\t%s' % (DateFormat(today, 'mm-dd-yyyy'), )
	print 'd mmm yyyy:\t\t%s' % (DateFormat(today, 'd mmm yyyy'), )
	print 'm.dd.yyyy:\t\t%s' % (DateFormat(today, 'm.dd.yyyy'), )
	print 'ddd, mmm d, yyyy:\t%s' % (DateFormat(today, 'ddd, mmm d, yyyy'), )
	print 'Not a Valid mask:\t%s' % (DateFormat(today, 'Not a Valid mask'), )
	print 'DDDD, MMMM D, YYYY:\t%s' % (DateFormat(today, 'DDDD, MMMM D, YYYY'), )
	print 'yyyymmdd:\t\t%s' % (DateFormat(today, 'yyyymmdd'), )
	print 'dd/mm-yyyy:\t\t%s' % (DateFormat(today, 'dd/mm-yyyy'), )
	