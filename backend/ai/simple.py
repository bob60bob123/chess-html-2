import random
from typing import Optional, Tuple
from backend.game.board import Board
from backend.game.pieces import Color
from backend.game.rules import GameRules

class SimpleAI:
    """Simple AI that randomly selects a legal move"""
    def __init__(self, board: Board, color: Color):
        self.board = board
        self.color = color
        self.rules = GameRules(board)

    def get_move(self) -> Optional[Tuple[str, str]]:
        """Randomly select a legal move"""
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None
        return random.choice(legal_moves)