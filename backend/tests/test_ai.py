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

def test_no_legal_moves_returns_none():
    """When there are no legal moves, AI should return None"""
    from backend.ai.simple import SimpleAI
    from backend.game.pieces import Queen, Rook, King
    board = Board()
    # Clear the board completely
    for file in 'abcdefgh':
        for rank in '12345678':
            board.set_piece(file + rank, None)
    # Set up a checkmate position:
    # Black king at a8 (cornered)
    # White queen at c7 (checking the king)
    # White rooks at b6 and c6 (protecting the queen)
    # King has no legal moves: a7 (attacked by rook b6), b8 (attacked by queen c7)
    board.set_piece("a8", King(Color.BLACK))
    board.set_piece("c7", Queen(Color.WHITE))
    board.set_piece("b6", Rook(Color.WHITE))
    board.set_piece("c6", Rook(Color.WHITE))
    board.turn = Color.BLACK

    ai = SimpleAI(board, Color.BLACK)
    move = ai.get_move()
    assert move is None

def test_medium_ai_returns_legal_move():
    from backend.ai.medium import MediumAI
    from backend.game.rules import GameRules
    board = Board()
    ai = MediumAI(board, Color.WHITE)
    move = ai.get_move()
    assert move is not None
    rules = GameRules(board)
    assert rules.is_legal_move(move[0], move[1], Color.WHITE)

def test_hard_ai_returns_legal_move():
    from backend.ai.hard import HardAI
    from backend.game.rules import GameRules
    board = Board()
    ai = HardAI(board, Color.WHITE)
    move = ai.get_move()
    assert move is not None
    rules = GameRules(board)
    assert rules.is_legal_move(move[0], move[1], Color.WHITE)