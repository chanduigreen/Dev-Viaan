#!/usr/bin/python
import serial
import time
import sys
import MySQLdb
import MySQLdb.constants.CLIENT
import time

# debugging value
index = 0

# Start up flag
fDoneStartUp = False

# Serial Settings
Baudrate = 9600
SerialPort = '/dev/ttyUSB0'

# MySQL table information
T_TRANSCEIVER_SERVER = 0
T_DEVICES_SOFTWARE = 1

# Web Ping command Information
WEB_PING_CMD = 208
WEB_PING_STATUS = 55

# Start Tank Command Information
NEW_VALUE_CMD = 4
CHECK_PIN_RESP_CMD = 6
GET_STATIONS_CMD = 7
GET_STATION_MAPPING_CMD = 8
GET_FCM_INFORMATION_CMD = 9
START_PUMP_FROM_OTEC_CMD = 10
GET_PRODUCTS_CMD = 11
GET_PRODUCT_MAPPING_CMD = 12
GET_WORK_ORDER_CMD = 13
GET_USER_WORK_ORDER_CMD = 14
GET_WORK_ORDER_INFO_CMD = 15
START_TANK_TOPOFF_CMD = 204   		
START_TANK_TOPOFF_RESPONE_CMD = 205 	
DISPENSE_COMPLETE_CMD = 206
DISPENSE_COMPLETE_RESP_CMD = 206				
EMERGENCY_TIMEOUT_STOP_CMD = 207
EMERGENCY_TIMEOUT_STOP_RESP_CMD = 207
WEBSITE_PING_CMD = 208
REEL_CALIBRATION_STOP_CMD = 210
REEL_CALIBRATION_STOP_RESP_CMD = 210

# Hardware Configuration Command Information
GET_HARDWARD_CONFIG_CMD = 45
SEND_HARDWARE_CONFIG_CMD = 46
SEND_HW_CONFIG_STATUS_INDEX = 1
HW_CONFIG_START = 0
HW_CONFIG_NEXT_DEVICE = 1
HW_CONFIG_DEVICE_ERROR = 254

# New Index accessors for queries
QUERY_F_ID_INDEX		= int(0)			# 0
QUERY_DEVICE_ID_INDEX 	= QUERY_F_ID_INDEX + int(1)		# 1
QUERY_HW_ADDR_INDEX		= QUERY_DEVICE_ID_INDEX + int(1)# 2
QUERY_COMMAND_ID_INDEX	= QUERY_HW_ADDR_INDEX + int(1)		# 3
QUERY_START_TOP_INDEX	= QUERY_COMMAND_ID_INDEX + int(1)	# 4
QUERY_PORT_INDEX		= QUERY_START_TOP_INDEX + int(1)# 5
QUERY_PRESET_INDEX		= QUERY_PORT_INDEX + int(1)
QUERY_UNIT_INDEX		= QUERY_PRESET_INDEX + int(1)
QUERY_SEGMENT_INDEX	    = int(15)
QUERY_CRC_INDEX			= int(17)

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

# Number of pulses based on units
Units = [368, 92, 46, 97] # GALLONS, QUARTS, PINTS, LITERS

# Defintions for indexing Database
f_id = 0       	# the most current command received table
last_id = 0 	# the last command executed from table

# Command to insert into database
sql_insert = '''INSERT INTO t_transceiver_server(f_bit0, f_bit1, f_bit2, f_bit3, f_bit4, f_bit5, f_bit6, f_bit7, f_bit8, f_bit9, f_bit10, f_bit11, f_bit12, f_bit13, f_bit14, f_bit15, f_bit16) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
sql_updateHW = """UPDATE t_devices_software SET f_connection_status=%s"""

#f_id, f_fcm_id, f_hw_addr, f_cmd_id, f_st_top, f_reel_channel, f_preset, f_units, f_bit7, f_bit8, f_bit9, f_bit10, f_bit11, f_bit12, f_bit13, f_seg_addr, f_bit15

# Command to receive most recent command sent
sql_pump = "SELECT * FROM t_server_transceiver ORDER BY f_id DESC LIMIT 1"
sql_getHw = "SELECT * FROM t_protocol_hw ORDER BY f_id DESC"
sql_hw = "SELECT COUNT(*) FROM t_protocol_hw"
sql_getSingleHw = "SELECT * FROM t_devices_software WHERE f_devices_software_id=%s LIMIT 1"
sql_userDetailsRetrieve = "SELECT * FROM t_users_details WHERE f_user_pin=%s"
sql_userCapabilitiesRetrieve = "SELECT * FROM t_user_capabilities_map WHERE f_user_id=%s"
sql_getStationCount = "SELECT COUNT(*) FROM t_stations"
sql_getStations = "SELECT * FROM t_stations ORDER BY f_station_id DESC"
sql_getStationMapCount = "SELECT COUNT(*) FROM t_user_station_map WHERE f_user_id=%s"
sql_getStationMap = "SELECT * FROM t_user_station_map WHERE f_user_id=%s"
sql_GetFcmInfo = "SELECT * FROM t_reel_data WHERE f_product_id=%s"
sql_getProductCount = "SELECT COUNT(*) FROM t_products"
sql_getProducts = "SELECT * FROM t_products ORDER BY f_product_id DESC"
sql_getProductMap = "SELECT f_tank_product_id FROM t_tank_details INNER JOIN t_tank_station_map USING (f_tank_id) WHERE f_station_id=%s"
sql_getWorkOrderCount = "SELECT COUNT(*) FROM t_adjust_workorder WHERE f_workorder_completed=0"
sql_getWorkOrders = "SELECT f_adjustwo_id, f_workorder_id FROM t_adjust_workorder WHERE f_workorder_completed=0 ORDER BY f_adjustwo_id DESC"
sql_getWorkOrderMap = "SELECT f_adjustwo_id FROM t_adjust_workorder WHERE f_user_id=%s AND f_workorder_completed=0"
sql_getWorkOrderInfo = "SELECT * FROM t_adjust_workorder WHERE f_adjustwo_id=%s"
sql_getReelInfo = "SELECT * FROM t_reel_data WHERE f_reel_id=%s"
sql_getMaxDispenseAmount = "SELECT f_open_dispense FROM t_adminstrative_options"


# Open database connection
try:
	conn = MySQLdb.connect(db="oilcop",host="localhost",user="root",passwd="nosoup4u");
	print ""
	print "Connected to Database"
except:
	print "Cannot connect to server.</br>"
	sys.exit(1)

#prepare a cursor object using cursor() method
cursor = conn.cursor()

# Holds serial info
ser = None
fSerialDone = 0

def Open_Serial():
	global ser
	try:
		ser = serial.Serial(SerialPort, Baudrate, timeout=.03, xonxoff=False, rtscts=False, dsrdtr=False)
		ser.flushInput()  # Get the garbage out of the input buffer
		ser.flushOutput() # Get the garbage out of the output buffer
		return 1
	except:
		return 0 

# Converts serial data into readable format
# Inputs: the 17 byte buffer
# Outputs: the new converted buffer
def ConvertData(buff):
	try:
		for i in range(0, 17):
			buff[i] =  str(ord(buff[i]))
        	#print "FROM T/R"
        	#print buff
        	#print (datetime.datetime.now())
        	return buff
	except:
        	return 0
        	#print "No data from serial"

# Calculates the CRC code to see if we received valid data
# Sums up all bytes and compares to final byte
# Inputs: The packet for crc to be calculated
# Outptus: the packet with updated crc value
def crc_resp(crc_packet):
	#print "Calculating CRC..."
	crc_sum = 0
	for i in range(0,18):
		crc_sum = crc_packet[i] + crc_sum

	while crc_sum > 255:
		crc_sum = crc_sum - 256

	#print "CRC Value: %d" % crc_sum
	crc_packet[CRC] = crc_sum
	return crc_packet

# Parses returned tuples by the database into a single list
# Input: the database tuples
# Output: the list of values
def Parse_Tuples(tuples):
	id_list = []
	for index in range(0,17):
		id_list.append(tuples[index])
	return id_list

# Reads a row from the transeiver receive table in database
# Inputs: None
# Outputs: None
def Database_Read(sql_receive, readType, parameters):
	#print ""
	#print "Reading from database"
	try:
		if readType == 1:
			cursor.execute(sql_receive)    # execute a read from database
			row = cursor.fetchone()        # collect the row read
		elif readType == 0:
			cursor.execute(sql_receive)    # execute a read from database
			row = cursor.fetchall()
		elif readType == 2:
			cursor.execute(sql_receive, parameters[0])    	# execute a read from database
			row = cursor.fetchone()        					# collect the row read
		elif readType == 3:
			cursor.execute(sql_receive, parameters[0])    	# execute a read from database
			row = cursor.fetchall()        					# collect the row read
		elif readType == 4:
			cursor.execute(sql_receive, parameters[0], parameters[1])
			row = cursor.fetchone()
		conn.commit()
		if row == None:					# database did not find row
			return '0'
		new_row = list(row)
		#print "Row:", new_row
		return new_row                 # return row
	except:
		return '0'

# Parses the received command
# If the current id is the same as last id, don't do anything
# Inputs: the row data as hex strings
# Outputs: True means good to go, False means don't do anything
def Database_Parse(row_data):
	#print ""
	#print "Parsing command received from database"
	try:
		packet = row_data[F_ID_INDEX]
		command = row_data[START_TANK_INDEX]

		# check to see if there is a new command from web server
		if packet == last_id:
			return False
		else:
			print "Data Parse:",row_data

			# Start tank or top-off command
			if int(command) == int(START_TANK_TOPOFF_CMD):
				if int(row_data[QUERY_START_TOP_INDEX]) == int(1):
					Protocol_TopOff(query=row_data) 	# command is a top-off
				else:
					Protocol_StartPump(query=row_data)	# command is a start pump
				return True
					
			# check to see if there is a ping command from web server
			if int(command) == int(WEB_PING_CMD):
				Protocol_WebPing(query=row_data)
				return True			

			# tell FCM to complete the dispense
			if int(command) == int(DISPENSE_COMPLETE_CMD):
				Protocol_DispenseComplete(query=row_data)
				return True

			# tell FCM to STOP NOW
			if int(command) == int(EMERGENCY_TIMEOUT_STOP_CMD):
				Protocol_EmergencyTimeoutStop(query=row_data)
				return True

			# stop the pumping and get number of pulses
			if int(command) == int(REEL_CALIBRATION_STOP_CMD):
				Protocol_ReelCalibrationStop(query=row_data)
				return True

			return False
		
	except:
		print "index error in database parse"
		return False
   
	#print "Server Command does not match any command ids"
	return False # no command found
         
# Write received serial command to server receive table
# Inputs: the packet that needs to be written as a string
# Outputs: None
def Database_Write(buff, table):
	#print "Writing to database"
	#print buff
	#StartTime = time.time()
	if table == T_TRANSCEIVER_SERVER:
		cursor.execute(sql_insert, (buff[0],buff[1],buff[2],buff[3],buff[4],buff[5],buff[6],buff[7],buff[8],buff[9],buff[10],buff[11],buff[12],buff[13],buff[14],buff[15],buff[16]))
	elif table == T_DEVICES_SOFTWARE:
		cursor.execute(sql_updateHW, (buff))
	conn.commit()
	#EndTime = time.time()
	#print "Database Write Time:", EndTime-StartTime

# Reads serial input from transceiver
# Data comes in as hex
# Inputs: None
# Outputs: String buffer of values received
def Serial_Read():
	global fSerialDone
	try:
		#print ""
		#print "Reading from serial"
		buf = ''
		globvar = ser.read(size=17) #read a byte
		#print globvar.encode("hex") #gives me the correct bytes, each on a newline
		buf =  buf + globvar #accumalate the response
		data = list(buf)
		new_buff = ConvertData(buff=data) # convert and print
		return new_buff
	except:
		"getting here"
		fSerialDone = 0
		ser.close()
		return 0
		

# Parses the serial packet to determine if the packet is in correct format
# Inputs: The serial packet as a string array received as hex
# Outputs: True means can write to database, False means ignore   
def Serial_Parse(raw_data):
	#print ""
	#print "Parsing Serial Data"
	try:
		command = raw_data[2]

		#print "command from serial:", command

		if command == str(NEW_VALUE_CMD):
			#print "New Value Found"
			#print raw_data
			Protocol_NewDisplayValue(packet=raw_data)
			return False
		 
		elif command == str(GET_HARDWARD_CONFIG_CMD):
			print "Hardware Config Command Found"
			Protocol_HwConfig(packet=raw_data)
			return False
			
		elif command == str(START_TANK_TOPOFF_RESPONE_CMD):
			Protocol_StartTankResponse(packet=raw_data)
			return False
			
		elif command == str(DISPENSE_COMPLETE_RESP_CMD):
			Protocol_DispenseCompleteResponse(packet=raw_data)
			return False
			
		elif command == str(EMERGENCY_TIMEOUT_STOP_RESP_CMD):
			Protocol_EmergencyTimeoutStopResponse(packet=raw_data)
			return False
			
		elif command == str(REEL_CALIBRATION_STOP_RESP_CMD):
			Protocol_ReelCalibrationStopResponse(packet=raw_data)
			return False
			
		elif command == str(CHECK_PIN_RESP_CMD):
			Protocol_CheckPinResponse(packet=raw_data)
			return False
			
		elif command == str(GET_STATIONS_CMD):
			Protocol_GetStations(packet=raw_data)
			return False
			
		elif command == str(GET_STATION_MAPPING_CMD):
			Protocol_GetStationUserMapping(packet=raw_data)
			return False
			
		elif command == str(GET_FCM_INFORMATION_CMD):
			Protocol_GetFCMInforamiton(packet=raw_data)
			return False
			
		elif command == str(GET_PRODUCTS_CMD):
			Protocol_GetProducts(packet=raw_data)
			return False
			
		elif command == str(GET_PRODUCT_MAPPING_CMD):
			Protocol_GetProductUserMapping(packet=raw_data)
			return False
			
		elif command == str(GET_WORK_ORDER_CMD):
			Protocol_GetWorkOrderInformation(packet=raw_data)
			return False
			
		elif command == str(GET_USER_WORK_ORDER_CMD):
			Protocol_GetUserWorkOrderInformation(packet=raw_data)
			return False
			
		elif command == str(GET_WORK_ORDER_INFO_CMD):
			Protocol_GetSpecificWorkOrderInfo(packet=raw_data)
			return False

		#print "No command found"
	except:
		#print "Serial Parse Fail"
		return False

	return False

# Writes command received from database to transceiver serial port
# Inputs: The packet to send
# Outputs: None
def Serial_Write(database_packet):
	print ""
	print "Writing to T/R"
	data = database_packet
	#print data
	try:
		preambleByteOne = int(59)
		preambleByteTwo = int(150)	
		for i in range(0, 17):
			data[i] = int(data[i])
		data.insert(0, preambleByteOne)
		data.insert(1, preambleByteTwo)	
		data = crc_resp(crc_packet = data)
		print data
		string_data = ''
		for i in range(0,19):
			data[i] = chr(data[i])
		#print "data to send", data
		data_string = ''.join(data)
		print "sending serial data"
		ser.write(data_string)
	except:
		print "Failed to send to serial"
		#sys.exit(1)

# Converts floating point number into fixed point
# Inputs: a value 0 - 9999
# Outputs: 4 digits and a decimal place 1 means 10ths, 2 means 100ths
def ConvertPreset(value):
	value = float(value)
	decimal = 0
	if value < 1000:
		value = int(value*10)
		decimal = 1
	else:
		decimal = 3
	digits = []
	digits.append(decimal) # insert a 1 meaning value has tenths
	for i in range(0, 4):
		digits.insert(0,value%10)
		value = value/10
	return digits

# Converts 4 bytes into a single unsigned long number
# Inputs: 4 bytes
# Outputs: Single unsigned long value
def ConvertBytesToLong(digits):
   for i in range(0, len(digits)):
      digits[i] = int(digits[i])
   value = int((digits[0]<<24) | (digits[1]<<16) | (digits[2]<<8) | (digits[3]))
   return value
   
# Converts 2 bytes into a single unsigned short number
# Inputs: 2 bytes
# Outputs: Single unsigned short value
def ConvertBytesToShort(digits):
	for i in range(0, len(digits)):
		digits[i] = int(digits[i])
	return int((digits[0]<<8) | (digits[1]))
	
# Converts fixed point number with 4 digits and decimal placement to floating point number.
# Values can be between 0 to 9999 with resolution going into the hundredths.
# a decimal of 1 means tenths and 2 means hundredths. 
# Inputs: a list containing 4 digits with most significant digit first and decimal place last
# Outputs: a single floating point number
def ConvertDecToPreset(digits):
   for i in range(0, len(digits)):
      digits[i] = float(digits[i])
   value = float((digits[0]*1000) + (digits[1]*100) + (digits[2]*10) + (digits[3]))
   value = float(value/10)
   print "New Value: ", value
   return value
   
#StartTankOneCmd = '\xFF\x03\xCC\x00\x01\x00\x0B\x00\x00\x00\x00\x00\x00\x00\x03\x00\xDD'
#print "TX: %s" StartTankOneCmd
#ser.write(StartTankOneCmd)
   
#========================================= GET HARDWARE CONFIGURATION ===================================================
def Protocol_HwConfig(packet):
	print packet
	if packet[SEND_HW_CONFIG_STATUS_INDEX] == str(HW_CONFIG_START):
		print "Starting Hardware Config"
		# Transceiver wants all hardware device configurations from website
		HardwareNumTuple = Database_Read(sql_receive=sql_hw, readType=0, parameters=0) # gets the number of total devices
		HardwareNum = int(HardwareNumTuple[0][0])						 # converts the number into readable format
		print HardwareNum
		allDevices = Database_Read(sql_receive=sql_getHw, readType=0, parameters=0)	 # gets the configuration for all devices
		aDevice = Parse_Tuples(tuples=allDevices[0])					 # gets the very first device
		for i in range(0, len(aDevice)):
			aDevice[i] = int(aDevice[i])								 # converts device configuration into readable format
		print aDevice
		responsePacket = []												 # Make the 17 bytes response packet to be sent to serial
		responsePacket.append(HardwareNum)				# Number of Devices
		responsePacket.append(0)				 	    # Null
		responsePacket.append(46)					 	# Command ID
		responsePacket.append(0)						# Status ID: Not the final buffer=0
		responsePacket.append(1)						# Current device beng sent
		responsePacket.append(aDevice[5])				# Device ID
		responsePacket.append(aDevice[6])				# Hardware Address
		responsePacket.append(aDevice[7])				# Device Status
		responsePacket.append(aDevice[8])						# Null
		responsePacket.append(aDevice[9])						 # Null
		responsePacket.append(aDevice[10])						 # Null
		responsePacket.append(aDevice[11])						 # Null
		responsePacket.append(0)						 # Null
		responsePacket.append(0)						# Null
		responsePacket.append(0)						# Null
		responsePacket.append(0)						# Null
		responsePacket.append(0)						# CRC calculated in Serial_Write
		print responsePacket
		Serial_Write(responsePacket)
	else:
		# Check to see if device was found
		if packet[SEND_HW_CONFIG_STATUS_INDEX] == str(HW_CONFIG_NEXT_DEVICE):
			Database_Write(buff=str(0), table=T_DEVICES_SOFTWARE)				# write success status to database
		else:
			print "Hardware Config Error"
			Database_Write(buff=str(254), table=T_DEVICES_SOFTWARE)				# write error status to database
			
		# Transceiver is ready to receive next device
		HardwareNumTuple = Database_Read(sql_receive=sql_hw, readType=0, parameters=0) 		# gets the number of total devices
		HardwareNum = int(HardwareNumTuple[0][0])						 		# converts the number into readable format
		if packet[3] <= str(HardwareNum):										# make sure this wasn't the last device to send
			nextDevice = int(packet[3])+1
			print "Current Device:", nextDevice
			allDevices = Database_Read(sql_receive=sql_getHw, readType=0, parameters=0)	 	# gets the configuration for all devices
			aDevice = Parse_Tuples(tuples=allDevices[int(packet[3])])			# gets the next device
			for i in range(0, len(aDevice)):
				aDevice[i] = int(aDevice[i])								 	# converts device configuration into readable format	
			responsePacket = []												 	# Make the 17 bytes response packet to be sent to serial
			responsePacket.append(HardwareNum)				 # Number of Devices
			responsePacket.append(0)				 	     # Null
			responsePacket.append(46)					 	 # Command ID
			responsePacket.append(0)						 # Status ID: Not the final buffer=0
			responsePacket.append(nextDevice)				 # Current device beng sent
			responsePacket.append(aDevice[5])				 # Device ID
			responsePacket.append(aDevice[6])				 # Hardware Address
			responsePacket.append(aDevice[7])				 # Device Status
			responsePacket.append(aDevice[8])						 # Null
			responsePacket.append(aDevice[9])						 # Null
			responsePacket.append(aDevice[10])						 # Null
			responsePacket.append(aDevice[11])						 # Null
			responsePacket.append(0)						 # Null
			responsePacket.append(0)						 # Null
			responsePacket.append(0)						 # Null
			responsePacket.append(0)						 # Null
			responsePacket.append(0)						 # CRC calculated in Serial_Write
			Serial_Write(responsePacket)
		
#============================================== START PUMP ==============================================================	
def Protocol_StartPump(query):
	print "Start Pump Command"
	# check to make sure there is a preset amount
	if query[QUERY_PRESET_INDEX] != 0:
		# Get kFactor code goes here
		kFactor = 1.0
		# Get units
		
		amountOfPulses = int(float(query[QUERY_PRESET_INDEX])*float(Units[int(query[QUERY_UNIT_INDEX])])*kFactor)
		print "Amount of pulses to pump", amountOfPulses

		print "past digits"
		responsePacket = [] 
		responsePacket.append(query[QUERY_DEVICE_ID_INDEX])
		responsePacket.append(query[QUERY_HW_ADDR_INDEX])
		responsePacket.append(query[QUERY_COMMAND_ID_INDEX])
		responsePacket.append(query[QUERY_START_TOP_INDEX])
		responsePacket.append(query[QUERY_PORT_INDEX])
		responsePacket.append((amountOfPulses&0xFF000000)>>24)
		responsePacket.append((amountOfPulses&0x00FF0000)>>16)
		responsePacket.append((amountOfPulses&0x0000FF00)>>8)
		responsePacket.append((amountOfPulses&0x000000FF))
		responsePacket.append(0)
		#responsePacket.append(query[QUERY_UNIT_INDEX])
		responsePacket.append(1) # units quarts
		responsePacket.append(0)
		responsePacket.append(0)
		responsePacket.append(0)
		responsePacket.append(query[QUERY_SEGMENT_INDEX])
		responsePacket.append(0)
		responsePacket.append(0)
		print "Sending to TR"
		Serial_Write(responsePacket)
		
#========================================== START PUMP RESPONSE =========================================================
def Protocol_StartTankResponse(packet):
	print "Start Tank Response:",packet
	Database_Write(buff=packet, table=T_TRANSCEIVER_SERVER)
			
#=============================================== TOP OFF ================================================================
def Protocol_TopOff(query):
	print "Top Off Command"
	
#============================================ NEW DISPLAY VALUE =========================================================
def Protocol_NewDisplayValue(packet):
	#print "New Display Value"
	print packet
	
	# convert pulses into unsigned long value
	fixedDigits = []
	fixedDigits.append(packet[5])
	fixedDigits.append(packet[6])
	fixedDigits.append(packet[7])
	fixedDigits.append(packet[8])
	fixedDigits.append(packet[9])
	newValue = ConvertBytesToLong(digits=fixedDigits)
	
	# convert kFactor to unsigned short value
	fixedDigits = []
	fixedDigits.append(packet[11])
	fixedDigits.append(packet[12])
	newValueTwo = ConvertBytesToShort(digits=fixedDigits)
	kFactor = float(newValueTwo)/1000.0
	
	valueToDisplay = format(float((newValue)/(kFactor*Units[int(packet[9])])), '.1f')
	
	print valueToDisplay
	
	databasePacket = []
	for i in range(0, 5):
		databasePacket.append(packet[i])
	databasePacket.append(str(valueToDisplay))
	for i in range(6, 17):
		databasePacket.append(0)
	#print databasePacket
	Database_Write(buff=databasePacket, table=T_TRANSCEIVER_SERVER)

#================================================= WEB PING =============================================================	
def Protocol_WebPing(query):
	print "Pinging FCM"
	query.pop(0)
	print query
	Serial_Write(query)
	
#============================================ DISPENSE COMPLETE =========================================================
def Protocol_DispenseComplete(query):
	print "Dispense Complete for FCM"
	query.pop(0)
	Serial_Write(query)

#========================================== DISPENSE COMPLETE RESPONSE ==================================================	
def Protocol_DispenseCompleteResponse(packet):
	print "Dispense Complete Response"
	aDigits = []
	aDigits.append(packet[7])
	aDigits.append(packet[8])
	aDigits.append(packet[9])
	aDigits.append(packet[10])
	value = ConvertDecToPreset(aDigits)
	packet[5] = value
	Database_Write(buff=packet,table=T_TRANSCEIVER_SERVER)

#========================================== EMERGENCY/TIMEOUT STOP ======================================================
def Protocol_EmergencyTimeoutStop(query):
	print "Emergency or Timeout Stop"
	query.pop(0)
	Serial_Write(query)

#====================================== EMERGENCY/TIMEOUT STOP RESPONSE =================================================
def Protocol_EmergencyTimeoutStopResponse(packet):
	print "Emergency or Timeout Stop Response"
	Database_Write(buff=packet,table=T_TRANSCEIVER_SERVER)

#========================================= REEL CALIBRATION STOP ========================================================
def Protocol_ReelCalibrationStop(query):
	print "Reel Calibration Stop"
	query.pop(0) # pops the f_id in the front of the list
	Serial_Write(query)

#====================================== REEL CALIBRATION STOP RESPONSE ==================================================
def Protocol_ReelCalibrationStopResponse(packet):
	print "Reel Calibration Stop Response"	
	aDigits = []
	aDigits.append(packet[6])
	aDigits.append(packet[7])
	aDigits.append(packet[8])
	aDigits.append(packet[9])
	value = ConvertBytesToLong(aDigits)
	print "Pulses: ", value
	packet[5] = value
	packet[6] = 0
	packet[7] = 0
	packet[8] = 0
	packet[9] = 0
	Database_Write(buff=packet,table=T_TRANSCEIVER_SERVER)
	
#=========================================== CHECK PIN VALUE RESPONSE ===================================================
def Protocol_CheckPinResponse(packet):
	print "NEW PIN CHECK"
	print packet
	pinNumber = ""
	for i in range(int(packet[3])):
		pinNumber = pinNumber+chr(int(packet[i+4]))
	print "User pin", pinNumber
	
	number = []
	number.append(pinNumber)
	# Get the user pertaining to pin number
	user = Database_Read(sql_receive=sql_userDetailsRetrieve, readType=2, parameters=number)
	print user
	if user == '0': # user did not exist
		packet[3] = 0
		Serial_Write(packet)
		return
	else:
		for i in range(len(user)):
			user[i] = str(user[i])
	
	# Get user capabilites
	capabilities = Database_Read(sql_receive=sql_userCapabilitiesRetrieve, readType=2, parameters=user) # reads from t_user_capabilities_map table
	if capabilities == '0': # user is not enabled
		packet[3] = 0
		Serial_Write(packet)
		return
	
	print capabilities
	caps_list = []
	caps_list = capabilities[1].split(",")
	#print caps_list
	
	packet[3] = user[0] # technicians id

	user[8] = int(user[8])  # user enabled
	user[9] = int(user[9])  # emergency stop
	user[10] = int(user[10]) # calibrate
	user [11] = int(user[11]) # kfactor
	perm = user[8] | (user[9]<<1) | (user[10]<<2) | (user[11]<<3)
	print "perm 1:", perm
	if '1' in caps_list: # Preset
		perm = perm | 16
	if '2' in caps_list: # Open Dispense
		perm = perm | 32
	if '3' in caps_list: # Select Work Order
		perm = perm | 64
	if '4' in caps_list: # Load Word Order
		perm = perm | 128
	
	print "perm 2:", perm
	packet[4] = str(perm) # store permissions in return packet
	
	# store first name and last name into return packet
	fName = list(user[1])
	lName = list(user[2])
	for i in range(0, 5):
		if (i) >= len(fName):
			fName.append('0')
		if (i) >= len(lName):
			lName.append('0')
	
	for i in range(0,5):
		packet[i+6] = ord(fName[i])
		packet[i+11] = ord(lName[i])
	
	print packet
	Serial_Write(packet)
	
#=================================================== GET STATIONS  ======================================================
def Protocol_GetStations(packet):
	print "Getting Stations"
	print packet

	# get the information about stations from database
	StationNumTuple = Database_Read(sql_receive=sql_getStationCount, readType=0, parameters=0) # gets the number of total stations
	StationNum = int(StationNumTuple[0][0])	# converts the number into readable format
	print "Number of Stations", StationNum
	allStations = Database_Read(sql_receive=sql_getStations, readType=0, parameters=0)	 	# gets all station information
	aStation = allStations[int(packet[4])]
	#aStation = Parse_Tuples(tuples=allStations[int(packet[4])])							# gets the information of station specified by packet
	print aStation
	# set up the return packet
	stationName = []
	stationName = list(aStation[1])
	packet[3] = StationNum
	packet[4] = str(int(packet[4])+1)
	packet[5] = str(int(aStation[0]))
	packet[6] = str(int(aStation[2]))
	for i in range(0, 9):
		if i < len(stationName):
			packet[i+7] = ord(stationName[i])
		else:
			packet[i+7] = ord('0')
	print "Packet to serial", packet
	Serial_Write(packet)
	
#========================================== GET STATIONS USER MAPPING  ==================================================
def Protocol_GetStationUserMapping(packet):	
	print "Station Mapping Command"
	print packet
	
	id = []
	id.append(packet[3])
	# get information about mapping from database
	allMappings = Database_Read(sql_receive=sql_getStationMap, readType=3, parameters=id)	 	# gets all station information
	print "Getting here"
	
	if allMappings == '0':
		return False
	
	aMapping = []
	for i in range(0, len(allMappings)):
		print allMappings[i]
		if allMappings[i][1].find(",") == -1:
			aMapping.append(str(allMappings[i][1]))
	
	print "Number of User Stations",int(len(aMapping))
	packet[3] = int(len(aMapping))
	for i in range(0, int(len(aMapping))):
		packet[i+4] = aMapping[i]
		
	for i in range( int(len(aMapping))+4, 17):
		packet[i] = '0'
		
	print packet
	Serial_Write(packet)
	
#=========================================== GET FCM INFORMATION  =======================================================
def Protocol_GetFCMInforamiton(packet):
	print "FCM Info"
	print packet
	ids = []
	#ids.append(packet[4])
	#ids.append(1)
	ids.append(packet[5])
	#ids.append(packet[4])
	allReelMapping = Database_Read(sql_receive=sql_GetFcmInfo, readType=3, parameters=ids)
	for i in range(0, len(allReelMapping)):
		if int(allReelMapping[i][4]) == int(packet[4]):
			reelMapping = allReelMapping[i]
			break;
		else:
			print "did not find"
			return 0
	print reelMapping
	units = int(reelMapping[7])
	fcmId = int(reelMapping[10])
	remoteId = int(reelMapping[11])
	portId = int(reelMapping[1])
	print "FCM ID:", fcmId
	print "SEGMENT ID:", remoteId
	ids = []
	ids.append(fcmId)
	fcmInfo = Database_Read(sql_receive=sql_getSingleHw, readType=2, parameters=ids)
	print fcmInfo
	
	ids = []
	ids.append(remoteId)	
	segmentInfo = Database_Read(sql_receive=sql_getSingleHw, readType=2, parameters=ids)
	print segmentInfo
	
	fcmAddr = fcmInfo[7]
	segmentAddr = segmentInfo[7]
	
	ddigits = []
	ddigits.append(int(packet[6]))
	ddigits.append(int(packet[7]))
	ddigits.append(int(packet[8]))
	ddigits.append(int(packet[9]))
	ddigits.append(int(packet[10]))
	presetValue = ConvertDecToPreset(digits=ddigits)
	amountOfPulses = int(presetValue*float(Units[1]))
	
	print "Amount of pulses to pump", amountOfPulses
	
	print "We are here"
	txPacket = []
	txPacket.append(8) # fcm device id
	txPacket.append(fcmAddr)
	txPacket.append(START_PUMP_FROM_OTEC_CMD)
	txPacket.append(0)
	txPacket.append(portId)
	txPacket.append((amountOfPulses&0xFF000000)>>24)
	txPacket.append((amountOfPulses&0x00FF0000)>>16)
	txPacket.append((amountOfPulses&0x0000FF00)>>8)
	txPacket.append((amountOfPulses&0x000000FF))
	txPacket.append(0)
	txPacket.append(1) #quarts
	txPacket.append(0)
	txPacket.append(0)
	txPacket.append(0)
	txPacket.append(segmentAddr) # segment address
	txPacket.append(0)
	txPacket.append(0)
	Serial_Write(txPacket)
	
#=================================================== GET PRODUCTS  ======================================================
def Protocol_GetProducts(packet):
	print "Getting Products"
	print packet

	# get the information about products from database
	ProductNumTuple = Database_Read(sql_receive=sql_getProductCount, readType=0, parameters=0) # gets the number of total products
	ProductNum = int(ProductNumTuple[0][0])	# converts the number into readable format
	print "Number of Products", ProductNum
	allProducts = Database_Read(sql_receive=sql_getProducts, readType=0, parameters=0)	 	# gets all product information
	aProduct = allProducts[int(packet[4])]
	print aProduct
	# set up the return packet
	productName = []
	productName = list(aProduct[1])
	packet[3] = ProductNum
	packet[4] = str(int(packet[4])+1)
	packet[5] = str(int(aProduct[0]))
	packet[6] = str(int(aProduct[2]))
	for i in range(0, 9):
		if i < len(productName):
			packet[i+7] = ord(productName[i])
		else:
			packet[i+7] = '0'
	print "Packet to serial", packet
	Serial_Write(packet)
	
#========================================= GET PRODUCT MAPPING  =========================================================
def Protocol_GetProductUserMapping(packet):
	print "Product Mapping Command"
	print packet
	
	id = []
	id.append(packet[3])
	# get information about mapping from database
	allMappings = Database_Read(sql_receive=sql_getProductMap, readType=3, parameters=id)	 	# gets all station information
	print "Getting here"
	
	if allMappings == '0':
		return False
	
	aMapping = []
	for i in range(0, len(allMappings)):
		aMapping.append(str(allMappings[i][0]))
	
	print "Number of User Products",int(len(aMapping))
	packet[3] = int(len(aMapping))
	for i in range(0, int(len(aMapping))):
		packet[i+4] = aMapping[i]
		
	for i in range( int(len(aMapping))+4, 17):
		packet[i] = '0'
		
	print packet
	Serial_Write(packet)
	
#========================================= GET WORK ORDER INFO  =========================================================
def Protocol_GetWorkOrderInformation(packet):
	print "Getting work order info"
	print packet
	
	# get the information about work orders from database
	InfoCount = Database_Read(sql_receive=sql_getWorkOrderCount, readType=0, parameters=0) # gets the number of total work orders
	Count = int(InfoCount[0][0])	# converts the number into readable format
	print "Number of Work Orders", Count
	allWorkOrders = Database_Read(sql_receive=sql_getWorkOrders, readType=0, parameters=0)	 	# gets all work order information
	aWorkOrder = allWorkOrders[int(packet[4])] # get the current work order that needs to be transferred
	print aWorkOrder
	
	# set up the return packet
	workOrderName = []
	workOrderName = list(aWorkOrder[1]) # name of work order is located in spot 2
	packet[3] = Count
	packet[4] = str(int(packet[4])+1)   # update which work order that is being sent
	packet[5] = str(int(aWorkOrder[0])) # work order id
	for i in range(0, 10):
		if i < len(workOrderName):
			packet[i+6] = ord(workOrderName[i])
		else:
			packet[i+6] = '0'
			
	print "Packet to serial", packet
	Serial_Write(packet)	
	
#========================================= GET USER WORK ORDER INFO  ====================================================
def Protocol_GetUserWorkOrderInformation(packet):
	print "Getting Work Order Mapping"
	print packet
	
	id = []
	id.append(packet[3])
	# get information about mapping from database
	allMappings = Database_Read(sql_receive=sql_getWorkOrderMap, readType=3, parameters=id)	 	# gets all work order information
	print "Getting here"
	
	if allMappings == '0':
		return False
	
	aMapping = []
	for i in range(0, len(allMappings)):
		aMapping.append(str(allMappings[i][0]))
	
	if int(len(aMapping)) > 12:
		numWorkOrders = 12
	else:
		numWorkOrders = int(len(aMapping))
	print "Number of Open User Work Orders",numWorkOrders
	packet[3] = numWorkOrders
	for i in range(0, numWorkOrders):
		packet[i+4] = aMapping[i]
		
	for i in range( numWorkOrders+4, 17):
		packet[i] = '0'
		
	print packet
	Serial_Write(packet)
	
#========================================= GET SPECIFIC WORK ORDER INFO  =================================================
def Protocol_GetSpecificWorkOrderInfo(packet):
	print "Getting Specific Work Order Information"
	print packet
	
	id = []
	id.append(packet[3])
	workOrderInfo = Database_Read(sql_receive=sql_getWorkOrderInfo, readType=2, parameters=id) # get fcm id and remote display id
	print workOrderInfo
	
	id = []
	if int(workOrderInfo[10]) == int(0):
		dispenseMax = Database_Read(sql_receive=sql_getMaxDispenseAmount, readType=1, parameters=id) # get max amount that technician can dispense
		print dispenseMax
		digits = ConvertPreset(value=dispenseMax[0]) # preset
	else:
		dispenseMax = float(workOrderInfo[10])
		digits = ConvertPreset(value=dispenseMax)
		
	print digits
	
	stationId = int(workOrderInfo[6]) # station id
	productId = int(workOrderInfo[8]) # product id
	
	print "We are here"
	txPacket = []
	txPacket.append(packet[0]) # fcm device id
	txPacket.append(packet[1])
	txPacket.append(GET_WORK_ORDER_INFO_CMD)
	txPacket.append(stationId)
	txPacket.append(productId)
	txPacket.append(0)
	txPacket.append(digits[0])	# preset d4
	txPacket.append(digits[1])	# preset d3
	txPacket.append(digits[2])	# preset d2
	txPacket.append(digits[3])	# preset d1
	txPacket.append(digits[4])  # preset decimal
	txPacket.append(0)
	txPacket.append(0)
	txPacket.append(0)
	txPacket.append(0) # segment address
	txPacket.append(0)
	txPacket.append(0)
	Serial_Write(txPacket)
	
	
#=========================================== MAIN PART OF SCRIPT ========================================================
# Get the most recent f_id
LastRow = []
LastRow = Database_Read(sql_receive=sql_pump, readType=1, parameters=0)
last_id = LastRow[F_ID_INDEX]
		
while True:

	# serial.Serial opens the serial port defined above
	while fSerialDone == 0:
		fSerialDone = Open_Serial()
		if fSerialDone == 1:
			print "Serial Port Open."
		
	# Check if transceiver wishes to send command to server
	#print "Checking for Serial Data"
	#LoopTimeStart = time.time()
	data = []
	data = Serial_Read()
	flag = Serial_Parse(raw_data=data)

	# Check for commands that server wants transceiver to execute
	#print "Check for new Database row"
	data = []
	data = Database_Read(sql_receive=sql_pump, readType=1, parameters=0)
	tempData = list(data)
	flag = Database_Parse(row_data=data)
	last_id = tempData[F_ID_INDEX]
	#LoopTimeEnd = time.time()
	#print "Loop Time", LoopTimeEnd-LoopTimeStart
      



