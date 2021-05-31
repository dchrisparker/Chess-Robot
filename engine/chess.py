# By Chris Parker

import operator
from abc import ABC, abstractmethod
from exceptions import InvalidFENError
from functools import cache
from typing import *


from chessEnum import Color, Column, Type


class Pair:
    """A class representing a coordinate on a chess board."""
    def __init__(self, y: int, x: int):
        """Construct a new Pair.

        Parameters
        ----------
        y : int
            Y value (row, rank, etc.)
        x : int
            X value (column, file, etc.)
        """
        self.y = y
        self.x = x

        if x in list(Column):
            self.row = y
            self.col = Column(x)

            self.rank = self.row
            self.file = self.col
    
    def getAlgCoords(self) -> str:
        """Return the algebraic version of this coordinate."""
        return f"{self.col.name.lower()}{self.row+1}"

    def isNegative(self) -> bool:
        return True if self.x < 0 or self.y < 0 else False

    def isAbove(self, maxY, maxX) -> bool:
        return True if self.x > maxX or self.y > maxY else False

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.getAlgCoords()
    
    def __repr__(self) -> str:
        return f"{self.y},{self.x}; {self.col.name}{self.row+1}"

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __bool__(self) -> bool:
        return bool(self.x) or bool(self.y) # Only returns false if both are 0 or None

        
        

class Piece(ABC):
    """An abstract class representing a chess piece."""
    def __init__(self, color: Color, type: Type) -> None:
        self.color = color
        self.type = type
        self.hasMoved = False

    def __str__(self) -> str:
        return f"{self.color.name} {self.type.name}"

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def isValidPath(self, start: Pair, end: Pair) -> Union[bool, Literal['c']]:
        pass

    @abstractmethod
    def getPath(self, start: Pair, end: Pair) -> List[Pair]:
        pass

    @abstractmethod
    def clone(self):
        pass
    

class Pawn(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.PAWN)
        self.hasMoved = False

    def isValidPath(self, start: Pair, end: Pair) -> Union[bool, Literal['c']]:
        # Color determines direction
        if start.col == end.col: # Going straight

            if start.row + (2*self.color) == end.row: # Going 2 forward?
                if not self.hasMoved: # First move?
                    return True
                else:
                    return False
            if start.row + self.color == end.row: # Going 1 forward
                return True # Always ok
            else: 
                return False
        elif ((start.col + 1 == end.col) or (start.col - 1 == end.col)) and (start.row + self.color == end.row): # Capture?
            return 'c' # Return c because this move is only valid if it is a capture
        else: # No valid options
            return False

    def getPath(self, start: Pair, end: Pair):
        path: List[Pair] = [] # List of coordinate the piece will move

        if start.col != end.col: # If the pawn is moving diagonally (capture)
            path = [end]
        else: # If the pawn is moving straight 
            for i in range(1, abs(start.row-end.row)+1):
                path.append(Pair(start.row + (i*self.color), start.x))

        return path

    def clone(self):
        return Pawn(self.color)

        
class Rook(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.ROOK)
        self.hasMoved = False

    def isValidPath(self, start: Pair, end: Pair):
        h = start.x == end.x
        v = start.y == end.y

        if h ^ v: # xor, checking if going horizontally and vertically or not moving
            return True
        else: # Must be going both or neither
            return False
    
    def getPath(self, start: Pair, end: Pair):
        path: List[Pair] = []
        pathLen: int
        
        if start.x < end.x:
            xDir = 1
        elif start.x > end.x:
            xDir = -1
        else:
            xDir = 0

        if start.y < end.y:
            yDir = 1
        elif start.y > end.y:
            yDir = -1
        else:
            yDir = 0

        if xDir:
            pathLen = abs(start.x-end.x)
        else:
            pathLen = abs(start.y-end.y)

        for i in range(1, pathLen): # Goes frm 1 to length of path

            if xDir: # If x is not constant
                path.append(Pair(start.y, start.x + i*xDir)) # Y is constant 
            else:
                path.append(Pair(start.y + i*yDir, start.x)) # X is constant
            

        return path
    
    def clone(self):
        return Rook(self.color)
        

class Knight(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.KNIGHT)
    
    def isValidPath(self, start: Pair, end: Pair):
        xDiff = abs(start.x - end.x)
        yDiff = abs(start.y - end.y)

        # Ensures the path is an L shape (2 one way and 1 the other)
        if ((xDiff == 2) ^ (yDiff == 2)) and ((xDiff == 1) ^ (yDiff == 1)): # xDiff xor yDiff == 2 and xDiff xor yDiff == 1
            return True
        else:
            return False

    def getPath(self, start: Pair, end: Pair):
        return [end]

    def clone(self):
        return Knight(self.color)


class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.BISHOP)

    def isValidPath(self, start: Pair, end: Pair):
        return start.x-end.x == start.y - end.y and start != end

    def getPath(self, start: Pair, end: Pair):
        path: List[Pair] = []

        pathLen = abs(start.x-end.x) # Length of the path

        # Finding x and y directions
        xDir = yDir = 1
        if start.x > end.x:
            xDir = -1
        if start.y > end.y:
            yDir = -1

        for i in range(1, pathLen):
            path.append(Pair(start.y + i*yDir, start.x + i*xDir))

        return path

    def clone(self):
        return Bishop(self.color)


class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.QUEEN)

    def isValidPath(self, start: Pair, end: Pair):
        return Bishop(self.color).isValidPath(start, end) or Rook(self.color).isValidPath(start, end)

    def getPath(self, start: Pair, end: Pair):

        xDir = yDir = 0
        if start.x < end.x:
            xDir = 1
        elif start.x > end.x:
            xDir = -1

        if start.y < end.y:
            yDir = 1
        elif start.y > end.y:
            yDir = -1

        if xDir != 0 and yDir != 0:
            return Bishop(self.color).getPath(start, end)
        else:
            return Rook(self.color).getPath(start, end)

    def clone(self):
        return Queen(self.color)


class King(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.KING)
        self.hasMoved = False

    def isValidPath(self, start: Pair, end: Pair):
        return (abs(start.x-end.x) <= 1) and (abs(start.y-end.y) <= 1) and start != end

    def getPath(self, start: Pair, end: Pair):
        return [end]

    def clone(self):
        return King(self.color)


class ChessBoard: 

    class Square:
        def __init__(self, coordinates: Pair, piece: Union[Piece, None]):
            self.coords = coordinates
            self.piece = piece
        
        def __str__(self) -> str:
            return str(self.piece)

        def __repr__(self) -> str:
            return self.__str__() + f"({self.coords.row},{self.coords.col})"

    # GLOBAL CLASS VARIABLES

    # Pieces 
    # White    
    wr, wn, wb = Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE)
    wq, wk, wp = Queen(Color.WHITE), King(Color.WHITE), Pawn(Color.WHITE)

    # Black
    br, bn, bb = Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK)
    bq, bk, bp = Queen(Color.BLACK), King(Color.BLACK), Pawn(Color.BLACK)

    # Origin (A1) is at 0,0 (top-left)
    DEFAULT_BOARD = ( 
        (Square(Pair(0,0),wr), Square(Pair(0,1),wn), Square(Pair(0,2),wb), Square(Pair(0,3),wq), Square(Pair(0,4),wk), Square(Pair(0,5),wb), Square(Pair(0,6),wn), Square(Pair(0,7),wr)),
        (Square(Pair(1,0),wp), Square(Pair(1,1),wp), Square(Pair(1,2),wp), Square(Pair(1,3),wp), Square(Pair(1,4),wp), Square(Pair(1,5),wp), Square(Pair(1,6),wp), Square(Pair(1,7),wp)),
        (Square(Pair(2,0),None), Square(Pair(2,1),None), Square(Pair(2,2),None), Square(Pair(2,3),None), Square(Pair(2,4),None), Square(Pair(2,5),None), Square(Pair(2,6),None), Square(Pair(2,7),None)),
        (Square(Pair(3,0),None), Square(Pair(3,1),None), Square(Pair(3,2),None), Square(Pair(3,3),None), Square(Pair(3,4),None), Square(Pair(3,5),None), Square(Pair(3,6),None), Square(Pair(3,7),None)),
        (Square(Pair(4,0),None), Square(Pair(4,1),None), Square(Pair(4,2),None), Square(Pair(4,3),None), Square(Pair(4,4),None), Square(Pair(4,5),None), Square(Pair(4,6),None), Square(Pair(4,7),None)),
        (Square(Pair(5,0),None), Square(Pair(5,1),None), Square(Pair(5,2),None), Square(Pair(5,3),None), Square(Pair(5,4),None), Square(Pair(5,5),None), Square(Pair(5,6),None), Square(Pair(5,7),None)),
        (Square(Pair(6,0),bp), Square(Pair(6,1),bp), Square(Pair(6,2),bp), Square(Pair(6,3),bp), Square(Pair(6,4),bp), Square(Pair(6,5),bp), Square(Pair(6,6),bp), Square(Pair(6,7),bp)),
        (Square(Pair(7,0),br), Square(Pair(7,1),bn), Square(Pair(7,2),bb), Square(Pair(7,3),bq), Square(Pair(7,4),bk), Square(Pair(7,5),bb), Square(Pair(7,6),bn), Square(Pair(7,7),br)),
    )
    
    # CONSTRUCTOR
    def __init__(self):
        self.attackedSquaresW: List[Pair] = []
        self.attackedSquaresB: List[Pair] = []
        self.resetBoard()
        self.updateAttackedSquares()

    # MOVEMENT METHODS
    def canMove(self, frm: Pair, to: Pair, *pseudoCap: Pair) -> Tuple[bool, Union[Literal['c'], None]]:
        """Check if a piece can move using its own methods and checking the path it would take.

        Parameters
        ----------
        frm : Pair
            Starting square.
        to : Pair
            Ending square.
        *pseudoCap : Pair
            Squares that can be "captured" but are empty (e.g., en passant square),

        Returns
        -------
        Tuple[bool, Literal['c'] | None]
            Return True if the piece can move or False if it cannot. Returns 'c' if the move would
            result in a capture.
        """
        sSquare = self.getSquare(frm)
        fSquare = self.getSquare(to)

        valid = sSquare.piece.isValidPath(frm, to)

        if (sSquare.piece == None) or (not valid) or (valid == 'c' and fSquare.piece == None):
            # print(sSquare.piece, valid, fSquare.piece)
            return False, None

        if fSquare.piece != None and sSquare.piece.color == fSquare.piece.color:
            # print(2)
            return False, None

        path = sSquare.piece.getPath(frm, to)

        for i in range(len(path)):
            if i < len(path)-1:
                if self.getSquare(path[i]).piece != None:
                    return False, None
            elif valid == 'c':
                if fSquare.coords in pseudoCap:
                    return True, 'c'
                elif fSquare.piece == None:
                    return False, None

        return True, ('c' if fSquare.piece != None else None)

    def move(self, frm: Pair, to: Pair) -> Union[Piece, None]:
        """Move a piece from start square to end square.

        Parameters
        ----------
        frm : Pair
            Starting square.
        to : Pair
            Ending Square

        Returns
        -------
        Piece | None
            Return the piece captured or None if no piece was captured.
        """
        cSquare = self.getSquare(frm)
        fSquare = self.getSquare(to)

        cap = fSquare.piece
        fSquare.piece = cSquare.piece
        fSquare.piece.hasMoved = True
        cSquare.piece = None

        return cap

    # MODIFIER METHODS
    def setSquare(self, sqr: Pair, piece: Piece) -> None:
        self.getSquare(sqr).piece = piece

    def resetBoard(self) -> None:
        self.board = list(self.DEFAULT_BOARD) 

    def updateAttackedSquares(self):
        """Update attackedSquaresW and attackedSquaresB to accurately show the squares under attack."""
        def _cullAll():
            """Format data after receiving coordinates from functions."""
            def _cull(list: List[Pair]):
                """Format data for one list."""
                i = 0
                while i < len(list):
                    pair = list[i]
                    if pair.isNegative() or pair.isAbove(len(self.board)-1, len(self.board[0])-1):
                        del(list[i])
                    else:
                        i += 1

                for i in range(len(list)):
                    list[i] = [list[i], 1]

                i = 0
                while i < len(list):
                    if i-1 >= 0 and list[i-1][0] == list[i][0]:
                        list[i][1] += list[i-1][1]
                        del(list[i-1])
                    else:
                        i += 1

            _cull(self.attackedSquaresW)
            _cull(self.attackedSquaresB)

        def _byPawn(square: ChessBoard.Square) -> List[Pair]:
            return [
                Pair(square.coords.y + square.piece.color, square.coords.x-1),
                Pair(square.coords.y + square.piece.color, square.coords.x+1)
            ] # Pawns can only attack 2 squares
        
        def _byKing(square: ChessBoard.Square) -> List[Pair]:
            return [
                Pair(square.coords.y-1, square.coords.x-1), Pair(square.coords.y+1, square.coords.x+1), 
                Pair(square.coords.y-1, square.coords.x+1), Pair(square.coords.y+1, square.coords.x-1), 
                Pair(square.coords.y, square.coords.x+1),   Pair(square.coords.y, square.coords.x-1),
                Pair(square.coords.y+1, square.coords.x),   Pair(square.coords.y-1, square.coords.x)
            ] # Returns all squares around king. Invalid squares are removed later

        def _byBishop(square: ChessBoard.Square) -> List[Pair]:
            rtn = []
            
            # Every combination of directions
            for yDir in (-1, 1):
                for xDir in (-1, 1):
                    y = square.coords.y + yDir
                    x = square.coords.x + xDir

                    while y < len(self.board) and y >= 0 and x < len(self.board[y]) and x >= 0:
                        rtn.append(Pair(y, x))

                        if self.board[y][x].piece != None:
                            break # Stops when there is a peace in the path

                        y += yDir
                        x += xDir

            return rtn

        def _byRook(square: ChessBoard.Square) -> List[Pair]:

            def _findStop(list: List[Pair]) -> List[Pair]:
                r = []
                for pair in list:
                    r.append(pair)
                    if self.board[pair.y][pair.x].piece != None:
                        break # Stop when another piece is in the path

                return r

            y = square.coords.y
            x = square.coords.x

            # Maxima
            maxY = len(self.board)-1
            maxX = len(self.board[0])-1

            # Paths to edges of board
            maxYPath = square.piece.getPath(square.coords, Pair(maxY, x))
            minYPath = square.piece.getPath(square.coords, Pair(0, x))

            maxXPath = square.piece.getPath(square.coords, Pair(y, maxX))
            minXPath = square.piece.getPath(square.coords, Pair(y, 0))

            # Return all 4 paths rook covers
            return _findStop(maxYPath) + _findStop(minYPath) + _findStop(maxXPath) + _findStop(minXPath)

        def _byQueen(square: ChessBoard.Square) -> List[Pair]:
            # Queens have the movement of a bishop and rook combined 
            return _byBishop(square) + _byRook(square) 

        def _byKnight(square: ChessBoard.Square) -> List[Pair]:
            y = square.coords.y
            x = square.coords.x
            return [Pair(y+2, x+1), Pair(y+2, x-1), Pair(y-2, x+1), Pair(y-2, x-1),
                    Pair(y+1, x+2), Pair(y+1, x-2), Pair(y-1, x+2), Pair(y-1, x-2)
            ] # Returns all squares around knight. Invalid squares are removed later
        
        # Clears old lists
        self.attackedSquaresB = []
        self.attackedSquaresW = []

        # Goes through every rank and file
        for rank in self.board: 
            for square in rank:
                # Ensuring there is a piece on the square
                if square.piece != None:
                    if square.piece.color == Color.WHITE:
                        # WARNING: This can be dangerous! It should be fine in this case but this may need to be 
                        # reevaluated in a later program
                        self.attackedSquaresW += eval("_by"+(square.piece.type.name.capitalize())+"(square)")
                    else:
                        self.attackedSquaresB += eval("_by"+(square.piece.type.name.capitalize())+"(square)")
        
        # Sort the lists with the y's and then the x's
        self.attackedSquaresW.sort(key = lambda l : (l.y, l.x))
        self.attackedSquaresB.sort(key = lambda l : (l.y, l.x))

        _cullAll() # Format the data    
    
    # ACCESSOR METHODS
    def getSquare(self, squarePos: Pair) -> Square:
        return self.board[squarePos.y][squarePos.x]

    def getKingPosition(self, color: Color) -> Pair:
        for rank in range(len(self.board)):
            for file in range(len(self.board[rank])):
                square = self.getSquare(Pair(rank, file))
                if square.piece.type == Type.KING and square.piece.color == color:
                    return Pair(rank, file)
        
    # FEN METHODS
    def FENPiecePlacement(self) -> str:
        """Return a FEN string based off the current board position

        Returns
        -------
        str
            Piece placement FEN string 
            NOTE: This is not a complete FEN string, just the piece placement

        Reference
        ---------
        https://www.chessprogramming.org/Forsyth-Edwards_Notation
        """
        rtn = ""
        digit = 0

        # Piece placement
        # Rank (frm 8 to 1)
        for rank in range(len(self.board)-1, -1, -1):
            # File (frm A to H)
            for square in self.board[rank]:
                piece = square.piece
                
                if piece != None: # If the square isn't empty
                    if digit: # If there is a digit
                        rtn += str(digit)
                        digit = 0

                    l = piece.type.value # Letter

                    if piece.color == Color.BLACK:
                        l = l.lower() # Black pieces are represented with lowercase

                    rtn += l
                else: # Must be an empty square
                    digit += 1

            if digit:
                rtn += str(digit)
                digit = 0
            if rank != 0:
                rtn += '/'

        return rtn
        
    def FENSetPosition(self, FEN: str) -> None:
        """Set board position from FEN string.

        Parameters
        ----------
        FEN : str
            Full or partial FEN string.
            NOTE: Only the position portion of the string is required. 
            (e.g., "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

        Raises
        ------
        InvalidFENError
            If the FEN string is not correctly formatted.
        """
        FEN = FEN.strip()
        lastRank = len(self.board)-1
        rank = lastRank
        file = 0
        

        for l in FEN:

            if l.isalpha():
                piece: Piece = None
                try: # Could be unsafe. Use carefully
                    if l.islower():
                        piece = eval("self.b"+l)
                    else:
                        piece = eval("self.w"+l.lower())
                except AttributeError:
                    raise InvalidFENError(FEN)

                self.setSquare(Pair(rank, file), piece)
                file += 1
            elif l.isnumeric():
                for f in range(file, file+int(l)):
                    self.setSquare(Pair(rank, f), None)
                file += int(l)


            if l == '/':
                rank -= 1
                if rank < 0:
                    raise InvalidFENError(FEN)
                file = 0

            if l == ' ': # Must be the end of position section
                break    # Other sections can be disguarded

        self.updateAttackedSquares()
            

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.FENPiecePlacement()

    def __repr__(self) -> str:
        rtn = ""
        for row in self.board:
            rtn += repr(row) + '\n'

        return rtn


class Chess:
    pass

def main():
    c = ChessBoard()


if __name__ == "__main__":
    main()
