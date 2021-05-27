# By Chris Parker

from os import PathLike, stat
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from typing import Any, List, Iterable, Tuple, Union, Optional
from pythonutil.nbreader import NonBlockingStreamReader as NBSR
from exceptions import InvalidEngineError

class UCIEngine:
    # TODO: Add propper comments
    def __init__(self, enginePath: Union[str, PathLike], *boolOpts: str, **options: Union[str, int]):

        self.path = enginePath
        self.inLog = []
        self.outLog = []

        # Starting engine
        self.eng = Popen(self.path, stdout=PIPE, stdin=PIPE, text=True)
        sleep(0.01)

        # Starting reader
        self.reader = NBSR(self.eng.stdout)
        sleep(0.01)

        self.sendCommand("uci") # Telling engine to use uci protocol
        sleep(0.5)

        if self._readLines()[-1] != "uciok\n":
            raise InvalidEngineError(self.path)
            

        # Setting options
        for setting in boolOpts:
            self.sendCommand(f"setoption name {str(setting)}")

        for setting in options:
            self.setOption(setting, options[setting])

        # Checking if engine is ready
        # Required to start searches
        self.isReady()

        sleep(0.1)

        # self._printLines()
        self._flushOut()  # Clears stdout


    # Printing info

    def dumpInLog(self) -> None:
        print(self.inLog)

    def dumpOutLog(self) -> None:
        print(self.outLog)

    def printLines(self, buffer: int=-1) -> None:
        lines = self._readLines(buffer)

        for line in lines:
            print(line, end="")


    # Sending preset commands 

    def newGame(self) -> None:
        self.sendCommand("ucinewgame")

    def go(self, *args: str, **kwargs: str) -> None:

        command = "go "
        for arg in args:
            command += f"{str(arg)} "
        for item in kwargs:
            command += f"{item} {str(kwargs[item])} "

        self.sendCommand(command)

    def isReady(self) -> bool:
        self._readLines()
        self.sendCommand("isready")
        sleep(0.125)
        if self._readLine() == "isready":
            return True
        else: 
            return False 


    # Sending commands

    def sendCommand(self, command: str, reads: int=0) -> None:
        if not self.eng.stdin:
            raise BrokenPipeError
        self.eng.stdin.write(f"{command}\n")
        self._flushIn()
        self.inLog.append(command)

    def setOption(self, name: str, value: Any) -> None:
        self.sendCommand(f"setoption name {name} value {value}")
    

    # Sending positions/moves

    def sendMoveSeq(self, moves: Iterable) -> None:
        movesStr: str
        if type(moves) != str:
            movesStr = self._moveSeqToString(moves)
        else:
            movesStr = moves

        self.sendCommand(f"position startpos moves {movesStr}")
        
    def sendPos(self, position: str) -> None:
        self.sendCommand(f"position fen {position}")

    def sendPosMoves(self, position: str, moves: str) -> None:
        self.sendCommand(f"position fen {position} moves {moves}")

    # Reading from engine stdout

    def _readLine(self) -> str:
        if not self.eng.stdout:
            raise BrokenPipeError

        x = self.reader.readline()
        if x: 
            self.outLog.append(x)
        return x

    def _readLines(self, buffer: int=-1) -> List[str]:
        rtn = []
        
        if buffer <= 0:
            x = self._readLine()
            while x:
                rtn.append(x)
                x = self._readLine()
        else:
            x = self._readLine()
            i = 0
            while x and i < buffer:
                rtn.append(x)
                x = self._readLine()
                i+=1

        return rtn


    # Flusing stdout and stdin

    def _flushIn(self) -> None:
        self.eng.stdin.flush()

    def _flushOut(self) -> None:
        self.eng.stdout.flush()


    # Utility
    @staticmethod
    def _moveSeqToString(seq: Iterable) -> str:
        rtn = ""
        for item in seq:
            rtn += str(item) + " "


    # Stoping engine

    def close(self) -> None:
        self.__del__()

    def __del__(self) -> None:
        self.sendCommand("quit")
        self.eng.kill()



class Stockfish(UCIEngine):
    def displayBoard(self) -> None:
        self.sendCommand("d")
        sleep(0.1)
        self.printLines()

def main():
    """UCIEngine & Stockfish tester"""
    eng = Stockfish("stockfish_13.exe", "UCI_LimitStrength", UCI_Elo = 1880, Threads = 4, Hash = 1024)
    eng.newGame()

    eng.displayBoard()

    eng.dumpInLog()

    eng.close()



if __name__ == "__main__":
    main()
