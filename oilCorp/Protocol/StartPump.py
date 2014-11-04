from Serial.serial_write import Serial_Write
from Convert.digit_convert import ConvertPreset

# New Index accessors for queries
QUERY_F_ID_INDEX        = int(0)            # 0
QUERY_DEVICE_ID_INDEX     = QUERY_F_ID_INDEX + int(1)        # 1
QUERY_HW_ADDR_INDEX        = QUERY_DEVICE_ID_INDEX + int(1)# 2
QUERY_COMMAND_ID_INDEX    = QUERY_HW_ADDR_INDEX + int(1)        # 3
QUERY_START_TOP_INDEX    = QUERY_COMMAND_ID_INDEX + int(1)    # 4
QUERY_PORT_INDEX        = QUERY_START_TOP_INDEX + int(1)# 5
QUERY_PRESET_INDEX        = QUERY_PORT_INDEX + int(1)
QUERY_UNIT_INDEX        = QUERY_PRESET_INDEX + int(1)
QUERY_SEGMENT_INDEX        = int(15)
QUERY_CRC_INDEX            = int(17)


#============================================== START PUMP ==============================================================    

def Protocol_StartPump(query):
    print "Start Pump Command"
    # check to make sure there is a preset amount
    
    if query[QUERY_PRESET_INDEX] != 0:
        print "getting here"
        Digits = ConvertPreset(value=query[QUERY_PRESET_INDEX])
        print "past digits"
        responsePacket = [] 
        
        for data in [QUERY_DEVICE_ID_INDEX,QUERY_HW_ADDR_INDEX,QUERY_COMMAND_ID_INDEX,QUERY_START_TOP_INDEX,QUERY_PORT_INDEX]:
            responsePacket.append(query[data])
        #responsePacket.append(query[])
        #responsePacket.append(query[])
        #responsePacket.append(query[])
        #responsePacket.append(query[])
        
        for i in range(5):
            responsePacket.append(Digits[i])
        #responsePacket.append(Digits[1])
        #responsePacket.append(Digits[2])
        #responsePacket.append(Digits[3])
        #responsePacket.append(Digits[4])
        
        responsePacket.append(query[QUERY_UNIT_INDEX])
        for i in range(2):
            responsePacket.append(0)
        
        #responsePacket.append(0)
        #responsePacket.append(0)
        responsePacket.append(query[QUERY_SEGMENT_INDEX])
        
        responsePacket.append(0)
        responsePacket.append(0)
        print "Sending to TR"
        
        Serial_Write(responsePacket)
