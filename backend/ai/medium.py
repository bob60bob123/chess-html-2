from typing import Optional, Tuple
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
            new_board = self._simulate_move(from_pos, to_pos)
            score = self._minimax(new_board, self.depth - 1, False)

            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)]
            elif score == best_score:
                best_moves.append((from_pos, to_pos))

        return random.choice(best_moves)

    def _minimax(self, board: Board, depth: int, is_maximizing: bool) -> float:
        if depth == 0:
            return self._evaluate(board)

        rules = GameRules(board)
        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = rules.get_all_legal_moves(color)

        if not legal_moves:
            if rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0  # Stalemate (draw)

        if is_maximizing:
            best_score = float('-inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._minimax(new_board, depth - 1, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._minimax(new_board, depth - 1, True)
                best_score = min(best_score, score)
            return best_score

    def _evaluate(self, board: Board) -> float:
        """Simple position evaluation: sum of piece values"""
        score = 0
        for piece in board.squares.values():
            if piece:
                value = piece.value
                if piece.color == self.color:
                    score += value
                else:
                    score -= value
        return score

    def _simulate_move(self, from_pos: str, to_pos: str) -> Board:
        return self._simulate_move_on_board(self.board, from_pos, to_pos)

    def _simulate_move_on_board(self, board: Board, from_pos: str, to_pos: str) -> Board:
        new_board = board.copy()
        piece = new_board.remove_piece(from_pos)
        new_board.set_piece(to_pos, piece)
        new_board.turn = board.turn.opponent()
        return new_board