# Write received serial command to server receive table
# Inputs: the packet that needs to be written as a string
# Outputs: None

from connect_db import connect_database
from thread import threading
lock=threading.Lock()

def Database_Write(buff, table):
    lock.acquire()
    print "Writing to database"
    print buff
    if table == T_TRANSCEIVER_SERVER:
        cursor=connect_database(sql_insert, (buff[0],buff[1],buff[2],buff[3],buff[4],buff[5],buff[6],buff[7],buff[8],buff[9],buff[10],buff[11],buff[12],buff[13],buff[14],buff[15],buff[16]))
        #cursor.execute(sql_insert, (buff[0],buff[1],buff[2],buff[3],buff[4],buff[5],buff[6],buff[7],buff[8],buff[9],buff[10],buff[11],buff[12],buff[13],buff[14],buff[15],buff[16]))
    elif table == T_DEVICES_SOFTWARE:
        cursor=connect_database(sql_updateHW, (buff))
        #cursor.execute(sql_updateHW, (buff))
    #conn.commit()
    conn.commit()
    EndTime = time.time()
    print "Database Write Time:", EndTime-StartTime
    lock.release()
    