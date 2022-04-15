# By Chris Parker
"""IMPORTS"""
from time import perf_counter, sleep
import threading

from chess import Pair, Piece, ChessBoard, Chess, alg_to_pair
from chess_enum import Type
from uciEngine import Stockfish

import pygame
from pygame.locals import (SRCALPHA, KEYDOWN, K_x, QUIT)
    
"""CONSTANTS"""    
# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

FPS = 144

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (169,169,169)
DARK_GREY = (45, 45, 45)

RED = 0xff0000

SQR_WHITE = 0xf0d9b5
SQR_BLACK = 0xb58863

START_STATE = None #"r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"

# Engine vars
ENGINE_WHITE = False # If the engine is playing white pieces
DEBUG = True
ENGINE_PATH = "stockfish_13.exe"
ENGINE_ARGS = ("UCI_LimitStrength",)
ENGINE_KWARGS = {"UCI_Elo" : 200, 
                 "Threads" : 4, 
                 "Hash" : 1024
                }
MAX_TIME = 1000 # ms

LOG = (True, "log.txt")

"""HELPER FUNCTIONS"""
def average_rgb(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> tuple[int, int, int]: 
    rtn = [None, None, None]
    for i, (val1, val2) in enumerate(tuple(zip(c1, c2))):
        rtn[i] = (val1 + val2) // 2
        
    return tuple(rtn)

def tint_rgb(c: tuple[int, int, int], offset: int) -> tuple[int, int, int]:
    rtn = [None, None, None]
    for i, val in enumerate(c):
        rtn[i] = val + offset
        
    return tuple(rtn)

def std_to_pair(coord: tuple[int, int]) -> Pair:
    return Pair(7-coord[1], coord[0])

def pair_to_std(coord: Pair) -> tuple[int, int]:
    return (coord.x, 7- coord.y)

"""BOARD"""
class GBoard(pygame.sprite.Sprite):
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
        for row in range(8):
            for col in range(8):
                self.centers[row][col] = (row * self.square_len + self.square_len // 2, 
                                           col * self.square_len + self.square_len // 2
                                           )
        
    def draw_squares(self):
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
        row = coord[0] // self.square_len
        col = coord[1] // self.square_len
        
        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return None
        else:
            return (row, col)
        
    def get_center(self, coord: tuple[int, int]) -> tuple[int, int]:
        return self.centers[coord[0]][coord[1]]

class Info(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        
        self.side_len = 0
        if SCREEN_WIDTH > SCREEN_HEIGHT:
            self.side_len = SCREEN_HEIGHT * .9
        else:
            self.side_len = SCREEN_WIDTH * .2
            
        self.surf = pygame.Surface((self.side_len, self.side_len))
        self.rect = self.surf.get_rect()
        

class GPiece(pygame.sprite.Sprite):
    def __init__(self, file_name: str, size: int) -> None:
        super().__init__()
        self.img_path = file_name
        self.size = size
        if file_name:
            self.surf = pygame.image.load(file_name)
            self.surf = pygame.transform.scale(self.surf, (size, size))
            self.rect = self.surf.get_rect()
        
    def collidepoint(self, x_y: list[int, int]) -> bool:
        return self.rect.collidepoint(x_y)
    
    def copy(self) -> 'GPiece':
        return GPiece(self.img_path, self.size)
    
    def __bool__(self) -> bool:
        return True if (self.img_path and self.size > 0) else False
    
class CircleMarker(pygame.sprite.Sprite):
    def __init__(self, radius: float, color: int | tuple[int, int, int, int]) -> None:
        super().__init__()
        
        self.radius = radius
        
        self.surf = pygame.Surface((radius*2, radius*2), SRCALPHA, 32)
        self.rect = self.surf.get_rect()
        
        pygame.draw.circle(self.surf, color, self.rect.center, radius)
        
        self.visible = False
  
class GameLoop:
    def __init__(self):
        # Initialize engine, needs more time than PyGame
        self.engine = Stockfish(ENGINE_PATH, *ENGINE_ARGS, **ENGINE_KWARGS)
        
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
        
        # Checkmate & stalemate for threading
        self.checkmate = None
        self.stalemate = False
        
        self.update = True
        self.start_game_state_thread()
        
        # for row in self.board.centers:
        #     print(row)
        # Debug
        # self.marker = CircleMarker((self.board.square_len / 2) * 0.5, (225, 0, 0, 155))
        
    def start(self):
        self.engine.new_game()
        
        # Main loop
        while self.running:
            self.clock.tick(FPS)
            if ENGINE_WHITE == self.game.white_turn:
                self.engine_turn()
                
            # for loop through the event queue
            for event in pygame.event.get():
                # Check for KEYDOWN event
                if event.type == KEYDOWN:
                    # If the Esc key is pressed, then exit the main loop
                    if event.key == K_x:
                        print(self.game.white_cap)
                        print(self.game.black_cap)
                        
                # CLICK AND DRAG #
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left-click
                        self.pickup_piece(event)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:    
                        if self.piece_draging == True: # Only do something if a piece is being dragged
                            if self.board.rect.collidepoint(self.main_to_board(event.pos)):
                                self.drop_piece(event)
                                self.update = True
                            else:
                                self.reset_dragged() # Can't place here, reset
                            
                        self.piece_draging = False # Done dragging

                elif event.type == pygame.MOUSEMOTION:
                    self.drag_piece(event)
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    if LOG[0]:
                        self.engine.close(LOG[1])
                    self.running = False 
            
            # Get all the keys currently pressed
            pressed_keys = pygame.key.get_pressed()
            
            # Fill the screen with bg color
            self.screen.fill(DARK_GREY)

            # Draw board
            self.screen.blit(self.board.surf, self.BOARD_POS)
            
            # Draw all sprites
            for piece in self.pieces:
                self.screen.blit(piece.surf, piece.rect)
            for move in self.possible_moves:
                if move.visible:
                    self.screen.blit(move.surf, move.rect)
                
            if self.checkmate:
                print("WHITE" if self.checkmate == 1 else "BLACK", "IN CHECKMATE")
                self.running = False
                
            if self.stalemate:
                print("STALEMATE")
                self.running = False
                
            # Draw debug tools
            # if self.marker.visible:
            #     self.screen.blit(self.marker.surf, self.marker.rect)
            
            # Update the display
            pygame.display.flip()
            
    def draw_move_markers(self, square: tuple[int, int]):
        clr = self.game.get_piece(std_to_pair(square)).color
        
        if (clr == 1 and self.game.white_turn) or (clr == -1 and not self.game.white_turn): # Correct turn
            moves = self.game.legal_moves(std_to_pair(square))
            for move in moves: # Draw legal moves
                move_sqr = pair_to_std(move)
                self.possible_moves.get_sprites_at(self.board_to_main(self.board.get_center(move_sqr)))[0].visible= True
            
    def clear_move_markers(self):
        for mark in self.possible_moves:
            mark.visible = False
            
    def draw_pieces(self):
        # Draw the initial pieces
        self.white_list.clear()
        self.black_list.clear()
        for y, row in enumerate(self.raw_board):
            for x, sqr in enumerate(row):
                p = sqr.piece
                if p:
                    if p.color == -1:
                        gp = GPiece("pieces\\_b_"+p.type.value.lower()+".png", self.board.square_len)
                        gp.rect.center = self.board_to_main(self.board.centers[x][7-y])
                        self.black_list.append(gp)
                    else:
                        gp = GPiece("pieces\\_w_"+p.type.value.lower()+".png", self.board.square_len)
                        gp.rect.center = self.board_to_main(self.board.centers[x][7-y])
                        self.white_list.append(gp)
        
        self.pieces = pygame.sprite.LayeredUpdates(self.white_list, self.black_list)
                        
    def drop_piece(self, event: pygame.event.Event):
        to_sqr = self.board.get_square(self.main_to_board(event.pos))
        coord = self.board_to_main(self.board.get_center(to_sqr))

        # self.marker.rect.center = coord
        # self.marker.visible = True
        
        self.dragged_piece.rect.center = coord # Snap to center of containing square
        
        frm = std_to_pair(self.dragged_last)
        to = std_to_pair(to_sqr)
        
        print(frm, to)
        move = self.game.move(frm, to)
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
            
            # Error or castling
            if self.game.get_piece(to) == None:
                self.draw_pieces()
                
        else:
            self.reset_dragged()
            
        self.clear_move_markers()
            
    def pickup_piece(self, event: pygame.event.Event):
        s = self.pieces.get_sprites_at(event.pos) # Get the sprite 
        self.dragged_piece = s[-1] if len(s) > 0 else None # Only get top if there is a sprite
        
        if self.dragged_piece: # if this actually did anything
            self.dragged_last = self.board.get_square(self.main_to_board(event.pos)) # Save position
            self.draw_move_markers(self.dragged_last)
            self.pieces.move_to_front(self.dragged_piece) # Should be at top
            self.piece_draging = True
            
            mouse_x, mouse_y = event.pos
            self.offset_x = self.dragged_piece.rect.x - mouse_x
            self.offset_y = self.dragged_piece.rect.y - mouse_y
            
    def drag_piece(self, event: pygame.event.Event):
        if self.piece_draging: # Move the current piece if we have one
            mouse_x, mouse_y = event.pos
            self.dragged_piece.rect.x = mouse_x + self.offset_x
            self.dragged_piece.rect.y = mouse_y + self.offset_y
            
    """ENGINE FUNCTIONS"""
            
    def move_piece(self, frm: tuple[int, int], to: tuple[int, int]):
        frm_pair = std_to_pair(frm)
        to_pair = std_to_pair(to)
        
        print(frm_pair, to_pair)
        move = self.game.move(frm_pair, to_pair)
        if move:
            print(move)
            to_pos = self.board_to_main(self.board.get_center(to))
            s = self.get_sprites_at(to)
            piece = self.get_sprites_at(frm)[0]
            
            self.pieces.remove(s)
            
            piece.rect.center = to_pos
            
            # Error or castling
            if self.game.get_piece(to_pair) == None:
                self.draw_pieces()
                print("REDRAW")
        else:
            print(move)
            
    def engine_turn(self) -> None:
        self.__send_pos()
        self.__start_search(MAX_TIME)
        sleep(MAX_TIME / 1000 + 0.01)
        self.engine.send_command("stop")
        sleep(0.001)
        self.engine._read_lines()
        move_str = self.engine.outLog[-1].split()
        if move_str[0] == "bestmove":
            start = pair_to_std(alg_to_pair(move_str[1][0:2]))
            end = pair_to_std(alg_to_pair(move_str[1][2:4]))
            self.move_piece(start, end)
        else:
            print(move_str[0])
            print("INVALID MOVE")
            
    def __send_pos(self) -> None:
        self.engine.send_command("position fen " + self.game.get_FEN())
        
    def __start_search(self, time: int) -> None:
        self.engine.go(movetime = time)
        
    def get_sprites_at(self, square: tuple[int, int]) -> list[pygame.sprite.Sprite]:
        return self.pieces.get_sprites_at(self.board_to_main(self.board.get_center(square)))

    def main_to_board(self, coord: tuple[int, int]):
        return (coord[0] - self.BOARD_POS[0], coord[1] - self.BOARD_POS[1])
    
    def board_to_main(self, coord: tuple[int, int]):
        return (coord[0] + self.BOARD_POS[0], coord[1] + self.BOARD_POS[1])
        
    def reset_dragged(self):
        self.dragged_piece.rect.center = self.board_to_main(self.board.get_center(self.dragged_last))
        print("CAN'T PLACE HERE!!!")
    
    def _check_checkmate_stale(self):
        
        # TODO: Add Locks to these variables
        while True:
            if self.update:
                copy = self.game.bare_copy()
                copy.update_all_legal()
                if copy.in_checkmate(1):
                    self.checkmate = 1
                if copy.in_checkmate(-1):
                    self.checkmate = -1
                
                sleep(0.01)
                self.stalemate = copy.in_stalemate()
                
                self.update = False
        
    def start_game_state_thread(self):
        threading.Thread(target=self._check_checkmate_stale, daemon=True).start()
        

def main():
    cont = True
    while cont:
        game = GameLoop()
        cont = game.start()
        game = None
        sleep(0.1)


if __name__ == "__main__":
    main()