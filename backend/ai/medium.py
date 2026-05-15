from typing import Optional, Tuple, List
from backend.game.board import Board
from backend.game.pieces import Color
from backend.game.rules import GameRules
import random

class MediumAI:
    """Medium AI using Minimax algorithm with 2-3 ply depth"""
    def __init__(self, board: Board, color: Color, depth: int = 2):
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
            captured = self._do_move(from_pos, to_pos)
            score = self._minimax(self.depth - 1, False)
            self._undo_move(from_pos, to_pos, captured)

            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)]
            elif score == best_score:
                best_moves.append((from_pos, to_pos))

        return random.choice(best_moves)

    def _do_move(self, from_pos: str, to_pos: str):
        piece = self.board.remove_piece(from_pos)
        captured = self.board.get_piece(to_pos)
        self.board.set_piece(to_pos, piece)
        self.board.turn = self.board.turn.opponent()
        return captured

    def _undo_move(self, from_pos: str, to_pos: str, captured):
        piece = self.board.remove_piece(to_pos)
        self.board.set_piece(from_pos, piece)
        if captured:
            self.board.set_piece(to_pos, captured)
        self.board.turn = self.board.turn.opponent()

    def _minimax(self, depth: int, is_maximizing: bool) -> float:
        if depth == 0:
            return self._evaluate()

        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = self.rules.get_all_legal_moves(color)

        if not legal_moves:
            if self.rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for from_pos, to_pos in legal_moves:
                captured = self._do_move(from_pos, to_pos)
                score = self._minimax(depth - 1, False)
                self._undo_move(from_pos, to_pos, captured)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for from_pos, to_pos in legal_moves:
                captured = self._do_move(from_pos, to_pos)
                score = self._minimax(depth - 1, True)
                self._undo_move(from_pos, to_pos, captured)
                best_score = min(best_score, score)
            return best_score

    def _evaluate(self) -> float:
        """Simple position evaluation: sum of piece values"""
        score = 0
        for piece in self.board.squares.values():
            if piece:
                value = piece.value
                if piece.color == self.color:
                    score += value
                else:
                    score -= value
        return score
