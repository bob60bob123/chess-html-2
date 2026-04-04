import copy
from typing import Dict, List, Optional, Tuple
from .pieces import (
    Piece, Pawn, Rook, Knight, Bishop, Queen, King, Color
)

class Board:
    def __init__(self):
        self.squares: Dict[str, Optional[Piece]] = {}
        self.turn = Color.WHITE
        self.move_history: List[dict] = []
        self.castling_rights = {
            Color.WHITE: {"K": True, "Q": True},  # White short castle, long castle
            Color.BLACK: {"k": True, "q": True},  # Black short castle, long castle
        }
        self.en_passant_target: Optional[str] = None  # En passant target square
        self.halfmove_clock: int = 0  # Halfmove clock (for draw detection)
        self._initialize_board()

    def _initialize_board(self):
        # Initialize 8x8 board
        for file in 'abcdefgh':
            for rank in '12345678':
                pos = file + rank
                self.squares[pos] = None

        # Place white pieces
        self.squares['a1'] = Rook(Color.WHITE)
        self.squares['b1'] = Knight(Color.WHITE)
        self.squares['c1'] = Bishop(Color.WHITE)
        self.squares['d1'] = Queen(Color.WHITE)
        self.squares['e1'] = King(Color.WHITE)
        self.squares['f1'] = Bishop(Color.WHITE)
        self.squares['g1'] = Knight(Color.WHITE)
        self.squares['h1'] = Rook(Color.WHITE)
        for file in 'abcdefgh':
            self.squares[file + '2'] = Pawn(Color.WHITE)

        # Place black pieces
        self.squares['a8'] = Rook(Color.BLACK)
        self.squares['b8'] = Knight(Color.BLACK)
        self.squares['c8'] = Bishop(Color.BLACK)
        self.squares['d8'] = Queen(Color.BLACK)
        self.squares['e8'] = King(Color.BLACK)
        self.squares['f8'] = Bishop(Color.BLACK)
        self.squares['g8'] = Knight(Color.BLACK)
        self.squares['h8'] = Rook(Color.BLACK)
        for file in 'abcdefgh':
            self.squares[file + '7'] = Pawn(Color.BLACK)

    @staticmethod
    def pos_to_coords(pos: str) -> Tuple[int, int]:
        """Convert position string (e.g., 'e4') to coordinates (file, rank)"""
        file_idx = ord(pos[0]) - ord('a')
        rank_idx = int(pos[1]) - 1
        return file_idx, rank_idx

    @staticmethod
    def coords_to_pos(file_idx: int, rank_idx: int) -> str:
        """Convert coordinates to position string"""
        return chr(ord('a') + file_idx) + str(rank_idx + 1)

    def get_piece(self, pos: str) -> Optional[Piece]:
        """Get piece at specified position"""
        return self.squares.get(pos)

    def set_piece(self, pos: str, piece: Optional[Piece]):
        """Set piece at specified position"""
        self.squares[pos] = piece

    def remove_piece(self, pos: str) -> Optional[Piece]:
        """Remove and return piece at specified position"""
        piece = self.squares[pos]
        self.squares[pos] = None
        return piece

    def is_empty(self, pos: str) -> bool:
        """Check if position is empty"""
        return self.squares[pos] is None

    def get_board_state(self) -> List[List[Optional[str]]]:
        """Get 2D array representation of board state (for frontend rendering)"""
        board = []
        for rank in range(8, 0, -1):  # From 8 to 1 (black's perspective)
            row = []
            for file in 'abcdefgh':
                pos = file + str(rank)
                piece = self.squares[pos]
                row.append(piece.symbol if piece else None)
            board.append(row)
        return board

    def copy(self) -> 'Board':
        """Create deep copy of board"""
        new_board = Board.__new__(Board)
        new_board.squares = copy.deepcopy(self.squares)
        new_board.turn = self.turn
        new_board.move_history = self.move_history.copy()
        new_board.castling_rights = {
            color: rights.copy() for color, rights in self.castling_rights.items()
        }
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        return new_board