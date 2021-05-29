# By Chris Parker

from typing import *
from abc import ABC, abstractmethod
from chessEnum import Type, Column, Color
import typing

class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.row = y
        self.col = Column(x)

    def getAlgCoords(self) -> str:
        return f"{self.col.name.lower()}{self.row+1}"

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"
    
    def __repr__(self) -> str:
        return f"{self.x},{self.y}; {self.col.name}{self.row+1}"

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __bool__(self) -> bool:
        return bool(self.x) or bool(self.y)

class Piece(ABC):
    
    def __init__(self, color: Color, type: Type) -> None:
        self.color = color
        self.type = type

    def __str__(self) -> str:
        return f"{self.color.name} {self.type.name}"

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def isValidPath(self, start: Pair, end: Pair):
        pass

    @abstractmethod
    def getPath(self, start: Pair, end: Pair):
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
                path.append(start.row + (i*self.color))

        return path

    def clone(self):
        return Pawn(self.color)

    # def isCaptureValid(self, start: Pair, end: Pair):
    #     if start.row + self.color == end.row:
    #         if start.x + 1 == end.x or start.x - 1 == end.x:
    #             return True

    #     return False

        
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
        
        for i in range(1, (abs(start.x - end.x) or abs(start.y - end.y)) + 1): # Goes from 1 to length of path

            if start.x-end.x: # If x is not constant
                path.append(Pair(start.x + i, start.y)) # Y is constant 
            else:
                path.append(Pair(start.x, start.y + i)) # X is constant

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
        if start.x-end.x > 0:
            xDir = -1
        if start.y-end.y > 0:
            yDir = -1

        for i in range(1, pathLen+1):
            path.append(Pair(i*xDir, i*yDir))

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
        if start.x-end.x > 0:
            xDir = -1
        elif start.x-end.x < 0:
            xDir = 1

        if start.y-end.y > 0:
            yDir = -1
        elif start.y-end.y < 0:
            yDir = 1

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

    # BOARD START POSITIONS
    # BACK_ROW_WHITE = (Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE),
    # Queen(Color.WHITE), King(Color.WHITE), Bishop(Color.WHITE) Pawn(Color.WHITE)) 
    # wp = Pawn(Color.WHITE) # White pawn
    
    wr, wn, wb = Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE)
    wq, wk, wp = Queen(Color.WHITE), King(Color.WHITE), Pawn(Color.WHITE)

    # BACK_ROW_BLACK = (Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK), 
    # Queen(Color.BLACK), King(Color.BLACK), Pawn(Color.BLACK))
    # bp = Pawn(Color.WHITE) # Black pawn

    br, bn, bb = Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK)
    bq, bk, bp = Queen(Color.BLACK), King(Color.BLACK), Pawn(Color.BLACK)

    # Origin (A1) is at 0,0 (top, left)
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


    
    def __init__(self):
        self.board = self.DEFAULT_BOARD
        self.resetBoard()

    def resetBoard(self):
        pass
        # Filling in white side
        # for i in range(len(self.board[0])):
        #     self.board[0][i] = self.Square(Pair(i, 0), self.BACK_ROW_WHITE[i])
        
        # for i in range(len(self.board[1])):
        #     self.board[1][i] = self.Square(Pair(i, 1), self.wp)
        
        # # Filling in black side
        # for i in range(len(self.board[7])):
        #     self.board[7][i] = self.Square(Pair(i, 7), self.BACK_ROW_BLACK[i])

        # for i in range(len(self.board[1])):
        #     self.board[1][i] = self.Square(Pair(i, 6), self.bp)

        # # Empty squares
        # for row in range(2, 6):
        #     for col in range(len(self.board[2])):
        #         self.board[row][col] = self.Square(Pair(col, row), None)

    def positionToFEN(self) -> str:
        rtn = ""
        

    def __str__(self) -> str:
        rtn = ""

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                rtn += f"{self.board[row][col].piece}"
            rtn += "|"
    
    



        



class Chess:
    pass


p = Pawn(Color.BLACK)
r = Rook(Color.WHITE)
n = Knight(Color.BLACK)
b = Bishop(Color.WHITE)
q = Queen(Color.BLACK)
k = King(Color.BLACK)

def main():
    p = Pawn(Color.BLACK)
    r = Rook(Color.WHITE)
    n = Knight(Color.BLACK)
    b = Bishop(Color.WHITE)
    q = Queen(Color.BLACK)
    k = King(Color.BLACK)

    print(p.color*1)

if __name__ == "__main__":
    main()