#! /usr/bin/python

from Convert.fixed_to_present import ConvertDecToPreset
from Database.database_write import Database_Write

T_TRANSCEIVER_SERVER = 0

#============================================ NEW DISPLAY VALUE =========================================================
def Protocol_NewDisplayValue(packet):
    print "New Display Value"
    fixedDigits = []
    for i in range(5,10):
        fixedDigits.append(packet[i])
    #fixedDigits.append(packet[5])
    #fixedDigits.append(packet[6])
    #fixedDigits.append(packet[7])
    #fixedDigits.append(packet[8])
    #fixedDigits.append(packet[9])
    
    newValue = ConvertDecToPreset(digits=fixedDigits)
    
    databasePacket = []
    for i in range(0, 5):
        databasePacket.append(packet[i])
    databasePacket.append(str(newValue))
    
    for i in range(6, 17):
        databasePacket.append(0)
    
    print databasePacket
    Database_Write(buff=databasePacket, table=T_TRANSCEIVER_SERVER)
