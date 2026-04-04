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

def test_get_board_state():
    board = Board()
    state = board.get_board_state()
    assert len(state) == 8  # 8 rows
    assert len(state[0]) == 8  # 8 columns
    assert state[0][4] == 'k'  # Rank 8 row, file e = black king
    assert state[7][4] == 'K'  # Rank 1 row, file e = white king

def test_copy():
    board = Board()
    copied = board.copy()
    assert copied.turn == board.turn
    assert copied.get_piece("e2").symbol == 'P'
    # Modify original, copied should be independent
    board.remove_piece("e2")
    assert copied.get_piece("e2").symbol == 'P'

def test_move_history():
    board = Board()
    assert board.move_history == []
    board.move_history.append({"from": "e2", "to": "e4"})
    assert len(board.move_history) == 1

def test_castling_rights():
    board = Board()
    assert board.castling_rights[Color.WHITE]["K"] == True
    assert board.castling_rights[Color.WHITE]["Q"] == True
    assert board.castling_rights[Color.BLACK]["k"] == True
    assert board.castling_rights[Color.BLACK]["q"] == True