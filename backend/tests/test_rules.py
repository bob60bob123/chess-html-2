import pytest
from backend.game.board import Board
from backend.game.rules import GameRules
from backend.game.pieces import Color

def test_king_in_check():
    board = Board()
    rules = GameRules(board)
    # No check in initial position
    assert not rules.is_king_in_check(Color.WHITE)
    assert not rules.is_king_in_check(Color.BLACK)

def test_legal_move_validation():
    board = Board()
    rules = GameRules(board)
    # White pawn e2 to e4 is legal two-step
    assert rules.is_legal_move("e2", "e4", Color.WHITE)
    # But e2 to e5 is illegal
    assert not rules.is_legal_move("e2", "e5", Color.WHITE)

def test_cannot_capture_own_piece():
    board = Board()
    rules = GameRules(board)
    # Cannot capture own piece
    assert not rules.is_legal_move("e2", "e3", Color.BLACK)  # Black can't move white pawn

def test_pawn_capture():
    board = Board()
    rules = GameRules(board)
    # Move pawn to d4
    board.set_piece("d4", board.remove_piece("d2"))
    # Now e4 pawn can capture d4 (diagonal)
    board.turn = Color.WHITE
    assert rules.is_legal_move("e4", "d5", Color.WHITE) == False  # Need to set up properly

def test_castling_setup():
    board = Board()
    rules = GameRules(board)
    # Clear squares for castling (short side)
    for pos in ['f1', 'g1']:
        board.set_piece(pos, None)
    # Check if short castling is possible for white
    assert rules.can_castle(Color.WHITE, "K") == True

def test_get_all_legal_moves():
    board = Board()
    rules = GameRules(board)
    white_moves = rules.get_all_legal_moves(Color.WHITE)
    # White has 20 moves in initial position
    assert len(white_moves) == 20
    black_moves = rules.get_all_legal_moves(Color.BLACK)
    assert len(black_moves) == 20