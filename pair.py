""" Pair class
    ----------
    Used for storing coordinates in a way that better relates to the
    coordinate system of chess.
    
    By: Chris Parker
"""

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
        """Is the pair negative?"""
        return self.x < 0 or self.y < 0

    def is_above(self, maxY, maxX) -> bool:
        """Is the pair above the given max."""
        return self.x > maxX or self.y > maxY
    
    def to_standard(self) -> tuple[int, int]:
        """Return the (x,y) tuple version of this pair."""
        return (self.x, self.y)

    # SPECIAL METHODS
    def __str__(self) -> str:
        return self.get_alg_coords()
    
    def __repr__(self) -> str:
        return f"{self.y},{self.x}; {self.col}{self.row}"

    def __bool__(self) -> bool:
        return (self.x != None and self.y != None)

    def __eq__(self, other: 'Pair') -> bool:
        if type(other) == Pair:
            return self.x == other.x and self.y == other.y
        else:
            return False
    
    def __getitem__(self, key: int | str) -> int | None:
        if key == "x" or key == "row" or key == 0:
            return self.x
        elif key == "y" or key == "col" or key == 1:
            return self.y
        