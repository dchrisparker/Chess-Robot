# By Chris Parker

from time import sleep
from subprocess import Popen, PIPE, STDOUT
from typing import Any, List
from pythonutil.nbreader import NonBlockingStreamReader as NBSR

class UCIEngine:
    def __init__(self, enginePath: str, threads=4, hash=32, limitStrength=False, elo=2850, slowMover=100):
        self.path = enginePath
        self.inLog = []
        self.outLog = []
        self.reader = None

        self._start(threads, hash, limitStrength, elo, slowMover)
        self.newGame()

    def _start(self, threads: int, hash: int, limitStrength: bool, elo: int, slowMover: int):
        self.eng = Popen(self.path, stdout=PIPE, stdin=PIPE, text=True) # Starting stockfish engine
        sleep(0.01)
        self.reader = NBSR(self.eng.stdout)
        sleep(0.01)
        self.sendCommand("uci") # Telling engine to use uci

        # Setting options
        self.setOption("Threads", threads)
        self.setOption("Hash", hash)
        self.setOption("UCI_LimitStrength", limitStrength)
        self.setOption("UCI_Elo", elo)
        self.setOption("Slow Mover", slowMover)
        self.sendCommand("isready")

        sleep(0.1)

        self._printLines()
        self._flushOut()  # Clears stdout

    def dumpInLog(self) -> None:
        print(self.inLog)

    def dumpOutLog(self) -> None:
        print(self.outLog)

    def newGame(self) -> None:
        self.sendCommand("ucinewgame")

    def sendPos(self, position: str) -> None:
        self.sendCommand(f"position fen {position}")

    def sendPosMoves(self, position: str, moves: str) -> None:
        self.sendCommand(f"position fen {position} moves {moves}")

    def sendCommand(self, command: str, reads=0):
        if not self.eng.stdin:
            raise BrokenPipeError
        self.eng.stdin.write(f"{command}\n")
        self._flushIn()
        self.inLog.append(command)

    def setOption(self, name: str, value: Any):
        self.sendCommand(f"setoption name {name} value {value}")

    def _flushIn(self):
        self.eng.stdin.flush()

    def _flushOut(self):
        self.eng.stdout.flush()

    def _readLine(self):
        if not self.eng.stdout:
            raise BrokenPipeError

        x = self.reader.readline()
        if x: 
            self.outLog.append(x)
        return x

    def _readLines(self, buffer=-1) -> List[str]:
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

    def _printLines(self, buffer=-1) -> None:
        lines = self._readLines(buffer)

        for line in lines:
            print(line, end="")

    def close(self) -> None:
        self.__del__()

    def __del__(self) -> None:
        self.sendCommand("quit")
        self.eng.kill()

class Stockfish(UCIEngine):
    def displayBoard(self):
        self.sendCommand("d")
        sleep(0.1)
        self._printLines()

def main():
    """UCIEngine & Stockfish tester"""
    eng = Stockfish("stockfish_13.exe")

    eng.displayBoard()

    eng.close()


if __name__ == "__main__":
    main()
