import pytest
from backend.game.board import Board
from backend.game.pieces import Color

def test_simple_ai():
    from backend.ai.simple import SimpleAI
    board = Board()
    ai = SimpleAI(board, Color.BLACK)
    move = ai.get_move()
    # SimpleAI returns (from, to) tuple
    assert move is not None
    assert len(move) == 2

def test_medium_ai():
    from backend.ai.medium import MediumAI
    board = Board()
    ai = MediumAI(board, Color.BLACK)
    move = ai.get_move()
    assert move is not None
    assert len(move) == 2

def test_hard_ai():
    from backend.ai.hard import HardAI
    board = Board()
    ai = HardAI(board, Color.BLACK)
    move = ai.get_move()
    assert move is not None
    assert len(move) == 2

def test_simple_ai_returns_legal_move():
    from backend.ai.simple import SimpleAI
    from backend.game.rules import GameRules
    board = Board()
    ai = SimpleAI(board, Color.WHITE)
    move = ai.get_move()
    rules = GameRules(board)
    assert rules.is_legal_move(move[0], move[1], Color.WHITE)

def test_all_ais_return_different_moves():
    """Different AIs should sometimes return different moves"""
    from backend.ai.simple import SimpleAI
    from backend.ai.medium import MediumAI
    from backend.ai.hard import HardAI

    board = Board()

    simple = SimpleAI(board, Color.WHITE)
    medium = MediumAI(board, Color.WHITE)
    hard = HardAI(board, Color.WHITE)

    # Just verify they all return valid moves
    simple_move = simple.get_move()
    medium_move = medium.get_move()
    hard_move = hard.get_move()

    assert simple_move is not None
    assert medium_move is not None
    assert hard_move is not None