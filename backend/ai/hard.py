from typing import Optional, Tuple
from backend.game.board import Board
from backend.game.pieces import Color
from backend.game.rules import GameRules
import random

class HardAI:
    """Hard AI using Alpha-Beta pruning with 4-6 ply depth"""
    def __init__(self, board: Board, color: Color, depth: int = 4):
        self.board = board
        self.color = color
        self.depth = depth
        self.rules = GameRules(board)

    def get_move(self) -> Optional[Tuple[str, str]]:
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None

        best_score = float('-inf')
        best_moves = []

        for from_pos, to_pos in legal_moves:
            new_board = self._simulate_move(from_pos, to_pos)
            score = self._alphabeta(new_board, self.depth - 1, float('-inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)]
            elif score == best_score:
                best_moves.append((from_pos, to_pos))

        return random.choice(best_moves)

    def _alphabeta(self, board: Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        if depth == 0:
            return self._evaluate(board)

        rules = GameRules(board)
        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = rules.get_all_legal_moves(color)

        if not legal_moves:
            if rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._alphabeta(new_board, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta cutoff
            return best_score
        else:
            best_score = float('inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._alphabeta(new_board, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return best_score

    def _evaluate(self, board: Board) -> float:
        """Improved evaluation: piece values + position values"""
        piece_square_table = self._get_piece_square_table()
        score = 0

        for pos, piece in board.squares.items():
            if piece:
                value = piece.value * 100
                if piece.color == self.color:
                    score += value + piece_square_table.get(piece.symbol, {}).get(pos, 0)
                else:
                    score -= value + piece_square_table.get(piece.symbol.upper(), {}).get(pos, 0)

        return score

    def _get_piece_square_table(self) -> dict:
        """Piece-square table for position evaluation (simplified)"""
        pawn_table = {
            'a': [0,  0,  0,  0,  0,  0,  0,  0],
            'b': [0,  0,  0,  0,  0,  0,  0,  0],
            'c': [0,  0,  0,  0,  0,  0,  0,  0],
            'd': [0,  0,  0,  0,  0,  0,  0,  0],
            'e': [0,  0,  0,  0,  0,  0,  0,  0],
            'f': [0,  0,  0,  0,  0,  0,  0,  0],
            'g': [0,  0,  0,  0,  0,  0,  0,  0],
            'h': [0,  0,  0,  0,  0,  0,  0,  0],
        }
        return {
            'P': pawn_table, 'p': pawn_table,
            'R': {}, 'r': {},
            'N': {}, 'n': {},
            'B': {}, 'b': {},
            'Q': {}, 'q': {},
            'K': {}, 'k': {},
        }

    def _simulate_move(self, from_pos: str, to_pos: str) -> Board:
        return self._simulate_move_on_board(self.board, from_pos, to_pos)

    def _simulate_move_on_board(self, board: Board, from_pos: str, to_pos: str) -> Board:
        new_board = board.copy()
        piece = new_board.remove_piece(from_pos)
        new_board.set_piece(to_pos, piece)
        new_board.turn = board.turn.opponent()
        return new_board