""" Exceptions
    ----------
    Contains all the exceptions used by the chess package.

"""

from os import PathLike
from typing import Union


class InvalidEngineError(Exception):
    """Exception raised for non UCI compatibility."""

    def __init__(self, path: Union[str, PathLike], message="Program is not a UCI compatible chess engine."):
        """Construct exception.

        Parameters
        ----------
        path : str, PathLike
            Path of program causing error.
        message : str, optional
            Error message, by default "Program is not a UCI compatible chess engine"
        """
        self.path = path
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.path} -> {self.message}"

class InvalidFENError(Exception):
    """Exception raised for and invalid FEN string being parsed."""

    def __init__(self, string: str, message="Not a valid FEN string."):
        """Construct exception

        Parameters
        ----------
        string : str
            FEN string that raised the error
        message : str, optional
            Error message, by default "Not a valid FEN string."
        """

        self.string = string
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.string} -> {self.message}"
