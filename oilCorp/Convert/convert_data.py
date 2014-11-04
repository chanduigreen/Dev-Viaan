# Converts serial data into readable format
# Inputs: the 17 byte buffer
# Outputs: the new converted buffer
def ConvertData(buff):
    try:
        for i in range(0, 17):
            buff[i] =  str(ord(buff[i]))
            print "FROM T/R"
            print buff
            #print (datetime.datetime.now())
            return buff
    except:
            return 0
            #print "No data from serial"
