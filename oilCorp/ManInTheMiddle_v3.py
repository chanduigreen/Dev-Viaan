#!/usr/bin/python
import serial
import time
import sys
import MySQLdb
import MySQLdb.constants.CLIENT
import datetime

# debugging value
index = 0

# Start up flag
fDoneStartUp = False

# MySQL table information
T_TRANSCEIVER_SERVER = 0
T_DEVICES_SOFTWARE = 1

EMERGENCY_TIMEOUT_STOP_CMD = 207
WEBSITE_PING_CMD = 208



# New Index accessors for serial
SERIAL_DEVICE_ID_INDEX 		= int(0)
SERIAL_HW_ADDR_INDEX		= SERIAL_DEVICE_ID_INDEX + int(1)
SERIAL_COMMAND_ID_INDEX		= SERIAL_HW_ADDR_INDEX + int(1)
SERIAL_START_TOP_INDEX		= SERIAL_COMMAND_ID_INDEX + int(1)
SERIAL_PORT_INDEX			= SERIAL_START_TOP_INDEX + int(1)
SERIAL_STATUS_INDEX			= SERIAL_PORT_INDEX + int(1)

# Old Index accessors
CMD_INDEX = 2
START_TANK_INDEX = 3 # really 2, but f_id increases index by 1
STOP_TANK_INDEX = 4
TANK_INDEX = 5 # really 4, but f_id increases index by 1
F_ID_INDEX = 0
CRC = 18

# Defintions for indexing Database
f_id = 0       	# the most current command received table
last_id = 0 	# the last command executed from table

	
#=========================================== MAIN PART OF SCRIPT ========================================================		
# Get the most recent f_id
from Database.database_read import Database_Read
from thread import threading

LastRow = []
LastRow = Database_Read(sql_receive=sql_pump, readType=1)
last_id = LastRow[F_ID_INDEX]

while True:
	# Check if transceiver wishes to send command to server
	#print "Checking for Serial Data"
	from Serial.serial_read import Serial_Read
	from Serial.serial_parse import Serial_parse
	from Database.database_parse import Database_Parse
	
	data = []        
	data = Serial_Read(ser)
	flag = Serial_Parse(raw_data=data)

	# Check for commands that server wants transceiver to execute
	#print "Check for new Database row"
	data = []
	data = Database_Read(sql_receive=sql_pump, readType=1)
	flag = Database_Parse(row_data=data)
	last_id = data[F_ID_INDEX]
      