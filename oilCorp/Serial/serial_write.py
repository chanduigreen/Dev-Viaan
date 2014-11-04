# Writes command received from database to transceiver serial port
# Inputs: The packet to send
# Outputs: None

## Importing the Module crc_resp
from CRC.crc_resp import crc_resp
from Serial.serial import connect_serial 

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
		connect_serial(data_string)
		#ser.write(data_string)
	except:
		print "Failed to send to serial"
		#sys.exit(1)

