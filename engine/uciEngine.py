# By Chris Parker

import os
import subprocess
import pathlib
from subprocess import Popen, PIPE, STDOUT
from typing import Any, List

class UCIEngine:
    def __init__(self, enginePath: str, hash=32, threads=4):
        self.path = enginePath
        self.inLog = []
        self.outLog = []

        self._start(hash, threads)
        
    def _start(self, hash: int, threads: int):
        self.eng = Popen(self.path, stdout=PIPE, stdin=PIPE, text=True)
        self.sendCommand("uci")
        self.sendCommand("setoption name Hash value {}".format(hash))
        self.sendCommand("setoption name Threads value {}".format(threads))
        self.sendCommand("isready")
        
        self.printStatus()

        print()

        self.dumpInLog()
        self.dumpOutLog()

        # stdout = []

        # for item in out:
        #     stdout.append(item[0])

        # for item in stdout:
        #     for line in item.split("\n"):
        #         print(line)

    def dumpInLog(self) -> None:
        print(self.inLog)

    def dumpOutLog(self) -> None:
        print(self.outLog)

    def newGame(self) -> None:
        pass

    def printStatus(self) -> List[str]:
        lines = self._getLines()
        for line in lines:
            print(line)

    def _getLines(self) -> List[str]:
        rtn = []

        r = None

        r = self._readLine()

        while r != "":
            rtn.append(r)
            r = self._readLine()

        return rtn
        
    def sendCommand(self, command: str) -> None:
        if not self.eng.stdin:
            raise BrokenPipeError
        self.eng.stdin.write(f"{command}\n")
        self._flushIn()
        self.inLog.append(command)

    def _flushIn(self):
        self.eng.stdin.flush()

    def _flushOut(self):
        self.eng.stdout.flush()

    def _readLine(self):
        if not self.eng.stdout:
            raise BrokenPipeError

        x = self.eng.stdout.readline().strip()
        self.outLog.append(x)
        return x

    def close(self) -> None:
        self.__del__()

    def __del__(self) -> None:
        self.sendCommand("quit")
        self.eng.kill()


def main():
    """UCIEngine tester"""
    eng = UCIEngine("stockfish_13.exe")
    eng.close()


if __name__ == "__main__":
    main()