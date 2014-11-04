#! /usr/bin/python

import serial

# Serial Settings
Baudrate = 9600
SerialPort = '/dev/ttyUSB0'

def connect_serial(data=None):
    try:
        ser = serial.Serial(SerialPort, Baudrate, timeout=.1, xonxoff=False, rtscts=False, dsrdtr=False)
        print "Serial Port Open."
        print "sending serial data"
        ser.write(data)
        
    except:
        print "Cannot open serial port."
        sys.exit(1) 

    ser.flushInput()  # Get the garbage out of the input buffer
    ser.flushOutput() # Get the garbage out of the output buffer
