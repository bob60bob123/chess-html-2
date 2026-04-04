from typing import List, Optional, Tuple
from .board import Board
from .pieces import Color, Piece, Pawn, Rook, Knight, Bishop, Queen, King

class GameRules:
    def __init__(self, board: Board):
        self.board = board

    def is_legal_move(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """Check if a piece of given color can move from from_pos to to_pos"""
        piece = self.board.get_piece(from_pos)
        if piece is None or piece.color != color:
            return False

        # Check if destination has own piece
        target = self.board.get_piece(to_pos)
        if target and target.color == color:
            return False

        # Basic movement rule check
        if not piece.can_move(from_pos, to_pos, self.board):
            return False

        # Check path is clear for sliding pieces
        if isinstance(piece, (Rook, Bishop, Queen)):
            if not self._is_path_clear(from_pos, to_pos):
                return False

        # Pawn capture rules (diagonal capture, straight move must be empty)
        if isinstance(piece, Pawn):
            file_same = from_pos[0] == to_pos[0]
            if file_same and not self.board.is_empty(to_pos):
                return False  # Pawn moving straight must have empty target
            if not file_same and self.board.is_empty(to_pos):
                # Diagonal move - check if en passant
                if not self._is_en_passant(from_pos, to_pos, color):
                    return False

        # Castling check
        if isinstance(piece, King):
            if self._is_castling(from_pos, to_pos, color):
                return True

        # Check if move leaves own king in check
        temp_board = self.board.copy()
        temp_board.set_piece(to_pos, temp_board.remove_piece(from_pos))
        temp_rules = GameRules(temp_board)
        if temp_rules.is_king_in_check(color):
            return False

        return True

    def is_king_in_check(self, color: Color) -> bool:
        """Check if king of given color is in check"""
        king_pos = self._find_king(color)
        if not king_pos:
            return False

        opponent = color.opponent()
        for pos, piece in self.board.squares.items():
            if piece and piece.color == opponent:
                if piece.can_move(pos, king_pos, self.board):
                    if self._is_path_clear(pos, king_pos):
                        return True
        return False

    def _find_king(self, color: Color) -> Optional[str]:
        """Find king position of given color"""
        for pos, piece in self.board.squares.items():
            if isinstance(piece, King) and piece.color == color:
                return pos
        return None

    def _is_path_clear(self, from_pos: str, to_pos: str) -> bool:
        """Check if path between two positions is clear (excluding start and end)"""
        fx, fy = Board.pos_to_coords(from_pos)
        tx, ty = Board.pos_to_coords(to_pos)

        dx = tx - fx
        dy = ty - fy

        if dx == 0:  # Same file
            step_x, step_y = 0, 1 if dy > 0 else -1
        elif dy == 0:  # Same rank
            step_x, step_y = 1 if dx > 0 else -1, 0
        elif abs(dx) == abs(dy):  # Diagonal
            step_x, step_y = 1 if dx > 0 else -1, 1 if dy > 0 else -1
        else:
            return True  # Not straight/diagonal (e.g., knight), assume clear

        x, y = fx + step_x, fy + step_y
        while (x, y) != (tx, ty):
            pos = Board.coords_to_pos(x, y)
            if not self.board.is_empty(pos):
                return False
            x += step_x
            y += step_y
        return True

    def can_castle(self, color: Color, side: str) -> bool:
        """Check if castling is possible
        side: 'K'=short castle (kingside), 'Q'=long castle (queenside)
        """
        rank = '1' if color == Color.WHITE else '8'
        king_pos = f'e{rank}'

        # Check if king has moved
        if not self.board.castling_rights[color][side.upper()]:
            return False

        # Check if king is in check
        if self.is_king_in_check(color):
            return False

        if side.upper() == 'K':  # Short castle
            rook_pos = f'h{rank}'
            if not isinstance(self.board.get_piece(rook_pos), Rook):
                return False
            # Check f,g squares are empty
            for pos in [f'f{rank}', f'g{rank}']:
                if not self.board.is_empty(pos):
                    return False
            king_pos_list = [f'e{rank}', f'f{rank}', f'g{rank}']
        else:  # Long castle
            rook_pos = f'a{rank}'
            if not isinstance(self.board.get_piece(rook_pos), Rook):
                return False
            # Check b,c,d squares are empty
            for pos in [f'b{rank}', f'c{rank}', f'd{rank}']:
                if not self.board.is_empty(pos):
                    return False
            king_pos_list = [f'e{rank}', f'd{rank}', f'c{rank}']

        # Check king doesn't pass through check
        temp_board = self.board.copy()
        for i in range(len(king_pos_list) - 1):
            temp_board.set_piece(king_pos_list[i+1], temp_board.remove_piece(king_pos_list[i]))
            temp_rules = GameRules(temp_board)
            if temp_rules.is_king_in_check(color):
                return False

        return True

    def _is_castling(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """Check if move is castling"""
        piece = self.board.get_piece(from_pos)
        if not isinstance(piece, King):
            return False

        fx, fy = Board.pos_to_coords(from_pos)
        tx, ty = Board.pos_to_coords(to_pos)

        # King can only move sideways 2 squares for castling
        if fy != ty or abs(tx - fx) != 2:
            return False

        rank = '1' if color == Color.WHITE else '8'
        if from_pos != f'e{rank}':
            return False

        side = 'K' if tx > fx else 'Q'  # tx>fx short castle, tx<fx long castle
        return self.can_castle(color, side)

    def _is_en_passant(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """Check if move is en passant"""
        piece = self.board.get_piece(from_pos)
        if not isinstance(piece, Pawn):
            return False

        # Pawn diagonal move to en passant target
        if self.board.en_passant_target == to_pos:
            return True
        return False

    def get_legal_moves(self, pos: str, color: Color) -> List[str]:
        """Get all legal moves for piece at position"""
        piece = self.board.get_piece(pos)
        if piece is None or piece.color != color:
            return []

        legal_moves = []
        for target_pos in piece.get_move_squares(pos, self.board):
            if self.is_legal_move(pos, target_pos, color):
                legal_moves.append(target_pos)
        return legal_moves

    def get_all_legal_moves(self, color: Color) -> List[Tuple[str, str]]:
        """Get all legal moves for given color"""
        all_moves = []
        for pos, piece in self.board.squares.items():
            if piece and piece.color == color:
                legal_targets = self.get_legal_moves(pos, color)
                for target in legal_targets:
                    all_moves.append((pos, target))
        return all_moves