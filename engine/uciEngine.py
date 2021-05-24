# By Chris Parker

import os
import subprocess
import time
from subprocess import Popen, PIPE, STDOUT

class UCIEngine:
    def __init__(self, enginePath, hash=32, threads=4):
        self.path = enginePath

        self.start(hash, threads)
        
    def start(self, hash, threads):
        self.eng = Popen([], stdout=PIPE, stdin=PIPE, stderr=STDOUT, text=True, executable=self.path)
        self.eng.stdin.write("uci\n")
        self.eng.stdin.write("setoption name Hash value {}".format(hash) + "\n")
        self.eng.stdin.write("setoption name Threads value {}".format(threads) + "\n")
        self.eng.stdin.write("isready\n")
        
        print(self.getLines())

        # stdout = []

        # for item in out:
        #     stdout.append(item[0])

        # for item in stdout:
        #     for line in item.split("\n"):
        #         print(line)


    def newGame(self):
        pass

    # def run(self, command):
    #     rtn = subprocess.check_output(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
    #     print(rtn)
    #     return rtn

    def printStatus(self):
        lines = self.getLines()
        for line in lines:
            print(line)

    def getLines(self):
        r = self.eng.stdout.readline()

        rtn = [r]

        while r != "":
            rtn.append(r)
            r = self.eng.stdout.readline()

        return r
        


    def close(self):
        self.eng.close()


def main():
    """UCIEngine tester"""
    eng = UCIEngine("stockfish_13.exe")


if __name__ == "__main__":
    main()