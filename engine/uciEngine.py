# By Chris Parker

# Exceptions
from exceptions import InvalidEngineError

# Subprocess
from subprocess import PIPE, STDOUT, Popen
from time import sleep

# Type hinting
from typing import Any, Iterable, List, Optional, Tuple, Union
from os import PathLike

# Reader
from pythonutil.nbreader import NonBlockingStreamReader as NBSR


class UCIEngine:
    """Provides functions for interacting with a universal chess interface (UCI) compatible chess engine.

    Raises
    ------
    InvalidEngineError
        If the program given is not UCI compatible
    BrokenPipeError
        If there are problems with the programs stdin or stdout
    """
    def __init__(self, enginePath: Union[str, PathLike], *boolOpts: str, **options: Union[str, int]):
        """Construct new `UCIEngine`.

        Parameters
        ----------
        enginePath : str, PathLike
            Path of the chess engine
        *boolOpts : str
            Boolean (on or off) options. 
            Ex. `UCI_LimitStrength`
        **options : str, int
            Options with a name and value.
            Ex. `UCI_Elo value 2200`
            NOTE: Many engines have limits for these values. See documentation for these engines.

        Raises
        ------
        InvalidEngineError
            If the program given is not UCI compatible
        """

        self.path = enginePath
        self.inLog = []
        self.outLog = []
        self.debugOn = False

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
        # NOTE: Required to start searches
        self.isReady()

        sleep(0.1)

        # self._printLines()
        self._flushOut()  # Clears stdout


    # Printing info

    def dumpInLog(self) -> None:
        """Print log of commands sent."""
        print(self.inLog)

    def dumpOutLog(self) -> None:
        """Print log of data received."""
        print(self.outLog)

    def printLines(self, buffer: int=-1) -> None:
        """Print all lines in stdout.

        Parameters
        ----------
        buffer : int, optional
            The maximum amount of lines to read. If <= 0, will read until end of avaliable data, by default -1
        """
        lines = self._readLines(buffer)

        for line in lines:
            print(line, end="")


    # Sending preset commands 

    def newGame(self) -> None:
        """Starts new game by sending `ucinewgame` command."""
        self.sendCommand("ucinewgame")

    def go(self, *args: str, **kwargs: int) -> None:
        """Send `go` command with provided arguments.

        Parameters
        ----------
        *args : str
            Valueless arguments.
            Ex. `ponder`
        *kwargs : int
            Valued arguments.
            Ex. `depth 10`
        """
        command = "go "
        for arg in args:
            command += f"{str(arg)} "
        for item in kwargs:
            command += f"{item} {str(kwargs[item])} "

        self.sendCommand(command)

    def stop(self) -> None:
        """Stop search by sending `stop` command."""
        self.sendCommand("stop")

    def isReady(self) -> bool:
        """Send `isready` command and return a boolean

        Returns
        -------
        bool
            True if 
        """
        self._readLines()
        self.sendCommand("isready")
        sleep(0.125)
        if self._readLine() == "readyok":
            return True
        else: 
            return False 

    def debug(self) -> bool:
        """Toggle debug mode by sending `debug on` or `debug off`.

        Returns
        -------
        bool
            True if debug is now on or False if debug is off
        """
        command = "debug "
        if self.debugOn:
            command += "off"
            self.debugOn = False
        else:
            command += "on"
            self.debugOn = True

        self.sendCommand(command)
        return self.debugOn


    # Sending commands

    def sendCommand(self, command: str, reads: int=0) -> Union[None, List[str]]:
        """Send a command to the engine.

        Parameters
        ----------
        command : str
            Command to send.
        reads : int, optional
            Number of times to read the output, by default 0

        Returns
        -------
        None
            If `reads` == 0
        List[str]
            If `reads` > 0
        
        Raises
        ------
        BrokenPipeError
            If there are problems writing to stdin
        """
        if not self.eng.stdin:
            raise BrokenPipeError
        self.eng.stdin.write(f"{command}\n")
        self._flushIn()
        self.inLog.append(command)

        if reads > 0:
            return self._readLines(reads)

        

    def setOption(self, name: str, value: Any) -> None:
        """Set option by sending `setoption` command.

        Parameters
        ----------
        name : str
            Name of the option.
            Ex. `Threads`
        value : Any
            Value of the option.
            Ex. `4`
        """
        self.sendCommand(f"setoption name {name} value {value}")
    

    # Sending positions/moves

    def sendMoveSeq(self, moves: Iterable) -> None:
        """Send a sequence of moves from the starting position.

        Parameters
        ----------
        moves : Iterable
            A string, list, tuple, etc. containing every move. 
            NOTE: If using a string, separate the moves by spaces.
        """
        movesStr: str
        if type(moves) != str:
            movesStr = self._moveSeqToString(moves)
        else:
            movesStr = moves

        self.sendCommand(f"position startpos moves {movesStr}")

    def sendPosMoves(self, position: str, move: str) -> None:
        """Send a FEN position and move to engine.

        Parameters
        ----------
        position : str
            A FEN string describing the position.
        move : str
            A *single* move.
        """
        self.sendCommand(f"position fen {position} moves {move}")


    # Reading from engine stdout

    def _readLine(self) -> str:
        """Read one line from the reader.

        Returns
        -------
        str
            The line read

        Raises
        ------
        BrokenPipeError
            If there are problems reading from stdout
        """
        if not self.eng.stdout:
            raise BrokenPipeError

        x = self.reader.readline()
        if x: 
            self.outLog.append(x)
        return x

    def _readLines(self, buffer: int=-1) -> List[str]:
        """Read until end of stream or end of buffer.

        Parameters
        ----------
        buffer : int, optional
            If > 0, number of lines to read, by default -1

        Returns
        -------
        List[str]
            List of every line read
        """
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
        """Flush engine stdin."""
        self.eng.stdin.flush()

    def _flushOut(self) -> None:
        """Flush engine stdout."""
        self.eng.stdout.flush()


    # Utility

    @staticmethod
    def _moveSeqToString(seq: Iterable[str]) -> str:
        """Convert a sequence of moves to a string the engine can use.

        Parameters
        ----------
        seq : Iterable[str]
            Sequence to convert.

        Returns
        -------
        str
            String of moves.
        """
        rtn = ""
        for item in seq:
            rtn += str(item) + " "

    def _writeLogsToFile(self, logPath: Union[str, PathLike]) -> None:
        """Write input and output logs to a file.

        Parameters
        ----------
        logPath : str, PathLike
            The path for the log file. Will overwrite if file already exists.
        """
        f = open(logPath, "w")

        f.write("UCIEngine Log File\n\n")

        f.write("IN:\n")
        for line in self.inLog:
            f.write(f"{line}\n")

        f.write("\n==================================================\n")

        f.write("\nOUT:\n")
        f.writelines(self.outLog)

        f.write("\n\nEND")
        f.close()


    # Stoping engine

    def close(self, logPath: Union[str, PathLike]="") -> None:
        """Close the engine and write logs to file if path is provided.

        Parameters
        ----------
        logPath : str, PathLike, optional
            Used to write logs to file for debugging. Leave blank to non write to file, by default ""
        """
        
        if logPath:
            self._writeLogsToFile(logPath)

        self.__del__()

    def __del__(self) -> None:
        """Stop the engine fully and kill process"""
        self.sendCommand("quit")
        self.eng.kill()



class Stockfish(UCIEngine):
    """Represents the Stockfish chess engine and provides methods to interact with it.

    Extends
    -------
    UCIEngine
        The UCIEngine class
    """
    def displayBoard(self) -> None:
        """Display the board using the `d` Stockfish command."""
        self.sendCommand("d")
        sleep(0.1)
        self.printLines()



def main():
    """UCIEngine & Stockfish tester"""
    eng = Stockfish("stockfish_13.exe", "UCI_LimitStrength", UCI_Elo = 1880, Threads = 4, Hash = 1024)
    eng.newGame()

    eng.displayBoard()

    eng.dumpInLog()

    eng.close(saveLogs=True, logPath="log.txt")



if __name__ == "__main__":
    main()
