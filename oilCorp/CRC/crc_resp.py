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
