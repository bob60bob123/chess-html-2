import pytest
from backend.game.pieces import Pawn, Rook, Knight, Bishop, Queen, King, Color

def test_pawn_initial_position():
    pawn = Pawn(Color.WHITE)
    assert pawn.color == Color.WHITE
    assert pawn.symbol == 'P'

def test_pawn_forward_squares():
    pawn = Pawn(Color.WHITE)
    # 白兵从e2走到e4是两步，e2到e3是一步
    assert pawn.can_move("e2", "e3") == True
    assert pawn.can_move("e2", "e4") == True  # 初始两步
    assert pawn.can_move("e2", "e5") == False # 不能直接走三步

def test_rook_straight_move():
    rook = Rook(Color.BLACK)
    assert rook.can_move("a1", "a8") == True
    assert rook.can_move("a1", "h1") == True
    assert rook.can_move("a1", "b2") == False  # 不能斜走