# By Chris Parker

from enum import Enum, auto, IntEnum
from abc import ABC, abstractmethod

class Columns(IntEnum):
    A, B, C, D, E, F, G, H = tuple(range(0,8))

class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.row = y
        self.col = Columns(x).name.lower()

class Piece(ABC):
    class Colors(IntEnum):
        WHITE = 0
        BLACK = 1

    class Types(Enum):
        PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING = auto()
    
    def __init__(self, color: Colors, name) -> None:
        self.color = color
        self.name = name

    @abstractmethod
    def isPathValid(self, endX, endY):
        pass

    @abstractmethod
    def getPath(self, startX, startY, endX, endY):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def clone(self):
        pass
    
class Pawn(Piece):
    pass

class Rook(Piece):
    pass

class Knight(Piece):
    pass

class Bishop(Piece):
    pass

class Queen(Piece):
    pass

class King(Piece):
    pass

class Board: 
    class Square:
        def __init__(self, coordinates: Pair, piece: Piece):
            self.coords = coordinates
            self.piece = piece
    class EmptySquare(Square):
        def __init__(self, coordinates: Pair):
            super().__init__(coordinates, None)


class Chess:
    pass



def main():
    p = Piece(Piece.Colors.WHITE, "pawn")

    print(p)

if __name__ == "__main__":
    main()