# Reads a row from the transeiver receive table in database
# Inputs: None
# Outputs: None

from connect_db import connect_database

def Database_Read(sql_receive, readType):
	#print ""
	#print "Reading from database"
	try:
		cursor=connect_database(sql_receive)
		#cursor.execute(sql_receive)    # execute a read from database
		if readType == 1:
			row = cursor.fetchone()        # collect the row read
		elif readType == 0:
			row = cursor.fetchall()
		conn.commit()
		new_row = list(row)
		#print "Row:", new_row
		return new_row                 # return row
	except ValueError:
		#print 'Not enough bytes in sql received'
		return '0'
