from enum import Enum, auto, IntEnum

class Color(IntEnum):
        WHITE = 1
        BLACK = -1

class Type(Enum):
    PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING = 'P', 'R', 'N', 'B', 'Q', 'K'

class Column(IntEnum):
    A, B, C, D, E, F, G, H = tuple(range(0,8))
    a, b, c, d, e, f, g, h = tuple(range(0,8))