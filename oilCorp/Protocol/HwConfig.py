#! /usr/bin/python

from Convert.parse_tuples import Parse_Tuples
from Database.database_write import Database_write
from Database.database_read import Database_read
from Serial.serial_write import Serial_Write

# Command to receive most recent command sent
sql_pump = "SELECT * FROM t_server_transceiver ORDER BY f_id DESC LIMIT 1"
sql_getHw = "SELECT * FROM t_protocol_hw ORDER BY f_id DESC"
sql_hw = "SELECT COUNT(*) FROM t_protocol_hw"

# Hardware Configuration Command Information
SEND_HW_CONFIG_STATUS_INDEX = 1
HW_CONFIG_START = 0
HW_CONFIG_NEXT_DEVICE = 1
HW_CONFIG_DEVICE_ERROR = 254

# MySQL table information
T_TRANSCEIVER_SERVER = 0
T_DEVICES_SOFTWARE = 1

#========================================= GET HARDWARE CONFIGURATION ===================================================

def Protocol_HwConfig(packet):
    print packet[SEND_HW_CONFIG_STATUS_INDEX]
    if packet[SEND_HW_CONFIG_STATUS_INDEX] == str(HW_CONFIG_START):
        print "Starting Hardware Config"
        # Transceiver wants all hardware device configurations from website
        HardwareNumTuple = Database_Read(sql_receive=sql_hw, readType=0) # gets the number of total devices
        HardwareNum = int(HardwareNumTuple[0][0])                         # converts the number into readable format
        print HardwareNum
        
        allDevices = Database_Read(sql_receive=sql_getHw, readType=0)     # gets the configuration for all devices
        aDevice = Parse_Tuples(tuples=allDevices[0])                     # gets the very first device
        
        for i in range(0, len(aDevice)):
            aDevice[i] = int(aDevice[i])                                 # converts device configuration into readable format
        
        print aDevice
        responsePacket = []                                                 # Make the 17 bytes response packet to be sent to serial
        responsePacket.append(HardwareNum)                # Number of Devices
        
        for data in [0,46,0,1]:
            responsePacket.append(data)
        
        #responsePacket.append(0)                         # Null
        #responsePacket.append(46)                         # Command ID
        #responsePacket.append(0)                        # Status ID: Not the final buffer=0
        #responsePacket.append(1)                        # Current device beng sent
        
        for i in range(5,12):
            responsePacket.append(aDevice[i])
        #responsePacket.append(aDevice[5])                #  5 -   Device ID
        #responsePacket.append(aDevice[6])                #  6 -   Hardware Address
        #responsePacket.append(aDevice[7])                #  7 -   Device Status
        #responsePacket.append(aDevice[8])                # Null
        #responsePacket.append(aDevice[9])                # Null
        #responsePacket.append(aDevice[10])               # Null
        #responsePacket.append(aDevice[11])               # Null
        
        for i in range(6):
            responsePacket.append(0)
        #responsePacket.append(0)                         # Null
        #responsePacket.append(0)                        # Null
        #responsePacket.append(0)                        # Null
        #responsePacket.append(0)                        # Null
        #responsePacket.append(0)                        # Null
        #responsePacket.append(0)                        # CRC calculated in Serial_Write
        print responsePacket

        Serial_Write(responsePacket)
    else:
        
        # Check to see if device was found
        if packet[SEND_HW_CONFIG_STATUS_INDEX] == str(HW_CONFIG_NEXT_DEVICE):
            Database_Write(buff=str(0), table=T_DEVICES_SOFTWARE)                # write success status to database
        else:
            print "Hardware Config Error"
            Database_Write(buff=str(254), table=T_DEVICES_SOFTWARE)                # write error status to database
            
        # Transceiver is ready to receive next device
        HardwareNumTuple = Database_Read(sql_receive=sql_hw, readType=0)         # gets the number of total devices
        HardwareNum = int(HardwareNumTuple[0][0])                                 # converts the number into readable format
        
        if packet[3] <= str(HardwareNum):                                        # make sure this wasn't the last device to send
            nextDevice = int(packet[3])+1
            
            print "Current Device:", nextDevice
            allDevices = Database_Read(sql_receive=sql_getHw, readType=0)         # gets the configuration for all devices
            aDevice = Parse_Tuples(tuples=allDevices[int(packet[3])])            # gets the next device
            
            for i in range(0, len(aDevice)):
                aDevice[i] = int(aDevice[i])                                     # converts device configuration into readable format    
            
            responsePacket = []                                                     # Make the 17 bytes response packet to be sent to serial
            responsePacket.append(HardwareNum)                 # Number of Devices
            
            for i in [0,46,0,nextDevice]:
                responsePacket.append(i)
            
            #responsePacket.append(0)                          # Null
            #responsePacket.append(46)                          # Command ID
            #responsePacket.append(0)                         # Status ID: Not the final buffer=0
            #responsePacket.append(nextDevice)                 # Current device beng sent

            for i in range(5,12):
                responsePacket.append(aDevice[i])

            
            #responsePacket.append(aDevice[5])                 # Device ID
            #responsePacket.append(aDevice[6])                 # Hardware Address
            #responsePacket.append(aDevice[7])                 # Device Status
            #responsePacket.append(aDevice[8])                         # Null
            #responsePacket.append(aDevice[9])                         # Null
            #responsePacket.append(aDevice[10])                         # Null
            #responsePacket.append(aDevice[11])                         # Null
            
            for i in range(5):
                responsePacket.append(0)
            
            #responsePacket.append(0)                         # Null
            #responsePacket.append(0)                         # Null
            #responsePacket.append(0)                         # Null
            #responsePacket.append(0)                         # Null
            #responsePacket.append(0)
            # CRC calculated in Serial_Write
            
            Serial_Write(responsePacket)
