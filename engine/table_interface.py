# By Chris Parker
 
### IMPORTS ###
import serial
import time

# SENDING #
INIT = 0x00
EXIT = 0xFF
CAL = 0x00

BEGIN_MOVE = 0x00
STOP_MOVE = 0x00

REQ_STATUS = 0x00
REQ_POS = 0x00
REQ_SQR = 0x00
SND_SQR = 0x00

# RECEIVING #

NULL = 0x00
WAITING = 0x00
MOVING = 0x00



class TableInterface:
    
    def __init__(self, port: str) -> None:
        self.mc = serial.Serial(port, baudrate=9600, timeout=0)
        
def main():
    mc = serial.Serial("COM6", baudrate=9600, timeout=0)
    
    data = " "
    
    while data != "":
        data = input(">>")
        mc.write(data)