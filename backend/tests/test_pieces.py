import pytest
from backend.game.pieces import Pawn, Rook, Knight, Bishop, Queen, King, Color

def test_pawn_initial_position():
    pawn = Pawn(Color.WHITE)
    assert pawn.color == Color.WHITE
    assert pawn.symbol == 'P'

def test_pawn_forward_squares():
    pawn = Pawn(Color.WHITE)
    # White pawn can move 1 or 2 squares forward from starting rank
    assert pawn.can_move("e2", "e3") == True
    assert pawn.can_move("e2", "e4") == True  # Initial two-step move
    assert pawn.can_move("e2", "e5") == False # Cannot move three squares

def test_black_pawn():
    pawn = Pawn(Color.BLACK)
    assert pawn.symbol == 'p'
    assert pawn.can_move("e7", "e6") == True
    assert pawn.can_move("e7", "e5") == True

def test_rook_straight_move():
    rook = Rook(Color.BLACK)
    assert rook.can_move("a1", "a8") == True
    assert rook.can_move("a1", "h1") == True
    assert rook.can_move("a1", "b2") == False  # Cannot move diagonally

def test_knight_move():
    knight = Knight(Color.WHITE)
    # Knight can move in L-shape: 2+1 or 1+2
    assert knight.can_move("b1", "c3") == True
    assert knight.can_move("b1", "a3") == True
    assert knight.can_move("b1", "b3") == False  # Cannot move straight

def test_bishop_move():
    bishop = Bishop(Color.WHITE)
    assert bishop.can_move("c1", "f4") == True  # Diagonal move
    assert bishop.can_move("c1", "c4") == False  # Cannot move straight

def test_queen_move():
    queen = Queen(Color.WHITE)
    assert queen.can_move("d1", "d8") == True  # Straight line
    assert queen.can_move("d1", "h5") == True   # Diagonal
    assert queen.can_move("d1", "e2") == True   # Diagonal
    assert queen.can_move("d1", "e3") == False  # Knight-like move not allowed

def test_king_move():
    king = King(Color.WHITE)
    assert king.can_move("e1", "e2") == True   # One step forward
    assert king.can_move("e1", "f1") == True   # One step right
    assert king.can_move("e1", "f2") == True   # One step diagonal
    assert king.can_move("e1", "e1") == False  # Cannot stay in place

def test_pawn_get_move_squares():
    pawn = Pawn(Color.WHITE)
    squares = pawn.get_move_squares("e2")
    assert "e3" in squares
    assert "e4" in squares
    assert "d3" in squares  # Diagonal capture
    assert "f3" in squares  # Diagonal capture

def test_knight_get_move_squares():
    knight = Knight(Color.WHITE)
    squares = knight.get_move_squares("b1")
    assert "c3" in squares
    assert "a3" in squares
    assert "d2" in squares
    assert len(squares) == 3
