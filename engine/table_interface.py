# By Chris Parker
 
### IMPORTS ###
import logging
import serial
import time

## CONSTANTS ##
# Logging
LOG_PATH = "int.log"

# SENDING #
INIT = 0x01 # 1
EXIT = 0xFF # 255
CAL = 0xE0 # 232

# BEGIN_MOVE = 0x00
# STOP_MOVE = 0x00
REQ_STATUS = 0x93 # 147
REQ_POS = 0x20 # 32
REQ_SQR = 0x89 # 137
SND_SQR = 0xA9 # 169
AXIS_MOVE = 0xAD # 170
HLF_MOVE = 0xBD
HOME_MOVE = 0xDB

# RECEIVING #
NULL = 0x00 # 0
WAITING = 0x76 # 118
MOVING = 0x0A # 10
MESSAGE = 0x22 # 34

logging.basicConfig(filename=LOG_PATH, filemode="w", encoding="utf-8", level=logging.DEBUG)

class TableInterface:
    def __init__(self, port: str, baudrate: int=115200) -> None:
        self.mc = serial.Serial(port, baudrate=baudrate, timeout=0)    
    
    def start(self) -> None:
        logging.info("INIT")
        self.write_code(INIT)
    
    def exit(self) -> None:
        logging.info("EXIT")
        self.write_code(EXIT)
        
    def calibrate(self) -> bool:
        logging.info("CAL")
        self.mc.read_all()
        self.mc.flushOutput()
        self.write_code(CAL)
        self.wait_for_data()
        
        msg = self.read_int()
        
        if msg == MOVING:
            return True
        elif msg == MESSAGE:
            time.sleep(0.01)
            logging.warning(self.mc.read_until(b'\n'))
            return False
        else:
            logging.error("Invalid return after CAL")
            return False
        
    def can_move(self) -> bool: 
        logging.info("REQ_STATUS")
        self.mc.read_all()
        self.mc.flushOutput()
        
        self.write_code(REQ_STATUS)
        self.wait_for_data()
        if self.read_int() == WAITING:
            return True
        else:
            return False
        
    def get_position(self) -> None | tuple[int, int]:
        logging.info("REQ_POS")
        self.mc.read_all()
        self.mc.flushOutput()
        
        self.write_code(REQ_POS)
        self.wait_for_data()
        msg = self.read_string()
        
        if msg:
            msg = msg.split(',')
            x = int(msg[0])
            y = int(msg[1])
            return x, y
        else:
            logging.error("Invalid return after REQ_POS")
            return None
        
    def get_square(self) -> None | tuple[int, int]:
        logging.info("REQ_SQR")
        self.mc.read_all()
        self.mc.flushOutput()
        
        self.write_code(REQ_SQR)
        self.wait_for_data()
        msg = self.read_string()
        
        if msg:
            msg = msg.split(',')
            x = int(msg[0])
            y = int(msg[1])
            return x, y
        else:
            logging.error("Invalid return after REQ_SQR")
            return None
    
    def move(self, sqr: tuple[int, int]) -> bool:
        logging.info("AXIS_MOVE %s", sqr)
        self.mc.read_all()
        self.mc.flushOutput()
        
        self.write_code(AXIS_MOVE)
        self.mc.write(("{},{}\n".format(sqr[0], sqr[1])).encode("utf-8", "ignore"))
        
        self.wait_for_data()
        msg = self.read_string()
        
        if msg == MOVING:
            return True
        else:
            logging.error("Invalid return after AXIS_MOVE")
            return False
        
    def move_piece(self, sqr1: tuple[int, int], sqr2: tuple[int, int]) -> bool:
        logging.info("SND_SQR %s; %s", sqr1, sqr2)
        self.mc.read_all()
        self.mc.flushOutput()
        
        self.write_code(SND_SQR)
        self.mc.write(("{},{};{},{}\n".format(sqr1[0], sqr1[1], sqr2[0], sqr2[1])).encode("utf-8", "ignore"))
        
        self.wait_for_data()
        msg = self.read_string()
        if msg == MOVING:
            return True
        else:
            logging.error("Invalid return after SND_SQR")
            return False
        
    def write_code(self, num: int) -> int:
        return self.mc.write((num).to_bytes(1, 'big'))
        
    def wait_for_data(self) -> None:
        while self.mc.in_waiting <= 0:
            pass
        
    def read_int(self) -> int:
        return ord(self.mc.read())
        
    def read_string(self, encoding="utf-8") -> str:
        return self.mc.readline().decode(encoding, "strict")
        
    def close(self) -> None:
        self.exit()
        time.sleep(0.001)
        self.mc.close()
        
def main():
    table = TableInterface("COM7")
    
    time.sleep(5)
    
    table.start()
    
    start = False
    while not start:
        table.mc.flushOutput()
        table.mc.read_all()
        table.wait_for_data()
        
        rd = table.read_int()
        if rd == WAITING:
            start = True
        elif rd == MESSAGE:
            print(table.read_string())
        
    time.sleep(1);    
    
    print("Can move:", table.can_move())
    print("Position:", table.get_position())
    print("Square:", table.get_square())
    
    time.sleep(5)
    
    print("Moved:", table.move_pieces((1,1), (5,2)))
    print("Moved:", table.move_pieces((3,4), (1,3)))
        
if __name__ == "__main__":
    main()