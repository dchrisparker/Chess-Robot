# By Chris Parker

import os
import subprocess
import pathlib
from subprocess import Popen, PIPE, STDOUT
from typing import Any, List


class Stockfish:
    def __init__(self, enginePath: str, threads=4, hash=32, limitStrength=False, elo=2850, slowMover=100):
        self.path = enginePath
        self.pos = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.inLog = []
        self.outLog = []

        self._start(threads, hash, limitStrength, elo, slowMover)
        self.newGame() # 23

    def _start(self, threads: int, hash: int, limitStrength: bool, elo: int, slowMover: int):
        self.eng = Popen(self.path, stdout=PIPE, stdin=PIPE, text=True)
        self.sendCommand("uci")
        self.setOption("Threads", threads)
        self.setOption("Hash", hash)
        self.setOption("UCI_LimitStrength", limitStrength)
        self.setOption("UCI_Elo", elo)
        self.setOption("Slow Mover", slowMover)
        self.sendCommand("isready")

        # Predetermined value, program will hang if increased
        self._printLines(29)
        self._flushOut  # Clears stdout

    def dumpInLog(self) -> None:
        print(self.inLog)

    def dumpOutLog(self) -> None:
        print(self.outLog)

    def newGame(self) -> None:
        self.sendCommand("ucinewgame")

    def sendMove(self, move: str) -> None:
        self.sendCommand("position ")

    def displayBoard(self):
        self._flushOut()
        self.sendCommand("d")
        self._printLines(23)

    def sendCommand(self, command: str) -> None:
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

        x = self.eng.stdout.readline()
        self.outLog.append(x)
        return x

    def _getLines(self, buffer: int) -> List[str]:
        rtn = []

        for i in range(buffer):
            rtn.append(self._readLine())

        return rtn

    def _printLines(self, buffer: int) -> None:
        lines = self._getLines(buffer)

        for line in lines:
            print(line, end="")

    def close(self) -> None:
        self.__del__()

    def __del__(self) -> None:
        self.sendCommand("quit")
        self.eng.kill()


def main():
    """UCIEngine tester"""
    eng = Stockfish("stockfish_13.exe")

    eng.close()


if __name__ == "__main__":
    main()
