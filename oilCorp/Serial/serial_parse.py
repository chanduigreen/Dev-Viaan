# Parses the serial packet to determine if the packet is in correct format
# Inputs: The serial packet as a string array received as hex
# Outputs: True means can write to database, False means ignore   


from Protocol.NewDisplayValue import Protocol_NewDisplayValue
from Protocol.StartTankResponse import Protocol_StartTankResponse
from thread import threading
# Start Tank Command Information
DISPENSE_COMPLETE_CMD = 206                #0xCE
NEW_VALUE_CMD = 4

# Hardware Configuration Command Information
GET_HARDWARD_CONFIG_CMD = 45

# Start Tank Command Information
#NEW_VALUE_CMD = 4
START_TANK_TOPOFF_CMD = 204               #0xCC
START_TANK_TOPOFF_RESPONE_CMD = 205     #0xCD
lock=threading.Lock()

def Serial_Parse(raw_data):
    #print ""
    #print "Parsing Serial Data"
    lock.acquire()
    try:
        command = raw_data[2]
        #print "command from serial:", command
        # command was stop tank
        if command == str(DISPENSE_COMPLETE_CMD):
            return True

        if command == str(NEW_VALUE_CMD):
            #print "New Value Found"
            #print raw_data
            Protocol_NewDisplayValue(packet=raw_data)
            return True
         
        if command == str(GET_HARDWARD_CONFIG_CMD):
            print "Hardware Config Command Found"
            Protocol_HwConfig(packet=raw_data)
            return False
            
        if command == str(START_TANK_TOPOFF_RESPONE_CMD):
            Protocol_StartTankResponse(packet=raw_data)
        #print "No command found"
    except:
        #print "Serial Parse Fail"
        return False
    finally:
        lock.release()
    return False
