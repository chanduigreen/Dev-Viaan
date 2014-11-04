# Reads serial input from transceiver
# Data comes in as hex
# Inputs: None
# Outputs: String buffer of values received

from Convert.convert_data import ConvertData

def Serial_Read(ser):
	buf = ''
	globvar = ser.read(size=17) 										# read a byte
	buf =  buf + globvar 												# accumalate the response
	data = list(buf)
	
	#new_buff = ConvertData(buff=data) 									# convert and print
	#return new_buff
	return ConvertData(buff=data)