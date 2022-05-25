""" Chess Pieces
    ------------
    Every piece used in a normal game of chess.
    
    Pieces should inherit from the abstract `Piece` class and should
    implement all of this class's methods.
"""

# Typing 
from typing import Literal, Callable

# Class imports
from abc import ABC, abstractmethod

# Chess imports
from chess_enum import Color, Type
from pair import Pair

class Piece(ABC):
    """An abstract class representing a chess piece."""
    def __init__(self, color: Color, type: Type) -> None:
        self.color = color
        self.type = type
        self.has_moved = False

    def __eq__(self, __o: 'Piece') -> bool:
        if __o:
            return self.color == __o.color and self.type == __o.type
        else:
            return False

    def __str__(self) -> str:
        return f"{self.color.name} {self.type.name}"

    def __repr__(self) -> str:
        return self.__str__()
    
    def __hash__(self) -> int:
        return hash((self.color, self.type))

    @abstractmethod
    def is_valid_path(self, start: Pair, end: Pair) -> bool | Literal['c']:
        """Is the path valid?"""
        pass

    @abstractmethod
    def get_path(self, start: Pair, end: Pair) -> list[Pair]:
        """Return the path."""
        pass

    @abstractmethod
    def get_all_ends(self, start: Pair) -> list[Pair]:
        """Get every possible square the piece can land on."""
        pass
    
    @abstractmethod
    def clone(self):
        """Copy this piece."""
        pass
    

class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, Type.PAWN)

    def is_valid_path(self, start: Pair, end: Pair) -> bool | Literal['c']:
        # Color determines direction
        if start.x == end.x: # Going straight

            if start.row + (2*self.color) == end.row: # Going 2 forward?
                return not self.has_moved # First move?
            elif start.row + self.color == end.row: # Going 1 forward
                return True # Always ok
            else: 
                return False
        elif (abs(start.x-end.x)) and (start.row + self.color == end.row): # Capture?
            return 'c' # Return c because this move is only valid if it is a capture
        else: # No valid options
            return False

    def get_path(self, start: Pair, end: Pair):
        path: list[Pair] = list() # List of coordinate the piece will move

        if start.x != end.x: # If the pawn is moving diagonally (capture)
            path = [end]
        else: # If the pawn is moving straight 
            path = [Pair(start.y+self.color, start.x), Pair(start.y+2*self.color, start.x)]

        return path
    
    def get_all_ends(self, start: Pair) -> list[Pair]:
        ends: list[Pair] = list()
        
        ends.append(Pair(start.y+self.color, start.x))
        ends.append(Pair(start.y+self.color, start.x+1))
        ends.append(Pair(start.y+self.color, start.x-1))
        
        if not self.has_moved:
            ends.append(Pair(start.y+(2*self.color), start.x))
            
        i = 0
        while i < len(ends):
            if ends[i].x < 0 or ends[i].y < 0:
                ends.pop(i)
            else:
                i += 1
            
        return ends

    def clone(self):
        return Pawn(self.color)

        
class Rook(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.ROOK)

    def is_valid_path(self, start: Pair, end: Pair):
        h = start.x == end.x
        v = start.y == end.y

        if h ^ v: # xor, checking if going horizontally and vertically or not moving
            return True
        else: # Must be going both or neither
            return False
    
    def get_path(self, start: Pair, end: Pair):
        path: list[Pair] = list()
        path_len: int
        
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
            path_len = abs(start.x-end.x)
        else:
            path_len = abs(start.y-end.y)

        for i in range(1, path_len+1): # Goes from 1 to length of path

            if xDir: # If x is not constant
                path.append(Pair(start.y, start.x + i*xDir)) # Y is constant 
            else:
                path.append(Pair(start.y + i*yDir, start.x)) # X is constant

        return path
    
    @staticmethod
    def get_all_ends(start: Pair, max_dist: int=8) -> list[Pair]:
        ends: list[Pair] = list()
        
        for x in range(-max_dist, max_dist):
            if x != 0 and start.x + x >= 0:
                ends.append(Pair(start.y, start.x+x))
            
        for y in range(-max_dist, max_dist):
            if y != 0 and start.y + y >= 0:
                ends.append(Pair(start.y+y, start.x))
            
        # ends.sort(key = lambda l : (l.y, l.x))
            
        return ends
    
    def clone(self):
        return Rook(self.color)
        

class Knight(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.KNIGHT)
    
    def is_valid_path(self, start: Pair, end: Pair):
        xDiff = abs(start.x - end.x)
        yDiff = abs(start.y - end.y)

        # Ensures the path is an L shape (2 one way and 1 the other)
        # xDiff xor yDiff == 2 and xDiff xor yDiff == 1
        if ((xDiff == 2) ^ (yDiff == 2)) and ((xDiff == 1) ^ (yDiff == 1)): 
            return True
        else:
            return False

    def get_path(self, start: Pair, end: Pair):
        return [end]
    
    @staticmethod
    def get_all_ends(start: Pair) -> list[Pair]:
        y = start.y
        x = start.x
        
        ends = [Pair(y+2, x+1), Pair(y+2, x-1), Pair(y-2, x+1), Pair(y-2, x-1),
                Pair(y+1, x+2), Pair(y+1, x-2), Pair(y-1, x+2), Pair(y-1, x-2)]
        
        i = 0
        while i < len(ends):
            if ends[i].x < 0 or ends[i].y < 0:
                ends.pop(i)
            else:
                i += 1
        
        return ends
        
    def clone(self):
        return Knight(self.color)


class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.BISHOP)

    def is_valid_path(self, start: Pair, end: Pair):
        return abs(start.x-end.x) == abs(start.y - end.y) and start != end

    def get_path(self, start: Pair, end: Pair):
        path: list[Pair] = list()

        path_len = abs(start.x-end.x) # Length of the path

        # Finding x and y directions
        xDir = yDir = 1
        if start.x > end.x:
            xDir = -1
        if start.y > end.y:
            yDir = -1

        for i in range(1, path_len+1):
            path.append(Pair(start.y + i*yDir, start.x + i*xDir))

        return path
    
    @staticmethod
    def get_all_ends(start: Pair, max_dist: int=8) -> list[Pair]:
        ends: list[Pair] = list()
        
        for y_dir in (-1, 1):
            for x_dir in (-1, 1):
                for y in range(max_dist):
                    for x in range(max_dist):
                        if start.x + x*x_dir >= 0 and start.y + y*y_dir >= 0:
                            ends.append(Pair(start.y+y*y_dir, start.x+x*x_dir))

        # ends.sort(key = lambda l : (l.y, l.x))
        
        return ends
        
    def clone(self):
        return Bishop(self.color)


class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.QUEEN)

    def is_valid_path(self, start: Pair, end: Pair):
        return Bishop(self.color).is_valid_path(start, end) or Rook(self.color).is_valid_path(start, end)

    def get_path(self, start: Pair, end: Pair):

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
            return Bishop(self.color).get_path(start, end)
        else:
            return Rook(self.color).get_path(start, end)
        
    @staticmethod
    def get_all_ends(start: Pair, max_dist:int=8) -> list[Pair]:
        ends: list[Pair] = list()
        
        ends = Bishop.get_all_ends(start, max_dist) + Rook.get_all_ends(start, max_dist)
        
        ends.sort(key = lambda l : (l.y, l.x))
        
        return ends

    def clone(self):
        return Queen(self.color)


class King(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.KING)
        self.has_moved = False

    def is_valid_path(self, start: Pair, end: Pair):
        return (abs(start.x-end.x) <= 1) and (abs(start.y-end.y) <= 1) and start != end

    def get_path(self, start: Pair, end: Pair):
        return [end]
    
    @staticmethod
    def get_all_ends(start: Pair) -> list[Pair]:
        ends: list[Pair] = list()
        for y_dir in (-1, 0, 1):
            for x_dir in (-1, 0, 1):
                new_x = start.x + x_dir
                new_y = start.y + y_dir
                
                if new_x >= 0 and new_y >= 0:
                    ends.append(Pair(new_y, new_x))
                    
        return ends

    def clone(self):
        return King(self.color)


piece_dict: dict[Type, Callable[[Color], None]] = {
    Type.PAWN   : Pawn,
    Type.KING   : King,
    Type.QUEEN  : Queen,
    Type.ROOK   : Rook,
    Type.BISHOP : Bishop,
    Type.KNIGHT : Knight
} 
"""Mapping all the types to their `Piece` constructors"""

# Alias for piece dict
PIECES = piece_dict
"""Mapping all the types to their `Piece` constructors (Alias)"""