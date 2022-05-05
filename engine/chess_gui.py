# By Chris Parker

### IMPORTS ###
from glob import glob
from time import perf_counter, sleep
import threading
import logging
from typing import Any
import yaml

from chess import Bishop, Knight, Pair, Piece, ChessBoard, Chess, Queen, Rook, alg_to_pair
from chess_enum import Type
from chess_enum import Color as PColor
from uciEngine import Stockfish

import pygame
from pygame.locals import (SRCALPHA, KEYDOWN, K_x, QUIT)

### CONSTANTS ### 
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (169,169,169)
DARK_GREY = (45, 45, 45)

RED = 0xff0000

SQR_WHITE = 0xf0d9b5
SQR_BLACK = 0xb58863

# Who's playing?
NO_ENGINE = 0
ONE_ENGINE = 1
TWO_ENGINE = 2


## CONFIGURABLE VARIABLES ##
# NOTE: These are the "true defaults". If a field is missing, these are the values it will have
CFG_PATH = "config.yaml"

# SCREEN #
# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

FPS = 144

# FILES #
PIECE_PATH = "pieces\\"
ENGINE_PATH = "stockfish_13.exe"

# GAME #
START_STATE = None
"""`None` == Default"""
GAME_MODE = ONE_ENGINE

# ENGINE #
ENGINE_WHITE = False # If the engine is playing white pieces
DEBUG = False
"""Engine debug mode enable"""
ENGINE_ARGS = tuple()
ENGINE_KWARGS = {"Threads" : 2, "Hash" : 512}
MAX_TIME = 1000 # ms

ENG_LOG = (DEBUG, "console.log")

### GLOBALS ###
paths = dict()
"""Stores the file paths for every piece"""

### LOGGING ###
logging.basicConfig(filename="gui.log", filemode="w", encoding="utf-8", level=logging.DEBUG)
logging.info("START LOG")

def read_cfg(cfg_path: str = CFG_PATH) -> None:
    logging.info("Reading config file: %s", cfg_path)
    cfg: dict[str, dict[str, Any]] = None
    
    try:
        with open(cfg_path, "r") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError:
        logging.error("Invalid config file format for %s", CFG_PATH)
    except FileNotFoundError:
        logging.error("Cannot find %s", CFG_PATH)
        
    if cfg:
        for sub in cfg.values():
            for key in sub:
                v = sub[key]
                logging.debug("Set `%s` to var `%s`", v, key)
                match key:
                    case "SCREEN_WIDTH":
                        global SCREEN_WIDTH
                        SCREEN_WIDTH = v
                    case "SCREEN_HEIGHT":
                        global SCREEN_HEIGHT
                        SCREEN_HEIGHT = v
                    case "FPS":
                        global FPS
                        FPS = v
                    case "PIECE_PATH":
                        global PIECE_PATH
                        PIECE_PATH = v
                    case "ENGINE_PATH":
                        global ENGINE_PATH
                        ENGINE_PATH = v
                    case "START_STATE":
                        global START_STATE
                        START_STATE = v
                    case "GAME_MODE":
                        global GAME_MODE
                        GAME_MODE = v
                    case "ENGINE_WHITE":
                        global ENGINE_WHITE
                        ENGINE_WHITE = v
                    case "DEBUG":
                        global DEBUG, ENG_LOG
                        DEBUG = v
                        ENG_LOG = (DEBUG, ENG_LOG[1])
                    case "MAX_TIME":
                        global MAX_TIME
                        MAX_TIME = v
                    case "ENGINE_ARGS":
                        global ENGINE_ARGS
                        ENGINE_ARGS = tuple(v)
                    case "ENGINE_KWARGS":
                        global ENGINE_KWARGS
                        ENGINE_KWARGS = v
                    case _:
                        logging.warning("%s not valid in %s", v, CFG_PATH)

    
### HELPER FUNCTIONS ###
def average_rgb(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> tuple[int, int, int]:
    """Get the average of to RGB values.""" 
    rtn = list()
    for i, (val1, val2) in enumerate(tuple(zip(c1, c2))):
        rtn.append((val1 + val2) // 2)
        
    return tuple(rtn)

def tint_rgb(c: tuple[int, int, int], offset: int) -> tuple[int, int, int]:
    """Add a tint to the color (make it darker)."""
    rtn = list()
    for i, val in enumerate(c):
        rtn.append(val + offset)
        
    return tuple(rtn)

def std_to_pair(coord: tuple[int, int]) -> Pair:
    """Convert standard (x,y) coordinate tuples to Pair.
    NOTE: Std coordinates go from the top-left to bottom-right

    Parameters
    ----------
    coord : tuple[int, int]
        Standard coordinate to convert

    Returns
    -------
    Pair
        Pair representation
    """
    return Pair(7-coord[1], coord[0])

def pair_to_std(coord: Pair) -> tuple[int, int]:
    """Convert a Pair to standard coordinates (x,y).
    NOTE: Pair goes from the bottom-left to the top-right

    Parameters
    ----------
    coord : Pair
        Pair to convert

    Returns
    -------
    tuple[int, int]
        Standard coordinate
    """
    return (coord.x, 7- coord.y)

### BOARD ###
class GBoard(pygame.sprite.Sprite):
    """The sprite that displays the board, including the squares, and saves the
    locations of each square.
    """
    def __init__(self):
        super().__init__()
        
        self.side_len = 0
        if SCREEN_WIDTH > SCREEN_HEIGHT:
            self.side_len = SCREEN_HEIGHT * .9
        else:
            self.side_len = SCREEN_WIDTH * .75
            
        self.square_len = int(self.side_len // 8)
        self.side_len = self.square_len * 8
            
        self.surf = pygame.Surface((self.side_len, self.side_len))
        self.rect = self.surf.get_rect()
        
        self.draw_squares()
        
        # 8x8 2D array w/ coordinate tuples (x, y)
        self.centers: list[list[tuple[int, int]]] = [[None for _ in range(8)] for _ in range(8)]
        
        self.__populate_centers()

    def __populate_centers(self):
        """Fill the values of `self.centers`."""
        for row in range(len(self.centers)):
            for col in range(len(self.centers[0])):
                self.centers[row][col] = (row * self.square_len + self.square_len // 2, 
                                           col * self.square_len + self.square_len // 2
                                           )

    def draw_squares(self):
        """Draw the squares onto the board surface."""
        for row in range(8):
            for col in range(8):
                color = None
                if (row+col) % 2 == 0:
                    color = SQR_WHITE
                else:
                    color = SQR_BLACK
                
                pygame.draw.rect(
                    self.surf, 
                    color, 
                    pygame.Rect(row*self.square_len, col*self.square_len, self.square_len, self.square_len)
                )

    def get_square(self, coord: tuple[int, int]) -> tuple[int, int] | None:
        """Return the square at this coordinate.

        Parameters
        ----------
        coord : tuple[int, int]
            Standard screen coordinate

        Returns
        -------
        tuple[int, int] | None
            Standard board coordinate or `None` if the square is off the board
        """
        row = coord[0] // self.square_len
        col = coord[1] // self.square_len
        
        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return None
        else:
            return (row, col)
        
    def get_center(self, coord: tuple[int, int]) -> tuple[int, int]:
        """Return the center of the given standard board coordinate.

        Parameters
        ----------
        coord : tuple[int, int]
            Board coordinate

        Returns
        -------
        tuple[int, int]
            Screen coordinate
        """
        return self.centers[coord[0]][coord[1]]

class Info(pygame.sprite.Sprite):
    """Displays important information about the game and the connected interface."""
    def __init__(self) -> None:
        super().__init__()
        
        self.side_len = 0
        if SCREEN_WIDTH > SCREEN_HEIGHT:
            self.side_len = SCREEN_HEIGHT * .9
        else:
            self.side_len = SCREEN_WIDTH * .2
            
        self.surf = pygame.Surface((self.side_len, self.side_len))
        self.rect = self.surf.get_rect()

class PromoteChoice(pygame.sprite.Sprite):
    """Window to display what a pawn should be promoted to"""
    def __init__(self, square_len: int, visible=False) -> None:    
        self.square_len = square_len
        self.border_width = square_len // 6
        self.width = square_len * 4 + self.border_width
        self.height = square_len + self.border_width
        
        self.visible = visible
        
        self.surf = pygame.surface.Surface((self.width, self.height))
        self.rect = self.surf.get_rect()
        
        int_rect = pygame.Rect(0, 0, self.width - self.border_width, self.height - self.border_width)
        int_rect.center = self.rect.center
        
        # Background
        pygame.draw.rect(self.surf, BLACK, self.rect)
        
        # Foreground 
        pygame.draw.rect(self.surf, DARK_GREY, int_rect, border_radius=5)
                
        self.piece_color = PColor.WHITE
        self.pieces: list[GPiece] = [None] * 4

    def __draw_pieces(self) -> None:
        """Make new pieces of the right color."""
        self.pieces[0] = GPiece(paths[Queen(self.piece_color)], self.square_len)
        self.pieces[1] = GPiece(paths[Rook(self.piece_color)], self.square_len)
        self.pieces[2] = GPiece(paths[Bishop(self.piece_color)], self.square_len)
        self.pieces[3] = GPiece(paths[Knight(self.piece_color)], self.square_len)

    def display_at(self, pos: tuple[int, int], color: PColor=PColor.WHITE):
        """Move the rect to the given position and set the sprite as visible.

        Parameters
        ----------
        pos : tuple[int, int]
            Screen postion to set the center of the window.
        color : PColor, optional
            Color of the pieces, by default PColor.WHITE
        """
        self.piece_color = color
        self.rect.center = pos
        
        self.__draw_pieces()
        self.visible = True

    def get_piece(self, pos: tuple[int, int]) -> Type | None:
        """Return the piece at the given screen position.

        Parameters
        ----------
        pos : tuple[int, int]
            Screen postion

        Returns
        -------
        Type | None
            Type of the piece (if it is in the window)
        """
        x = pos[0]
        y = pos[1]
    
        queen_left = self.rect.left + self.border_width
        queen_right = queen_left + self.square_len
        
        rook_left = queen_right
        rook_right = rook_left + self.square_len
        
        bishop_left = rook_right
        bishop_right = bishop_left + self.square_len
        
        knight_left = bishop_right
        knight_right = knight_left + self.square_len
        
        if y > self.rect.top + self.border_width and y < self.rect.bottom - self.border_width:
            if x > queen_left and x < queen_right:
                return Type.QUEEN
            if x > rook_left and x < rook_right:
                return Type.ROOK
            if x > bishop_left and x < bishop_right:
                return Type.BISHOP
            if x > knight_left and x < knight_right:
                return Type.KNIGHT
            
        return None

    def collidepoint(self, x_y: tuple[int, int]) -> bool:
        """Return True if the given position is in the window.

        Parameters
        ----------
        x_y : tuple[int, int]
            Screen coordinates

        Returns
        -------
        bool
            True if the given position is in the window, else False
        """
        return self.rect.collidepoint(x_y)

    def draw(self, surf: pygame.surface.Surface) -> None:
        """Draws the window and pieces onto a given surface.
        
        Parameters
        ----------
        surf : Surface
            Surface to draw to.
        """
        surf.blit(self.surf, self.rect)
        
        for i, piece in enumerate(self.pieces):
            piece.rect.centery = self.rect.centery
            piece.rect.left = self.rect.left + self.border_width + i * self.square_len
            
            surf.blit(piece.surf, piece.rect)

class GPiece(pygame.sprite.Sprite):
    """Individual piece sprite."""
    def __init__(self, file_name: str, size: int) -> None:
        super().__init__()
        self.img_path = file_name
        self.size = size
        if file_name:
            self.surf = pygame.image.load(file_name)
            self.surf = pygame.transform.scale(self.surf, (size, size))
            self.rect = self.surf.get_rect()

    def collidepoint(self, x_y: list[int, int]) -> bool:
        """Return True if the given position is on the piece.

        Parameters
        ----------
        x_y : tuple[int, int]
            Screen coordinates

        Returns
        -------
        bool
            True if the given position is on the piece, else False
        """
        return self.rect.collidepoint(x_y)

    def copy(self) -> 'GPiece':
        """Return a copy of the piece.

        Returns
        -------
        GPiece
            Copy of piece
        """
        return GPiece(self.img_path, self.size)
    
    def __bool__(self) -> bool:
        return True if (self.img_path and self.size > 0) else False

class CircleMarker(pygame.sprite.Sprite):
    """Translucent circle to use as a marker."""
    def __init__(self, radius: float, color: int | tuple[int, int, int, int]) -> None:
        super().__init__()
        
        self.radius = radius
        
        self.surf = pygame.Surface((radius*2, radius*2), SRCALPHA, 32)
        self.rect = self.surf.get_rect()
        
        pygame.draw.circle(self.surf, color, self.rect.center, radius)
        
        self.visible = False

class GameLoop:
    """Main game loop."""
    def __init__(self):
        # Initialize engine, needs more time than PyGame
        self.engine = Stockfish(ENGINE_PATH, *ENGINE_ARGS, **ENGINE_KWARGS)
        logging.info("Starting engine at path %s with settings %s \n %s", ENGINE_PATH, ENGINE_ARGS, ENGINE_KWARGS)
        
        # Initialize pygame
        pygame.init()
        
        # Create the screen object
        # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Board sprite
        self.board = GBoard()
        self.BOARD_POS = (int(SCREEN_WIDTH * .05), int(SCREEN_HEIGHT * .05))
        
        self.game = Chess(False)
        self.raw_board = self.game.board.board
        
        # Pieces 
        self.white_list: list[GPiece] = list()
        self.black_list: list[GPiece] = list()
        self.pieces: pygame.sprite.LayeredUpdates = None
        
        # Set the pieces
        if START_STATE:
            logging.debug("Setting FEN:%s", START_STATE)
            self.game.set_FEN(START_STATE)
        self.draw_pieces()            
        
        # All the move markers
        self.possible_move_list: list[CircleMarker] = list()
        for row in range(8):
            for col in range(8):
                mark = CircleMarker((self.board.square_len / 2) / 4, (0, 0, 200, 100))
                mark.rect.center = self.board_to_main(self.board.get_center((col, row)))
                self.possible_move_list.append(mark)
        
        self.possible_moves = pygame.sprite.LayeredUpdates(self.possible_move_list)
        
        # Piece dragging
        self.dragged_piece: GPiece = GPiece(None, 0)
        self.dragged_last = (0, 0)
        self.piece_draging = False
        
        # Variable to keep the main loop running
        self.running = True
        self.clock = pygame.time.Clock()
        
        ## Multithread Vars ##
        self.__threads: list[threading.Thread] = list()
        
        # Checkmate & stalemate for threading
        self.checkmate = None
        self.stalemate = False
        
        # Can the two players move
        self.human_turn = True if not ENGINE_WHITE and (GAME_MODE != TWO_ENGINE) else False
        self.cpu_turn = None
        if GAME_MODE == TWO_ENGINE: 
            self.cpu_turn = True
        
        self.update = True
        self.start_game_state_thread()
        
        # Promotion window
        self.promote_win: PromoteChoice = PromoteChoice(self.board.square_len*1.5)
        self.promotion: tuple[int, int] = None # Square to promote
        
        # for row in self.board.centers:
        #     print(row)
        # Debug
        self.marker = CircleMarker((self.board.square_len / 2) / 3, (225, 0, 0, 125))
        
        if DEBUG:
            self.engine.debug()

    def start(self) -> bool:
        """Start a new game."""
        logging.info("Game start")
        self.engine.new_game()
        sleep(0.1)
        
        # Main loop
        while self.running:
            self.clock.tick(FPS)
            if GAME_MODE == ONE_ENGINE:
                if ENGINE_WHITE == self.game.white_turn and self.cpu_turn:
                    self.cpu_turn = False
                    self.human_turn = False
                    self.engine_turn()
            if GAME_MODE == TWO_ENGINE:
                if self.cpu_turn:
                    self.engine_turn()
                
            # for loop through the event queue
            for event in pygame.event.get():
                # Check for KEYDOWN event
                if event.type == KEYDOWN:
                    # If the Esc key is pressed, then exit the main loop
                    if event.key == K_x:
                        print("WHITE CAP:", self.game.white_cap)
                        print("BLACK CAP:", self.game.black_cap)
                        
                # CLICK AND DRAG #
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left-click
                        if self.human_turn:
                            self.pickup_piece(event)

                elif event.type == pygame.MOUSEBUTTONUP:                    
                    if event.button == 1:    
                        if self.piece_draging == True: # Only do something if a piece is being dragged
                            if self.board.rect.collidepoint(self.main_to_board(event.pos)):
                                self.drop_piece(event)
                                self.update = True
                            else:
                                self.reset_dragged() # Can't place here, reset
                        elif self.promote_win.visible and self.promote_win.collidepoint(event.pos):
                            promote = self.promote_win.get_piece(event.pos)
                            self.promote_win.visible = False
                            
                            self.game.promote(std_to_pair(self.promotion), prm_type=promote)
                            self.draw_pieces() # Redraw
                            
                        self.piece_draging = False # Done dragging

                elif event.type == pygame.MOUSEMOTION:
                    self.drag_piece(event)
                # Check for QUIT event. If QUIT, then close
                elif event.type == QUIT:
                    self.close()
            
            # Get all the keys currently pressed
            # pressed_keys = pygame.key.get_pressed()
            
            # Fill the screen with bg color
            self.screen.fill(DARK_GREY)

            # Draw board
            self.screen.blit(self.board.surf, self.BOARD_POS)
            
            # Promotion window
            if self.promote_win.visible:
                self.promote_win.draw(self.screen)
            
            # Draw all sprites
            for piece in self.pieces:
                self.screen.blit(piece.surf, piece.rect)
            for move in self.possible_moves:
                if move.visible:
                    self.screen.blit(move.surf, move.rect)
                
            if self.checkmate:
                self.update = False
                self.human_turn = False
                self.cpu_turn = False
                print("WHITE" if self.checkmate == 1 else "BLACK", "IN CHECKMATE")
                #self.close()
                
            if self.stalemate:
                self.update = False
                self.human_turn = False
                self.cpu_turn = False
                print("STALEMATE")
                #self.close()
                
            # Draw debug tools
            if self.marker.visible:
                self.screen.blit(self.marker.surf, self.marker.rect)
            
            # Update the display
            pygame.display.flip()

    def draw_move_markers(self, square: tuple[int, int]) -> None:
        """Draw circle markers for each possible move (of one piece).

        Parameters
        ----------
        square : tuple[int, int]
            Standard board coordinate to check
        """ 
        clr = self.game.get_piece(std_to_pair(square)).color
        
        if ((clr == PColor.WHITE and self.game.white_turn) 
            or (clr == PColor.BLACK and not self.game.white_turn)): # Correct turn
            
            moves = self.game.legal_moves(std_to_pair(square))
            for move in moves: # Draw legal moves
                move_sqr = pair_to_std(move)
                self.possible_moves.get_sprites_at(self.board_to_main(self.board.get_center(move_sqr)))[0].visible=True

    def clear_move_markers(self) -> None:
        """Hide every possible move marker."""
        for mark in self.possible_moves:
            mark.visible = False

    def draw_pieces(self) -> None:
        """Draw every piece on the GBoard."""
        # Draw the initial pieces
        self.white_list.clear()
        self.black_list.clear()
        if len(paths) > 0:
            for y, row in enumerate(self.raw_board):
                for x, sqr in enumerate(row):
                    p = sqr.piece
                    if p:
                        gp = GPiece(paths[p], self.board.square_len)
                        gp.rect.center = self.board_to_main(self.board.centers[x][7-y])
                        if p.color == PColor.BLACK:
                            self.black_list.append(gp)
                        else:
                            self.white_list.append(gp)

            self.pieces = pygame.sprite.LayeredUpdates(self.white_list, self.black_list)
        else: # If this is the first call to this function, make our life easier in the future
            new_board = ChessBoard()
            for y, row in enumerate(new_board.board):
                for x, sqr in enumerate(row):
                    p = sqr.piece
                    if p:
                        path = [PIECE_PATH]
                        if p.color == PColor.BLACK:
                            path.append("_b_")
                        else:
                            path.append("_w_")
                        
                        path += [p.type.value.lower(), ".png"]
                        paths[p] = "".join(path)
            
            self.draw_pieces()

    def drop_piece(self, event: pygame.event.Event) -> None:
        """Drop the piece given an event.

        Parameters
        ----------
        event : pygame.event.Event
            Event object
        """
        to_sqr = self.board.get_square(self.main_to_board(event.pos))
        coord = self.board_to_main(self.board.get_center(to_sqr))
        
        self.marker.rect.center = self.board_to_main(self.board.get_center(self.dragged_last))
        self.dragged_piece.rect.center = coord # Snap to center of containing square
        
        frm = std_to_pair(self.dragged_last)
        to = std_to_pair(to_sqr)
        
        org_p = self.game.get_piece(frm)
        
        print(frm, to)
        move = self.game.move(frm, to, auto_promote=False)
        if move:
            print(move)
            s = self.pieces.get_sprites_at(event.pos)
            if len(s) > 1:
                self.pieces.remove(s[0])
            else:
                if self.game.en_pass_capture:
                    to_std = pair_to_std(self.game.en_pass_capture)
                    spt = self.get_sprites_at(to_std)
                    self.pieces.remove(spt)
            
            p = self.game.get_piece(to)
            
            # Error or castling
            if not p or (
                org_p.type == Type.KING and to_sqr in ((0,0), (2,0), (6,0), (7,0), (0,7), (2,7), (6,7), (7,7))
                ):
                self.draw_pieces() 
                
            if (to_sqr[1] == 0 or to_sqr[1] == 7) and p and p.type == Type.PAWN:
                self.promotion = to_sqr
                pos = ((self.BOARD_POS[0] + self.board.side_len) / 2, (self.BOARD_POS[1] + self.board.side_len) / 2)
                self.promote_win.display_at(
                    pos, color = self.game.get_piece(to).color
                    )
            
            if GAME_MODE == ONE_ENGINE:
                self.human_turn = False
            self.marker.visible = True
            
            if GAME_MODE == ONE_ENGINE:
                self.cpu_turn = True
        else:
            self.reset_dragged() # If nothing works, reset the piece
            
        self.clear_move_markers()

    def pickup_piece(self, event: pygame.event.Event) -> None:
        """Start dragging the piece given an event.

        Parameters
        ----------
        event : pygame.event.Event
            Event object
        """
        s = self.pieces.get_sprites_at(event.pos) # Get the sprite 
        self.dragged_piece = s[-1] if len(s) > 0 else None # Only get top if there is a sprite
        
        if self.dragged_piece: # if this actually did anything
            self.dragged_last = self.board.get_square(self.main_to_board(event.pos)) # Save position
            self.draw_move_markers(self.dragged_last)
            self.pieces.move_to_front(self.dragged_piece) # Should be at top
            self.piece_draging = True
            
            mouse_x, mouse_y = event.pos
            # Set an offset so the piece doesn't snap to center of mouse
            self.offset_x = self.dragged_piece.rect.x - mouse_x 
            self.offset_y = self.dragged_piece.rect.y - mouse_y

    def drag_piece(self, event: pygame.event.Event) -> None:
        """Move the piece with the mouse (when dragged).

        Parameters
        ----------
        event : pygame.event.Event
            Event object
        """
        if self.piece_draging: # Move the current piece if we have one
            mouse_x, mouse_y = event.pos
            self.dragged_piece.rect.x = mouse_x + self.offset_x
            self.dragged_piece.rect.y = mouse_y + self.offset_y

    ### ENGINE FUNCTIONS ###

    def move_piece(self, frm: tuple[int, int], to: tuple[int, int]) -> None:
        """Move a piece from a square to another without dragging.

        Parameters
        ----------
        frm : tuple[int, int]
            From square position
        to : tuple[int, int]
            To square position
        """
        frm_pair = std_to_pair(frm)
        to_pair = std_to_pair(to)
        
        org_p = self.game.get_piece(frm_pair)
        
        #print(frm_pair, to_pair)
        move = self.game.move(frm_pair, to_pair, auto_promote=False)
        #print(move)
        logging.info("%s%s, %s", frm_pair, to_pair, move)
        if move:
            to_pos = self.board_to_main(self.board.get_center(to))
            s = self.get_sprites_at(to)
            piece = self.get_sprites_at(frm)[0]
            
            self.pieces.remove(s)
            
            piece.rect.center = to_pos
            
            # Error or castling
            if not self.game.get_piece(to_pair) or (
                org_p.type == Type.KING and to in ((0,0), (2,0), (6,0), (7,0), (0,7), (2,7), (6,7), (7,7))
                ):
                self.draw_pieces()
            
            self.marker.rect.center = self.board_to_main(self.board.get_center(frm))
            self.marker.visible = True

    def __engine_turn(self) -> None:
        """Have the engine make a move."""
        self.engine.send_command("position fen " + self.game.get_FEN())
        self.engine.go(movetime = MAX_TIME)
        sleep(MAX_TIME / 1000) # Wait move time
        
        # Wait until the move has been received
        read = True
        while read:
            self.engine._read_lines()
            move_str = self.engine.outLog[-1].split()
            if move_str[0] == "bestmove" and move_str[1] != "(none)":
                start = pair_to_std(alg_to_pair(move_str[1][0:2]))
                end = pair_to_std(alg_to_pair(move_str[1][2:4]))
                self.move_piece(start, end)
                
                if len(move_str[1]) > 4:
                    self.game.promote(std_to_pair(end), Type(move_str[1][4].upper()))
                    logging.info("Promotion to %s by engine", move_str[1][4])
                    self.draw_pieces()
                    
                read = False
            elif move_str[1] == "(none)":
                logging.warning("Nullmove received")
                read = False
            else:
                read = True
                
        if GAME_MODE == ONE_ENGINE:
            self.human_turn = True
        self.update = True
                
        for thread in self.__threads:
            if thread.name == "engine":
                self.__threads.remove(thread)
                break # Deg tears :'(

    def pause(self) -> None:
        """Stop piece movement w/o freezing window."""
        self.human_turn = False
        self.cpu_turn = False
        
    def pause_all(self) -> None:
        """Stop piece movement and threads updating."""
        self.pause()
        self.update = False
        
    def unpause(self) -> None:
        """Reverse action of pause function."""
        self.update = True
        self.human_turn = self.game.white_turn != ENGINE_WHITE
        self.cpu_turn = not self.human_turn

    def get_sprites_at(self, square: tuple[int, int]) -> list[pygame.sprite.Sprite]:
        """Get the sprite at a square."""
        return self.pieces.get_sprites_at(self.board_to_main(self.board.get_center(square)))

    def main_to_board(self, coord: tuple[int, int]):
        """Convert the coordinates received from the board to the coordinates of the main window."""
        return (coord[0] - self.BOARD_POS[0], coord[1] - self.BOARD_POS[1])

    def board_to_main(self, coord: tuple[int, int]):
        """Convert the coordinates main window to the coordinates of the board."""
        return (coord[0] + self.BOARD_POS[0], coord[1] + self.BOARD_POS[1])

    def reset_dragged(self):
        """Move dragged piece back to its original square."""
        self.dragged_piece.rect.center = self.board_to_main(self.board.get_center(self.dragged_last))
        print("CAN'T PLACE HERE!!!")

    ### Threading ###
    def __check_checkmate_stale(self):
        """Check if the game is in stalemate or someone has won.
        NOTE: DO NOT RUN IN MAIN!!
        """
        # TODO: Add Locks to these variables
        while self.running:
            if self.update:
                copy = self.game.bare_copy()
                copy.update_all_legal()
                if copy.in_checkmate(PColor.WHITE):
                    self.checkmate = PColor.WHITE
                elif copy.in_checkmate(PColor.BLACK):
                    self.checkmate = PColor.BLACK
                elif copy.in_stalemate():
                    self.stalemate = True
                    
                sleep(0.01)
                
                self.update = False

    def start_game_state_thread(self):
        """Check if the game is in stalemate or someone has won.
        NOTE: Starts another thread
        """
        self.__threads.append(
            threading.Thread(
                target=self.__check_checkmate_stale,
                name="check-stale",
                daemon=True)
            )
        self.__threads[-1].start()

    def engine_turn(self):
        """Have the engine make a move."""
        self.__threads.append(
            threading.Thread(
                target=self.__engine_turn,
                name="engine",
                daemon=True
            )
        )
        self.__threads[-1].start()

    ### END ###

    def close(self) -> None:
        """Close everything and do cleanup"""
        logging.info("Closing game")
        if ENG_LOG[0]:
            self.engine.close(ENG_LOG[1])
        
        for thread in self.__threads:
            logging.info("Closing: %s", thread.name)
            thread.join(0.5)
        
        self.running = False


def main():
    """Run everything"""
    cont = True
    while cont:
        read_cfg()
        game = GameLoop()
        cont = game.start()
        game = None
        sleep(0.1)


if __name__ == "__main__":
    main()
