# Converts floating point number into fixed point
# Inputs: a value 0 - 9999
# Outputs: 4 digits and a decimal place 1 means 10ths, 2 means 100ths
def ConvertPreset(value):
	print "Start Conversion"
	value = float(value)
	decimal = 0
	if value < 100:
		value = int(value*100)
		decimal = 2
	elif value < 1000:
		value = int(value*10)
		decimal = 1
	else:
		decimal = 3
	digits = []
	digits.append(decimal) # insert a 1 meaning value has tenths
	for i in range(0, 4):
		digits.insert(0,value%10)
		value = value/10
	print "End Converstion"
	return digits
