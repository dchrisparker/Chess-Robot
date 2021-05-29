# By Chris Parker

from typing import *
from abc import ABC, abstractmethod
from chessEnum import Type, Column, Color

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
        def __init__(self, coordinates: Pair, piece: Piece):
            self.coords = coordinates
            self.piece = piece
    class EmptySquare(Square):
        def __init__(self, coordinates: Pair):
            super().__init__(coordinates, None)


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