# By Chris Parker
# Typing imports
from __future__ import annotations
from typing import List, Literal, Tuple

# Class imports
from abc import ABC, abstractmethod

# Chess Imports
from exceptions import InvalidFENError
from chess_enum import Color, Column, Type

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

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.get_alg_coords()
    
    def __repr__(self) -> str:
        return f"{self.y},{self.x}; {self.col}{self.row}"

    def __eq__(self, other: Pair) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __bool__(self) -> bool:
        return bool(self.x) or bool(self.y) # Only returns false if both are 0 or None

        
        

class Piece(ABC):
    """An abstract class representing a chess piece."""
    def __init__(self, color: Color, type: Type) -> None:
        self.color = color
        self.type = type
        self.has_moved = False

    def __eq__(self, __o: Piece) -> bool:
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
    def get_path(self, start: Pair, end: Pair) -> List[Pair]:
        pass

    @abstractmethod
    def clone(self):
        pass
    

class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, Type.PAWN)

    def is_valid_path(self, start: Pair, end: Pair) -> bool | Literal['c']:
        # Color determines direction
        if start.y == end.y: # Going straight

            if start.row + (2*self.color) == end.row: # Going 2 forward?
                if not self.has_moved: # First move?
                    return True
                else:
                    return False
            if start.row + self.color == end.row: # Going 1 forward
                return True # Always ok
            else: 
                return False
        elif ((start.y + 1 == end.y) or (start.y - 1 == end.y)) and (start.row + self.color == end.row): # Capture?
            return 'c' # Return c because this move is only valid if it is a capture
        else: # No valid options
            return False

    def get_path(self, start: Pair, end: Pair):
        path: List[Pair] = [] # List of coordinate the piece will move

        if start.y != end.y: # If the pawn is moving diagonally (capture)
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

    def is_valid_path(self, start: Pair, end: Pair):
        h = start.x == end.x
        v = start.y == end.y

        if h ^ v: # xor, checking if going horizontally and vertically or not moving
            return True
        else: # Must be going both or neither
            return False
    
    def get_path(self, start: Pair, end: Pair):
        path: List[Pair] = []
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

        for i in range(1, path_len): # Goes from 1 to length of path

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

    def clone(self):
        return Knight(self.color)


class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color, Type.BISHOP)

    def is_valid_path(self, start: Pair, end: Pair):
        return start.x-end.x == start.y - end.y and start != end

    def get_path(self, start: Pair, end: Pair):
        path: List[Pair] = []

        path_len = abs(start.x-end.x) # Length of the path

        # Finding x and y directions
        xDir = yDir = 1
        if start.x > end.x:
            xDir = -1
        if start.y > end.y:
            yDir = -1

        for i in range(1, path_len):
            path.append(Pair(start.y + i*yDir, start.x + i*xDir))

        return path

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

    # GLOBAL CLASS VARIABLES

    # Pieces 
    # White    
    wr, wn, wb = Rook(Color.WHITE), Knight(Color.WHITE), Bishop(Color.WHITE)
    wq, wk, wp = Queen(Color.WHITE), King(Color.WHITE), Pawn(Color.WHITE)

    # Black
    br, bn, bb = Rook(Color.BLACK), Knight(Color.BLACK), Bishop(Color.BLACK)
    bq, bk, bp = Queen(Color.BLACK), King(Color.BLACK), Pawn(Color.BLACK)
    
    # Origin (A1) is at 0,0 (top-left)
    DEFAULT_BOARD = tuple(tuple(Square(Pair(y, x), None) for x in range(8)) for y in range(8)) # Blank board
    DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" # FEN for default placement
    
    # CONSTRUCTOR
    def __init__(self) -> None:
        self.attacked_squares_w: List[Pair] = [] # Squares attacked by white
        self.attacked_squares_b: List[Pair] = [] # Squares attacked by black
        self.board: List[List[Square]] = list(self.DEFAULT_BOARD)
        
        self.reset_board()
        self.update_attacked_squares()

    # MOVEMENT METHODS
    def can_move(self, frm: Pair, to: Pair, *pseudoCap: Pair) -> Tuple[bool, Literal['c']| None]:
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
        sSquare = self.get_square(frm)
        fSquare = self.get_square(to)

        valid = sSquare.piece.is_valid_path(frm, to)

        if (sSquare.piece == None) or (not valid) or (valid == 'c' and fSquare.piece == None):
            # print(sSquare.piece, valid, fSquare.piece)
            return False, None

        if fSquare.piece != None and sSquare.piece.color == fSquare.piece.color:
            # print(2)
            return False, None

        path = sSquare.piece.get_path(frm, to)

        for i in range(len(path)):
            if i < len(path)-1:
                if self.get_square(path[i]).piece != None:
                    return False, None
            elif valid == 'c':
                if fSquare.coords in pseudoCap:
                    return True, 'c'
                elif fSquare.piece == None:
                    return False, None

        return True, ('c' if fSquare.piece != None else None)

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
            def _cull(list: List[Pair]):
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

        def _byPawn(square: Square) -> List[Pair]:
            return [
                Pair(square.coords.y + square.piece.color, square.coords.x-1),
                Pair(square.coords.y + square.piece.color, square.coords.x+1)
            ] # Pawns can only attack 2 squares
        
        def _byKing(square: Square) -> List[Pair]:
            return [
                Pair(square.coords.y-1, square.coords.x-1), Pair(square.coords.y+1, square.coords.x+1), 
                Pair(square.coords.y-1, square.coords.x+1), Pair(square.coords.y+1, square.coords.x-1), 
                Pair(square.coords.y, square.coords.x+1),   Pair(square.coords.y, square.coords.x-1),
                Pair(square.coords.y+1, square.coords.x),   Pair(square.coords.y-1, square.coords.x)
            ] # Returns all squares around king. Invalid squares are removed later

        def _byBishop(square: Square) -> List[Pair]:
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

        def _byRook(square: Square) -> List[Pair]:

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
            maxYPath = square.piece.get_path(square.coords, Pair(maxY, x))
            minYPath = square.piece.get_path(square.coords, Pair(0, x))

            maxXPath = square.piece.get_path(square.coords, Pair(y, maxX))
            minXPath = square.piece.get_path(square.coords, Pair(y, 0))

            # Return all 4 paths rook covers
            return _findStop(maxYPath) + _findStop(minYPath) + _findStop(maxXPath) + _findStop(minXPath)

        def _byQueen(square: Square) -> List[Pair]:
            # Queens have the movement of a bishop and rook combined 
            return _byBishop(square) + _byRook(square) 

        def _byKnight(square: Square) -> List[Pair]:
            y = square.coords.y
            x = square.coords.x
            return [Pair(y+2, x+1), Pair(y+2, x-1), Pair(y-2, x+1), Pair(y-2, x-1),
                    Pair(y+1, x+2), Pair(y+1, x-2), Pair(y-1, x+2), Pair(y-1, x-2)
            ] # Returns all squares around knight. Invalid squares are removed later
        
        # Clears old lists
        self.attacked_squares_w = []
        self.attacked_squares_b = []

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
        
        # Sort the lists with the y's and then the x's
        self.attacked_squares_w.sort(key = lambda l : (l.y, l.x))
        self.attacked_squares_b.sort(key = lambda l : (l.y, l.x))

        _cull_all() # Format the data    
    
    # ACCESSOR METHODS
    def get_square(self, squarePos: Pair) -> Square:
        return self.board[squarePos.y][squarePos.x]

    def get_king_position(self, color: Color) -> Pair:
        for rank in range(len(self.board)):
            for file in range(len(self.board[rank])):
                square = self.get_square(Pair(rank, file))
                if square.piece.type == Type.KING and square.piece.color == color:
                    return Pair(rank, file)
        
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

        assert len(compare_FEN) == len(compare_def)
        
        for row_i, (board_row, def_row) in enumerate(zip(reversed(compare_FEN), reversed(compare_def))):
            assert len(board_row) == len(def_row)
            for col_i, (board_char, def_char) in enumerate(zip(board_row, def_row)):
                if board_char != def_char:
                    if board_char != "#":
                        self.board[row_i][col_i].piece.has_moved = True

        self.update_attacked_squares()
            
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
        new_FEN = []
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

class Chess:
    """Play a game of chess."""

    def __init__(self) -> None:
        self.board = ChessBoard()
        self.white_cap: List[Piece] = [] # Captured white pieces
        self.black_cap: List[Piece] = [] # Captured black pieces
        self.en_pass: Square = None # En passant square
        self.white_turn = True # Who's turn
        self.half_move = 0 
        self.full_move = 1
        self.move_list: List[str] = [] # List of strings in form `e2e4` w/o piece symbols
        
        self.white_legal: List[str] = [] # Legal moves for white
        self.black_legal: List[str] = [] # Legal moves for black
        
        self.winner: None | Color = None
    
    def check_for_winner(self) -> None:
        pass
    
    def all_legal_moves(self) -> None:
        pass
    
    def move(self, frm: Pair, to: Pair) -> bool:
        """Move piece from a square to another if that move is valid. 
        NOTE: Automatically captures pieces.

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
        cap = None
        
        if self.board.can_move(frm, to, self.en_pass) and (bool(start.piece.color) == self.white_turn):
            cap = self.board.move(frm, to)
            
            if cap:
                if self.white_turn:
                    self.black_cap.append(cap)
                else:
                    self.white_cap.append(cap)
                    
        else:
            return False
        
        # Increment move counters after successful move
        if not self.white_turn:
            self.full_move += 1
            
        if not cap and start.piece.type != Type.PAWN:
            self.half_move += 1
        else:
            self.half_move = 0
        
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
                      self.en_pass.coords.get_alg_coords() if self.en_pass else "-", str(self.half_move), 
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
            self.en_pass = sects[3]
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
                
    @staticmethod
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
        return Pair(int(string[1])-1, Column[string[0]])
        
    
def main():
    c = Chess()
    print(c.board.__repr__())
    print(c.castle_options())
    # c.board.move(Chess.alg_to_pair("h7"), Chess.alg_to_pair("h6"))
    # c.board.move(Chess.alg_to_pair("h8"), Chess.alg_to_pair("h7"))
    # print(c.board.__repr__())
    # print(c.castle_options())
    
    c.set_FEN("r1bq1bnr/p2kp1pp/1pn2p2/2pp4/1P2P1P1/P1PP4/R3BP1P/1NBQK1NR b K - 0 1")
    
    # Show every piece and whether or not it has moved
    for row in range(8):
        for col in range(8):
            piece = c.get_piece(Pair(row, col))
            if piece:
                print(f"{piece} at {Pair(row, col).get_alg_coords()} has moved: {piece.has_moved}")
                
    print(c.get_FEN())
    

if __name__ == "__main__":
    main()
