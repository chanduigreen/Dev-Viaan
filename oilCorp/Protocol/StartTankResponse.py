# MySQL table information
T_TRANSCEIVER_SERVER = 0

#========================================== START PUMP RESPONSE =========================================================
def Protocol_StartTankResponse(packet):
    print "Start Tank Response:",packet
    Database_Write(buff=packet, table=T_TRANSCEIVER_SERVER)