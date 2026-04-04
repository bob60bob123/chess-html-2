from enum import Enum
from typing import TYPE_CHECKING, List, Tuple, Optional

if TYPE_CHECKING:
    from .board import Board

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def opponent(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class Piece:
    def __init__(self, color: Color):
        self.color = color
        self.symbol = ""
        self.value = 0

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        raise NotImplementedError

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'P' if color == Color.WHITE else 'p'
        self.value = 1

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        file_from = ord(from_pos[0])
        rank_from = int(from_pos[1])
        file_to = ord(to_pos[0])
        rank_to = int(to_pos[1])

        direction = 1 if self.color == Color.WHITE else -1
        start_rank = 2 if self.color == Color.WHITE else 7

        # Move forward one square
        if file_from == file_to and rank_to == rank_from + direction:
            return True
        # Initial two-step move
        if file_from == file_to and rank_from == start_rank and rank_to == rank_from + 2 * direction:
            return True
        # Capture (diagonal one square)
        if abs(file_to - file_from) == 1 and rank_to == rank_from + direction:
            return True
        return False

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        direction = 1 if self.color == Color.WHITE else -1
        start_rank = 2 if self.color == Color.WHITE else 7

        # Move forward one square
        new_rank = rank_idx + direction
        if 0 <= new_rank <= 7:
            pos = chr(ord('a') + file_idx) + str(new_rank + 1)
            squares.append(pos)
            # Initial two-step move
            if rank_idx + 1 == start_rank:
                new_rank = rank_idx + 2 * direction
                if 0 <= new_rank <= 7:
                    pos = chr(ord('a') + file_idx) + str(new_rank + 1)
                    squares.append(pos)

        # Diagonal capture
        for df in [-1, 1]:
            new_file = file_idx + df
            new_rank = rank_idx + direction
            if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                pos = chr(ord('a') + new_file) + str(new_rank + 1)
                squares.append(pos)

        return squares

# Rook - moves horizontally and vertically any number of squares
class Rook(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'R' if color == Color.WHITE else 'r'
        self.value = 5

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        if from_pos[0] != to_pos[0] and from_pos[1] != to_pos[1]:
            return False  # Must be same file or same rank
        return True

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        # Four horizontal/vertical directions
        for direction in [(0,1),(0,-1),(1,0),(-1,0)]:
            for i in range(1, 8):
                new_file = file_idx + direction[0] * i
                new_rank = rank_idx + direction[1] * i
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares

# Knight - moves in L-shape (2+1)
class Knight(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'N' if color == Color.WHITE else 'n'
        self.value = 3

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return (df == 1 and dr == 2) or (df == 2 and dr == 1)

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for df, dr in moves:
            new_file = file_idx + df
            new_rank = rank_idx + dr
            if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares

# Bishop - moves diagonally any number of squares
class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'B' if color == Color.WHITE else 'b'
        self.value = 3

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return df == dr and df > 0  # Must be diagonal with equal distance

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        # Four diagonal directions
        for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for i in range(1, 8):
                new_file = file_idx + direction[0] * i
                new_rank = rank_idx + direction[1] * i
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares

# Queen - moves horizontally, vertically, or diagonally any number of squares
class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'Q' if color == Color.WHITE else 'q'
        self.value = 9

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        # Same file, same rank, or diagonal
        return (from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]) or (df == dr and df > 0)

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        # All eight directions
        for direction in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            for i in range(1, 8):
                new_file = file_idx + direction[0] * i
                new_rank = rank_idx + direction[1] * i
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares

# King - moves one square in any direction
class King(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'K' if color == Color.WHITE else 'k'
        self.value = 1000

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return df <= 1 and dr <= 1 and (df + dr > 0)  # Max one square, cannot stay

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        for df in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if df == 0 and dr == 0:
                    continue
                new_file = file_idx + df
                new_rank = rank_idx + dr
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares
