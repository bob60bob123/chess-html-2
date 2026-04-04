import pytest
from backend.game.board import Board
from backend.game.pieces import Color

def test_board_initialization():
    board = Board()
    assert board.turn == Color.WHITE
    # Check initial layout
    assert board.get_piece("a1").symbol == "R"  # White rook
    assert board.get_piece("e1").symbol == "K"  # White king
    assert board.get_piece("d1").symbol == "Q"  # White queen
    assert board.get_piece("a8").symbol == "r"  # Black rook
    assert board.get_piece("e8").symbol == "k"  # Black king

def test_get_piece():
    board = Board()
    piece = board.get_piece("e2")
    assert piece.symbol == "P"  # White pawn

def test_pos_to_coords():
    from backend.game.board import Board
    assert Board.pos_to_coords("a1") == (0, 0)
    assert Board.pos_to_coords("h8") == (7, 7)
    assert Board.pos_to_coords("e4") == (4, 3)

def test_coords_to_pos():
    from backend.game.board import Board
    assert Board.coords_to_pos(0, 0) == "a1"
    assert Board.coords_to_pos(4, 3) == "e4"

def test_is_empty():
    board = Board()
    assert not board.is_empty("e2")  # Has pawn
    assert board.is_empty("e4")  # Empty

def test_remove_piece():
    board = Board()
    piece = board.remove_piece("e2")
    assert piece.symbol == "P"
    assert board.is_empty("e2")

def test_set_piece():
    board = Board()
    board.remove_piece("e2")
    assert board.is_empty("e2")
    # Re-set piece
    from backend.game.pieces import Pawn
    board.set_piece("e2", Pawn(Color.WHITE))
    assert not board.is_empty("e2")
    assert board.get_piece("e2").symbol == "P"