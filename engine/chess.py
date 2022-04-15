# By Chris Parker
# Typing imports
from typing import Any, Literal

# Class imports
from abc import ABC, abstractmethod

# Chess Imports
from exceptions import InvalidFENError
from chess_enum import Color, Column, Type

# Utility 
from copy import deepcopy
from linked_list import DoubleLinkedList as DLL, Node

# Testing/Debug
from time import perf_counter

class Pair:
    """A class representing a coordinate on a chess board."""
    A = 65 # A in ASCII

    def __init__(self, y: int, x: int) -> None:
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

        if self.y != None and self.x != None:
            self.row = y+1
            self.col = chr(self.A + x)

            self.rank = self.row
            self.file = self.col
    
    def get_alg_coords(self) -> str:
        """Return the algebraic version of this coordinate."""
        return f"{self.col.lower()}{self.row}"

    def is_negative(self) -> bool:
        return True if self.x < 0 or self.y < 0 else False

    def is_above(self, maxY, maxX) -> bool:
        return True if self.x > maxX or self.y > maxY else False
    
    def to_standard(self) -> tuple[int, int]:
        return (self.x, self.y)

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.get_alg_coords()
    
    def __repr__(self) -> str:
        return f"{self.y},{self.x}; {self.col}{self.row}"

    def __bool__(self) -> bool:
        return (self.x != None and self.y != None)

    def __eq__(self, other: 'Pair' | Any) -> bool:
        if type(other) == Pair:
            return self.x == other.x and self.y == other.y
        else:
            return False
    
    def __getitem__(self, key: int | str) -> int | None:
        if key == "x" or key == "row" or key == 0:
            return self.x
        elif key == "y" or key == "col" or key == 1:
            return self.y
        
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

    @abstractmethod
    def is_valid_path(self, start: Pair, end: Pair) -> bool | Literal['c']:
        pass

    @abstractmethod
    def get_path(self, start: Pair, end: Pair) -> list[Pair]:
        pass

    @abstractmethod
    def get_all_ends(self, start: Pair) -> list[Pair]:
        pass
    
    @abstractmethod
    def clone(self):
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

class Square:
        def __init__(self, coordinates: Pair, piece: Piece | None) -> None:
            self.coords = coordinates
            self.piece = piece
        
        def __str__(self) -> str:
            return str(self.piece)

        def __repr__(self) -> str:
            return self.__str__() + f" ({self.coords.get_alg_coords()})"

class ChessBoard:
    # CONSTRUCTOR
    def __init__(self, start_FEN: str=None) -> None:
        # GLOBAL CLASS VARIABLES

        # Pieces 
        # White    
        self.wr, self.wn, self.wb = Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE)
        self.wq, self.wk, self.wp = Queen(Color.WHITE), King(Color.WHITE), Pawn(Color.WHITE)

        # Black
        self.br, self.bn, self.bb = Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK)
        self.bq, self.bk, self.bp = Queen(Color.BLACK), King(Color.BLACK), Pawn(Color.BLACK)

        # Origin (A1) is at 0,0 (top-left)
        self.EMPTY_BOARD = tuple(tuple(Square(Pair(y, x), None) for x in range(8)) for y in range(8)) # Blank board
        self.DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" # FEN for default placement
        
        self.attacked_squares_w: list[list[Pair, int]] = list() # Squares attacked by white
        self.attacked_squares_b: list[list[Pair, int]] = list() # Squares attacked by black
        self.board: list[list[Square]] = deepcopy(list(self.EMPTY_BOARD))
        
        if start_FEN:
            self.FEN_set_postion(start_FEN)
        else:
            self.reset_board()
        self.update_attacked_squares()
        

    # MOVEMENT METHODS
    def can_move(self, frm: Pair, to: Pair, pseudoCap: Pair=None) -> tuple[bool, Literal['c']| None]:
        """Check if a piece can move using its own methods and checking the path it would take.

        Parameters
        ----------
        frm : Pair
            Starting square.
        to : Pair
            Ending square.
        pseudoCap : Pair
            Square that can be "captured" but is empty (e.g., en passant square),

        Returns
        -------
        tuple[bool, Literal['c'] | None]
            Return True if the piece can move or False if it cannot. Returns 'c' if the move would
            result in a capture.
        """
        sSquare = self.get_square(frm)
        fSquare = self.get_square(to)

        valid = sSquare.piece.is_valid_path(frm, to)

        if (sSquare.piece == None) or (not valid):
            # print(sSquare.piece, valid, fSquare.piece)
            return False, None

        if fSquare.piece != None and sSquare.piece.color == fSquare.piece.color:
            # print(2)
            return False, None

        path = sSquare.piece.get_path(frm, to)

        if sSquare.piece.type == Type.PAWN and len(path) > 1 and fSquare.piece:
            return  False, None

        for i in range(len(path)):
            if i < len(path)-1:
                if self.get_square(path[i]).piece != None:
                    return False, None
            elif valid == 'c':
                if pseudoCap and fSquare.coords == pseudoCap:
                    return True, 'c'
                elif fSquare.piece == None:
                    return False, None

        return True, ('c' if fSquare.piece != None and fSquare.piece.color != sSquare.piece.color else None)

    def move(self, frm: Pair, to: Pair) -> Piece | None:
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
        cSquare = self.get_square(frm)
        fSquare = self.get_square(to)

        cap = fSquare.piece
        fSquare.piece = cSquare.piece
        fSquare.piece.has_moved = True
        cSquare.piece = None

        return cap

    # MODIFIER METHODS
    def set_square(self, sqr: Pair, piece: Piece) -> None:
        self.get_square(sqr).piece = piece

    def reset_board(self) -> None:
        self.FEN_set_postion(self.DEFAULT_FEN)

    def update_attacked_squares(self):
        """Update attacked_squares_w and attacked_squares_b to accurately show the squares under attack."""
        # This whole function seems really inefficient. It'll be fine for now but it feels dumb

        def _cull_all():
            """Format data after receiving coordinates from functions."""
            def _cull(list: list[Pair]):
                """Format data for one list."""
                i = 0
                while i < len(list):
                    pair = list[i]
                    if pair.is_negative() or pair.is_above(len(self.board)-1, len(self.board[0])-1):
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

            _cull(self.attacked_squares_w)
            _cull(self.attacked_squares_b)

        def _byPawn(square: Square) -> list[Pair]:
            return [
                Pair(square.coords.y + square.piece.color, square.coords.x-1),
                Pair(square.coords.y + square.piece.color, square.coords.x+1)
            ] # Pawns can only attack 2 squares
        
        def _byKing(square: Square) -> list[Pair]:
            return [
                Pair(square.coords.y-1, square.coords.x-1), Pair(square.coords.y+1, square.coords.x+1), 
                Pair(square.coords.y-1, square.coords.x+1), Pair(square.coords.y+1, square.coords.x-1), 
                Pair(square.coords.y, square.coords.x+1),   Pair(square.coords.y, square.coords.x-1),
                Pair(square.coords.y+1, square.coords.x),   Pair(square.coords.y-1, square.coords.x)
            ] # Returns all squares around king. Invalid squares are removed later

        def _byBishop(square: Square) -> list[Pair]:
            rtn = list()
            
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

        def _byRook(square: Square) -> list[Pair]:

            def _findStop(list: list[Pair]) -> list[Pair]:
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
            maxYPath = square.piece.get_path(square.coords, Pair(maxY, x))
            minYPath = square.piece.get_path(square.coords, Pair(0, x))

            maxXPath = square.piece.get_path(square.coords, Pair(y, maxX))
            minXPath = square.piece.get_path(square.coords, Pair(y, 0))

            # Return all 4 paths rook covers
            return _findStop(maxYPath) + _findStop(minYPath) + _findStop(maxXPath) + _findStop(minXPath)

        def _byQueen(square: Square) -> list[Pair]:
            # Queens have the movement of a bishop and rook combined 
            return _byBishop(square) + _byRook(square) 

        def _byKnight(square: Square) -> list[Pair]:
            p = square.coords
            
            # Returns all squares around knight. Invalid squares are removed later
            return Knight.get_all_ends(p)
        
        # Clears old lists
        self.attacked_squares_w.clear()
        self.attacked_squares_b.clear()

        # Goes through every rank and file
        for rank in self.board: 
            for square in rank:
                # Ensuring there is a piece on the square
                if square.piece != None:
                    if square.piece.color == Color.WHITE:
                        # Using eval to avoid dummy thicc if statement blocks. Will evaluate to something like:
                        # `_by<Piece>(square)` where "<Piece>" is the name of the piece.
                        #
                        # WARNING: This can be dangerous! It should be fine in this case but this may need to be 
                        # reevaluated in a later program
                        self.attacked_squares_w += eval("_by"+(square.piece.type.name.capitalize())+"(square)")
                    else:
                        self.attacked_squares_b += eval("_by"+(square.piece.type.name.capitalize())+"(square)")
        
        # # Sort the lists with the y's and then the x's
        # self.attacked_squares_w.sort(key = lambda l : (l.y, l.x))
        # self.attacked_squares_b.sort(key = lambda l : (l.y, l.x))

        _cull_all() # Format the data    
    
    # ACCESSOR METHODS
    def get_square(self, squarePos: Pair) -> Square:
        return self.board[squarePos.y][squarePos.x]

    def get_king_position(self, color: Color) -> Pair:
        for rank in range(len(self.board)):
            for file in range(len(self.board[rank])):
                square = self.get_square(Pair(rank, file))
                if square.piece and square.piece.type == Type.KING and square.piece.color == color:
                    return Pair(rank, file)
        
    def in_attacked(self, coord: Pair, side: Color) -> bool:
        atk = None
        if side == Color.WHITE:
            atk = self.attacked_squares_b
        else:
            atk = self.attacked_squares_w
            
        for item in atk:
            if item[0] == coord:
                return True
            
        return False
        
    # FEN METHODS
    def FEN_piece_placement(self) -> str:
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
        # Rank (from 8 to 1)
        for rank in range(len(self.board)-1, -1, -1):
            # File (from A to H)
            for square in self.board[rank]:
                piece = square.piece
                
                if piece != None: # If the square isn't empty
                    if digit: # If there is a digit
                        rtn += str(digit)
                        digit = 0

                    l: str = piece.type.value # Letter

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
        
    def FEN_set_postion(self, FEN: str) -> None:
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

                self.set_square(Pair(rank, file), piece.clone())
                file += 1
            elif l.isnumeric():
                for f in range(file, file+int(l)):
                    self.set_square(Pair(rank, f), None)
                file += int(l)


            if l == '/':
                rank -= 1
                if rank < 0:
                    raise InvalidFENError(FEN)
                file = 0

            if l == ' ': # Must be the end of position section
                break    # Other sections can be disguarded
            
        # Now check that any moved pieces have movement indicated in piece attributes
        compare_FEN = self.__expand_FEN(FEN.split(" ")[0]).split("/")
        compare_def = self.__expand_FEN(self.DEFAULT_FEN).split("/")

        # assert len(compare_FEN) == len(compare_def)
        
        for row_i, (board_row, def_row) in enumerate(zip(reversed(compare_FEN), reversed(compare_def))):
            # assert len(board_row) == len(def_row)
            for col_i, (board_char, def_char) in enumerate(zip(board_row, def_row)):
                if board_char != def_char:
                    if board_char != "#":
                        self.board[row_i][col_i].piece.has_moved = True

        self.update_attacked_squares()
            
    @staticmethod
    def in_board(pair: Pair) -> bool:
        if pair.y >= 0 and pair.y < 8 and pair.x >= 0 and pair.x < 8:
            return True
        
        return False
            
    @staticmethod
    def __expand_FEN(FEN: str) -> str:
        """Fill in blanks (indicated by numbers) with `#` to normalize length.

        Parameters
        ----------
        FEN : str
            FEN string to expand

        Returns
        -------
        str
            Expanded FEN string
        """
        new_FEN = list()
        for char in FEN:
            if char.isalpha() or char == "/":
                new_FEN.append(char)
            elif char.isnumeric():
                for i in range(int(char)):
                    new_FEN.append("#")
                    
        return "".join(new_FEN)

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.FEN_piece_placement()

    def __repr__(self) -> str:
        rtn = ""
        for row in self.board:
            rtn += repr(row) + '\n'

        return rtn

class GameStates(DLL):
    MAX = 1000
    
    def __init__(self, start_state):
        super().__init__(start_state)
        self.start = start_state
    
    def add_state(self, state: 'Chess'):
        if self.len + 1 < self.MAX:
            self.add_end(state)
        
    def remove_state(self):
        self.remove_last()
        
    def new_branch(self, state: 'Chess'=None):
        if self.current.next:
            self.current.next.previous = None # Delete the pointer of the next node
        if state:
            self.current.next = Node(state, None, self.current) # Set the next pointer to the new branch
            self.tail = self.current.next
        else:
            self.tail = self.current
        self._count_len()
        

class Chess:
    """Play a game of chess."""

    def __init__(self, save_moves=True) -> None:
        self.board = ChessBoard()
        self.white_cap: list[Piece] = list() # Captured white pieces
        self.black_cap: list[Piece] = list() # Captured black pieces
        self.en_pass: Pair = None # En passant square
        self.white_turn = True # Who's turn
        self.half_move = 0 
        self.full_move = 1
        
        self.all_legal_w: list[str] = list()
        self.all_legal_b: list[str] = list()
        
        self.game_states = None
        if save_moves:
            self.game_states = GameStates(Chess(False))
            
        self.en_pass_capture: Pair = Pair(None, None)
        
    @classmethod
    def bare(cls):
        game = cls.__new__(cls)
        
        game.board = ChessBoard()
        game.en_pass = None
        game.game_states = None
        
        return game
    
    def in_check(self, side: Color) -> bool:
        """Find if the king of color `side` is in check.

        Parameters
        ----------
        side : Color
            Color of king

        Returns
        -------
        bool
            True if in check (i.e. the king is in a square attacked by other side)
        """
        king = self.board.get_king_position(side)
        if self.board.in_attacked(king, side):
            return True
            
        return False # No if statements were true, return False
            
    def in_checkmate(self, side: Color) -> bool:
        """Find if the king of color `side` is in checkmate.

        Parameters
        ----------
        side : Color
            Color of king

        Returns
        -------
        bool
            True if in checkmate (i.e. the king is in a square attacked by other side and there are no legal moves)
        """
        
        if self.in_check(side):
            
            if side == Color.WHITE and len(self.all_legal_w) == 0:
                return True
            elif side == Color.BLACK and len(self.all_legal_b) == 0:
                return True
        else:
            return False
        
    def in_stalemate(self) -> bool:
        """Find if the game has ended in a stalemate

        Returns
        -------
        bool
            True if the game is in stalemate
        """
        
        if self.white_turn and len(self.all_legal_w) == 0:
            return True
        elif not self.white_turn and len(self.all_legal_b) == 0:
            return True
        
        return False
    
    def legal_moves(self, pair: Pair) -> list[Pair]:
        """Find every legal move for the given piece.

        Parameters
        ----------
        pair : Pair
            Square the piece is on

        Returns
        -------
        list[Pair]
            A list of legal moves
        """
        piece = self.get_piece(pair)
        legal: list[Pair] = list()
        
        if piece:
            if piece.type == Type.ROOK:
                legal = self.__rook_legal(pair)
            elif piece.type == Type.BISHOP:
                legal = self.__bishop_legal(pair)
            elif piece.type == Type.QUEEN:
                legal = self.__queen_legal(pair)
            else:
                for end in piece.get_all_ends(pair):
                    if self.board.in_board(end):
                        # TODO: Make this more efficient
                        nxt, can = self.next_move(pair, end)
                        if can and not nxt.in_check(piece.color):
                            legal.append(end)

                if piece.type == Type.KING:
                    for corner in (Pair(0, 0), Pair(0,7), Pair(7, 0), Pair(7, 7)):
                        # if self.get_piece(corner) and self.can_castle(pair, corner):
                        #     legal.append(corner)
                        nxt1, can1 = self.next_move(pair, corner)
                        if can1 and not nxt1.in_check(piece.color):
                            legal.append(corner)
                            
                    
        # legal.sort(key = lambda l: (l.y, l.x))
        
        return legal
    
    def __rook_legal(self, pair: Pair):
        piece = self.get_piece(pair)
        legal: list[Pair] = list()
        
        left_safe = False
        right_safe = False
        up_safe = False
        down_safe = False
        
        ends = piece.get_all_ends(pair)
        remove = list()
        for end in ends:
            if self.board.in_board(end):
                left = end.x == pair.x - 1
                right = end.x == pair.x + 1
                up = end.y == pair.y + 1
                down = end.y == pair.y - 1
                if left or right or up or down:
                    nxt, can = self.next_move(pair, end)
                    if can and not nxt.in_check(piece.color):
                        legal.append(end)

                        # Don't change value if it's True
                        left_safe = left or left_safe
                        right_safe = right or right_safe
                        up_safe = up or up_safe
                        down_safe = down or down_safe
                    else:
                        remove.append(end)
            else:
                remove.append(end)
                    
        for end in remove:
            ends.remove(end)
                    
        for end in ends:
            if self.board.in_board(end):
                left = end.x < pair.x
                right = end.x > pair.x
                up = end.y > pair.y
                down = end.y < pair.y
                if left and left_safe or right and right_safe or up and up_safe or down and down_safe:
                    if self.board.can_move(pair, end, self.en_pass)[0]:
                        legal.append(end)
                        
        return legal
    
    def __bishop_legal(self, pair: Pair):
        piece = self.get_piece(pair)
        legal: list[Pair] = list()
        
        ul_safe = False # Up - left
        ur_safe = False # Up - right
        dl_safe = False # Down - left
        dr_safe = False # Down - right
        
        ends = piece.get_all_ends(pair)
        remove = list()
        for end in ends:
            if self.board.in_board(end):
                ul = end.y == pair.y + 1 and end.x == pair.x - 1
                ur = end.y == pair.y + 1 and end.x == pair.x + 1
                dl = end.y == pair.y - 1 and end.x == pair.x - 1
                dr = end.y == pair.y - 1 and end.x == pair.x + 1

                if ul or ur or dl or dr:
                    nxt, can = self.next_move(pair, end)
                    if can and not nxt.in_check(piece.color):
                        legal.append(end)
                        remove.append(end)

                        # Don't change value if it's True
                        ul_safe = ul or ul_safe
                        ur_safe = ur or ur_safe
                        dl_safe = dl or dl_safe
                        dr_safe = dr or dr_safe
            else:
                remove.append(end)
                    
        for end in remove:
            ends.remove(end)
                    
        for end in ends:
            if self.board.in_board(end):
                ul = end.y > pair.y and end.x < pair.x - 1
                ur = end.y > pair.y and end.x > pair.x + 1
                dl = end.y < pair.y and end.x < pair.x - 1
                dr = end.y < pair.y and end.x > pair.x + 1
                if ul and ul_safe or ur and ur_safe or dl and dl_safe or dr and dr_safe:
                    if self.board.can_move(pair, end, self.en_pass)[0]:
                        legal.append(end)
                        
        return legal
    
    def __queen_legal(self, pair: Pair):
        return self.__rook_legal(pair) + self.__bishop_legal(pair)
    
    def all_legal_moves(self, side: Color) -> list[tuple[Pair, list[Pair]]]:
        """Find the legal moves for every piece on the board of a given color.

        Parameters
        ----------
        side : Color
            Color to check

        Returns
        -------
        list[tuple[Pair, list[Pair]]]
            A list of (Piece, Move(s)) tuples
        """
        legal: list[tuple[Pair, Pair]] = list() # List of from-to
        
        for row in range(8):
            for col in range(8):
                p = Pair(row, col)
                if self.get_piece(p) and self.get_piece(p).color == side:
                    move = self.legal_moves(p)
                    if move:
                        legal.append((p, move))
                    
        # return sorted(legal, key = lambda l: (l[0].y, l[0].x))
        return legal
    
    def update_all_legal(self) -> None:
        """Update legal move lists
        """
        self.all_legal_w = self.all_legal_moves(Color.WHITE)
        self.all_legal_b = self.all_legal_moves(Color.BLACK)
    
    def move(self, frm: Pair, to: Pair) -> bool:
        """Move piece from a square to another if that move is valid. 
        NOTE: Automatically captures pieces.
        NOTE: Does not check for check or checkmate

        Parameters
        ----------
        frm : Pair
            Start position
        to : Pair
            End position

        Returns
        -------
        bool
            True if movement was successful, False otherwise
        """
        rtn = False
        nxt, can = self.next_move(frm, to)
        
        if can and not nxt.in_check(Color.WHITE if self.white_turn else Color.BLACK):
            rtn, cap = self.__move(frm, to)
            
            if cap:
                if cap.color == Color.WHITE:
                    self.white_cap.append(cap)
                else:
                    self.black_cap.append(cap)
        
        return rtn
    
    def __move(self, frm: Pair, to: Pair) -> tuple[bool, Piece | None]:
        """Move piece from a square to another if that move is valid. 
        NOTE: Internal function! Use Chess.move() instead

        Parameters
        ----------
        frm : Pair
            Start position
        to : Pair
            End position

        Returns
        -------
        bool
            True if movement was successful, False otherwise
        """
        start = self.board.get_square(frm)
        pwn = start.piece.type == Type.PAWN
        cap = None
        
        
        if (self.board.can_move(frm, to, self.en_pass)[0] 
            and ((start.piece.color == Color.WHITE) == self.white_turn)
            ):
            cap = self.board.move(frm, to)
            
            # En passant
            self.en_pass_capture = None
            if self.en_pass and to == self.en_pass:
                cap_pos = Pair(to.y + (-1 if self.white_turn else 1), to.x)
                                
                if self.get_piece(cap_pos).color != start.piece.color:
                    cap = self.get_piece(cap_pos)
                    self.en_pass_capture = cap_pos
                    self.board.set_square(cap_pos, None)
                
            self.en_pass = None # En passant chance ends every turn
            if pwn and abs(frm.y - to.y) == 2:
                sign = -((frm.y - to.y) // abs(frm.y - to.y))
                self.en_pass = Pair(frm.y + sign, frm.x)
            
        # Check for castling conditions
        elif (start.piece and self.get_piece(to)):
                if self.can_castle(frm, to): # Castling worked
                    self.castle(frm, to)
                else:
                    return False, None
        else: # Nothing works
            return False, None
        
        # Increment move counters after successful move
        if not self.white_turn:
            self.full_move += 1
            
        if not cap and not pwn:
            self.half_move += 1
        else:
            self.half_move = 0
            
        self.white_turn = not self.white_turn
        
        self.board.update_attacked_squares()
        if self.game_states:
            self.game_states.add_state(self.generic_copy())
        
        return True, cap
    
    def next_move(self, frm: Pair, to: Pair) -> tuple['Chess', bool]:
        new_chess = self.bare_copy()
        rtn, _ = new_chess.__move(frm, to)
        
        return new_chess, rtn
    
    def castle(self, frm: Pair, to: Pair) -> None:
            
        # Move the king and rook
        if frm.x < to.x:
            self.board.move(frm, Pair(to.y, frm.x + 2))
            self.board.move(to, Pair(to.y, frm.x + 1))
        else:
            self.board.move(frm, Pair(to.y, frm.x - 2))
            self.board.move(to, Pair(to.y, frm.x - 1))
    
    def can_castle(self, frm: Pair, to: Pair) -> bool:
        king = self.get_piece(frm)
        rook = self.get_piece(to)
        
        # Make sure the pieces are a king and a rook
        if not (king.type == Type.KING and rook.type == Type.ROOK):
            return False
        
        # Right color?
        if not (king.color == rook.color):
            return False

        if not(
            to == alg_to_pair("a1") or to == alg_to_pair("h1") or to == alg_to_pair("a8") or to == alg_to_pair("h8")
            ):
            return False
        
        if self.in_check(king.color):
            return False

        # Check if that castling option is valid
        castle_str = self.castle_options()
        if to == alg_to_pair("a1") and "Q" not in castle_str:
            return False
        if to == alg_to_pair("h1") and "K" not in castle_str:
            return False
        if to == alg_to_pair("a8") and "q" not in castle_str:
            return False
        if to == alg_to_pair("h8") and "k" not in castle_str:
            return False
        
        # Check if the path is clear
        if frm.x < to.x:
            c_col = frm.x + 1
            while c_col < 7:
                sqr = self.board.get_square(Pair(frm.y, c_col))
                if sqr.piece or self.board.in_attacked(sqr.coords, king.color):
                    return False
                c_col += 1
        
        if frm.x > to.x:
            c_col = frm.x - 1
            while c_col > 0:
                sqr = self.board.get_square(Pair(frm.y, c_col))
                if sqr.piece or (self.board.in_attacked(sqr.coords, king.color) and c_col > 1):
                    return False
                c_col -= 1
            
        return True
        
    def castle_options(self) -> str:
        """Generate string that contains castling options.

        Returns
        -------
        str
            String in the form `KQkq` or `-`
        """
        option_string = "" 
        
        A1 = self.get_piece(Pair(0,0))
        H1 = self.get_piece(Pair(0,7))
        A8 = self.get_piece(Pair(7,0))
        H8 = self.get_piece(Pair(7,7))
        w_king = self.get_piece(Pair(0,4))
        b_king = self.get_piece(Pair(7,4))
        
        if w_king and not w_king.has_moved:
            if A1 and not A1.has_moved:
                option_string += "Q"
            if H1 and not H1.has_moved:
                option_string += "K"
                
        if b_king and not b_king.has_moved:
            if H8 and not H8.has_moved:
                option_string += "k"
            if A8 and not A8.has_moved:
                option_string += "q"

        return option_string if bool(option_string) else "-"
        
    def get_piece(self, pos: Pair) -> Piece:
        """Get piece at postion.

        Parameters
        ----------
        pos : Pair
            Postion of piece (row, column)

        Returns
        -------
        Piece
            Piece at given position
        """
        return self.board.get_square(pos).piece
    
    def get_FEN(self) -> str:
        """Return the FEN version of the current game.

        Returns
        -------
        str
            Full FEN string
        """
        FEN_string = [self.board.FEN_piece_placement(), "w" if self.white_turn else "b", self.castle_options(), 
                      self.en_pass.get_alg_coords() if self.en_pass else "-", str(self.half_move), 
                      str(self.full_move)]
        
        return " ".join(FEN_string)
    
    def set_FEN(self, FEN: str):
        """Set the game state using a FEN string.

        Parameters
        ----------
        FEN : str
            FEN String

        Raises
        ------
        InvalidFENError
            If the FEN string is improperly formatted or has conflicting information
        """
        # Function variables 
        castle_err = "Castle options do not match position."
        A1 = self.get_piece(Pair(0,0))
        H1 = self.get_piece(Pair(0,7))
        A8 = self.get_piece(Pair(7,0))
        H8 = self.get_piece(Pair(7,7))
        w_king = self.get_piece(Pair(0,4))
        b_king = self.get_piece(Pair(7,4))
        
        # Split the string into sections
        sects = FEN.split()
        
        # Ensure there are no more or less than 6 sections
        if len(sects) != 6:
            raise InvalidFENError(FEN)
        
        # Set the position
        # NOTE: No need to raise exception here, FEN_set_postion function will do it
        self.board.FEN_set_postion(sects[0])
        
        # Set the current turn
        # NOTE: No exception here. This is a simple error we can deal with
        self.white_turn = True if sects[1].lower() == "w" else False
        
        # Castle options
        if len(sects[2]) > 4: # There shouldn't be more than 4 castling options
            raise InvalidFENError(FEN)
        
        # Check every option and ensure there is no conflicting info w/ position
        for char in sects[2]:
            if char == "K":
                if H1 != self.board.wr:
                    raise InvalidFENError(FEN, castle_err)
                    
            if char == "Q":
                if A1 != self.board.wr:
                    raise InvalidFENError(FEN, castle_err)
                
            if (char == "K" or char == "Q"):
                if w_king != self.board.wk:
                    raise InvalidFENError(FEN, castle_err)
            
            if char == "k":
                if H8 != self.board.br:
                    raise InvalidFENError(FEN, castle_err)
            
            if char == "q":
                if A8 != self.board.br:
                    raise InvalidFENError(FEN, castle_err)
            
            if char == "k" or char == "q":
                if b_king != self.board.bk:
                    raise InvalidFENError(FEN, castle_err)
                
        # Changing the has_moved variable for castling pieces
        if "K" not in sects[2] and H1 == self.board.wr:
            H1.has_moved = True
        if "Q" not in sects[2] and A1 == self.board.wr:
            A1.has_moved = True
        if "k" not in sects[2] and H8 == self.board.br:
            H8.has_moved = True
        if "q" not in sects[2] and A8 == self.board.br:
            A8.has_moved = True
            
        # En passant square
        if sects[3] != "-":
            self.en_pass = alg_to_pair(sects[3])
        else:
            self.en_pass = None
            
        # Halfmove clock
        if not sects[4].isdigit():
            raise InvalidFENError(FEN, "Invalid halfmove clock.")
        
        self.half_move = int(sects[4])
        
        # Fullmove clock
        if not sects[5].isdigit():
            raise InvalidFENError(FEN, "Invalid fullmove clock.")
        
        self.full_move = int(sects[5]) 
        
    def bare_copy(self) -> 'Chess':
        new_chess = self.bare()
        new_chess.set_FEN(self.get_FEN())
        new_chess.white_turn = self.white_turn
        # print(new_chess.board == self.board)
        
        return new_chess
        
    def generic_copy(self) -> 'Chess':
        new_chess = Chess(False)
        new_chess.set_FEN(self.get_FEN())
        new_chess.white_turn = self.white_turn
        new_chess.white_cap = self.white_cap.copy()
        new_chess.black_cap = self.black_cap.copy()
        
        return new_chess
        
    def copy(self) -> 'Chess':
        new_chess = Chess(True)
        new_chess.set_FEN(self.get_FEN())
        new_chess.white_turn = self.white_turn
        new_chess.white_cap = self.white_cap.copy()
        new_chess.black_cap = self.black_cap.copy()
        
        return new_chess
        
    def __str__(self) -> str:
        return self.get_FEN()
    
    def __repr__(self) -> str:
        return "\n\n".join((self.__str__(), self.board.__repr__()))
    
    
def alg_to_pair(string: str) -> Pair:
    """Convert pieceless algebraic coordinates into Pair.

    Parameters
    ----------
    string : str
        Algebraic coordinate

    Returns
    -------
    Pair
        Pair representation
    """
    return Pair(int(string[1])-1, Column[string[0]].value)

def in2D(data: Any, lst: list[list[Any]]) -> bool:
    for row in lst:
        if data in row:
            return True
        
    return False
 
# def main():
#     def __formatted_legal_moves(c: Chess, color: Color) -> str:
#         string = list()
#         legal = c.all_legal_moves(color)
#         for row in legal:
#             row_string = [f"{c.get_piece(row[0]).type.value}{row[0].__str__()}:"]
#             for col in row[1]:
#                 row_string.append(f"{c.get_piece(col) or ''}{col.__str__()}")
                
#             string.append(" ".join(row_string))
            
#         return "\n".join(string)
            
        
#     c = Chess()
#     print(c.board.__repr__())
#     print(c.castle_options())
#     # c.board.move(alg_to_pair("h7"), alg_to_pair("h6"))
#     # c.board.move(alg_to_pair("h8"), alg_to_pair("h7"))
#     # print(c.board.__repr__())
#     # print(c.castle_options())
    
#     c.set_FEN("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
    
#     # Show every piece and whether or not it has moved
#     for row in range(8):
#         for col in range(8):
#             piece = c.get_piece(Pair(row, col))
#             if piece:
#                 print(f"{piece} at {Pair(row, col).get_alg_coords()} has moved: {piece.has_moved}")
    
#     print(__formatted_legal_moves(c, Color.BLACK))
    
#     print(c.castle(alg_to_pair("e1"), alg_to_pair("a1")))
#     print(c.castle(alg_to_pair("e8"), alg_to_pair("h8")))
    
#     print(c.__repr__())

def main():
    x = Chess()
    y = Chess()
    
    x.set_FEN("rnbqkbnr/pp1ppppp/2p5/8/6Q1/4P3/PPPP1PPP/RNB1KBNR b KQkq - 0 1")
    
    print(x == y, x.board == y.board, x.board.board == y.board.board)
    print(x.board.EMPTY_BOARD)
    print()
    print(y.board.EMPTY_BOARD)
    

if __name__ == "__main__":
    main()
