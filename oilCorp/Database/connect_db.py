
import MySQLdb
import MySQLdb.constants.CLIENT

def connect_database(cmd):
    # Open database connection
    try:
        conn = MySQLdb.connect(db="oilcop",host="localhost",user="root",passwd="nosoup4u");
        print ""
        print "Connected to Database"
        #prepare a cursor object using cursor() method
        cursor = conn.cursor()
        return (cursor.execute(cmd))    # execute a read from database
        
    except:
        print "Cannot connect to server.</br>"
        sys.exit(1)
