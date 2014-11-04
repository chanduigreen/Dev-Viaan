# Parses the received command
# If the current id is the same as last id, don't do anything
# Inputs: the row data as hex strings
# Outputs: True means good to go, False means don't do anything

from Protocol.TopOff import Protocol_TopOff
from Protocol.StartPump import Protocol_StartPump


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

F_ID_INDEX = 0
START_TANK_INDEX = 3 # really 2, but f_id increases index by 1
START_TANK_TOPOFF_CMD = 204   			#0xCC

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
            # Start tank or top-off command
            if int(command) == int(START_TANK_TOPOFF_CMD):
                if int(row_data[QUERY_START_TOP_INDEX]) == int(1):
                    Protocol_TopOff(query=row_data)     # command is a top-off
                else:
                    Protocol_StartPump(query=row_data)    # command is a start pump
                
    except:
        print "index error in database parse"
        return False
   
    #print "Server Command does not match any command ids"
    return False # no command found
