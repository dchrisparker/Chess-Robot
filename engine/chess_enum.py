# Enumeration
from enum import Enum, IntEnum

class Color(IntEnum):
    """Piece color."""
    WHITE = 1
    BLACK = -1

class Type(Enum):
    """Piece type."""
    PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING = 'P', 'R', 'N', 'B', 'Q', 'K'

class Column(IntEnum):
    """Column labels."""
    A, B, C, D, E, F, G, H = tuple(range(0,8))
    a, b, c, d, e, f, g, h = tuple(range(0,8))