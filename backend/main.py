from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.board import Board
from backend.game.pieces import Color, Pawn, King, Rook, Bishop, Knight, Queen
from backend.game.rules import GameRules
from backend.ai.simple import SimpleAI
from backend.ai.medium import MediumAI
from backend.ai.hard import HardAI
from backend.storage.replay import ReplayStorage

# Use absolute path for replay storage
replay_storage = ReplayStorage(storage_dir=str(Path(__file__).parent / "replays"))

app = FastAPI(title="Chess Game API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state storage (use Redis in production)
games: Dict = {}

class StartGameRequest(BaseModel):
    difficulty: str  # simple, medium, hard

class MoveRequest(BaseModel):
    game_id: str
    from_pos: Optional[str] = None
    to_pos: Optional[str] = None
    promotion: Optional[str] = None  # 升变棋子: Q, R, B, N

class GameState(BaseModel):
    game_id: str
    board: List[List[Optional[str]]]
    turn: str
    check: bool
    game_over: bool
    result: Optional[str]
    legal_moves: Dict

@app.post("/api/game/start")
def start_game(req: StartGameRequest):
    # Validate difficulty
    valid_difficulties = ["simple", "medium", "hard"]
    if req.difficulty not in valid_difficulties:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    game_id = str(uuid.uuid4())[:8]
    board = Board()
    games[game_id] = {
        "board": board,
        "difficulty": req.difficulty,
        "move_history": [],
    }
    rules = GameRules(board)
    legal_moves = {}
    for pos, piece in board.squares.items():
        if piece and piece.color == Color.WHITE:
            moves = rules.get_legal_moves(pos, Color.WHITE)
            if moves:
                legal_moves[pos] = moves

    return {
        "game_id": game_id,
        "board": board.get_board_state(),
        "turn": "white",
        "check": rules.is_king_in_check(Color.WHITE),
        "game_over": False,
        "result": None,
        "legal_moves": legal_moves,
    }

@app.post("/api/game/move")
def make_move(req: MoveRequest):
    """Handle player move only, return immediately without AI move"""
    if not req.from_pos or not req.to_pos:
        return {"legal": False, "reason": "missing position"}

    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    rules = GameRules(board)
    color = Color.WHITE  # Player is always white

    # Validate move legality
    if not rules.is_legal_move(req.from_pos, req.to_pos, color):
        return {"legal": False, "reason": "illegal move"}

    # Check for pawn promotion before executing move
    piece = board.get_piece(req.from_pos)
    to_rank = int(req.to_pos[1])
    is_promotion = (isinstance(piece, Pawn) and ((piece.color == Color.WHITE and to_rank == 8) or
                                                   (piece.color == Color.BLACK and to_rank == 1)))

    # If promotion required but not provided, ask for promotion
    if is_promotion and not req.promotion:
        return {"legal": True, "promotion_required": True, "from_pos": req.from_pos, "to_pos": req.to_pos}

    # Execute move
    piece = board.remove_piece(req.from_pos)
    captured = board.get_piece(req.to_pos)
    board.set_piece(req.to_pos, piece)

    # Detect special moves before handling them
    is_castling = None
    is_en_passant = False

    # Castling detection: King moves 2 squares horizontally
    if isinstance(piece, King) and abs(ord(req.to_pos[0]) - ord(req.from_pos[0])) == 2:
        is_castling = 'K' if req.to_pos[0] == 'g' else 'Q'
        # Move the rook
        if is_castling == 'K':
            rook = board.remove_piece(req.from_pos[0] + 'h')
            board.set_piece('f' + req.from_pos[1], rook)
        else:
            rook = board.remove_piece(req.from_pos[0] + 'a')
            board.set_piece('d' + req.from_pos[1], rook)

    # En passant detection: pawn moves diagonally to empty square
    if isinstance(piece, Pawn) and req.from_pos[0] != req.to_pos[0] and captured is None:
        is_en_passant = True
        captured = board.get_piece(req.to_pos[0] + req.from_pos[1])
        # Remove the captured pawn (en passant)
        board.remove_piece(req.to_pos[0] + req.from_pos[1])

    # Handle promotion
    promotion_result = None
    if is_promotion and req.promotion:
        from backend.game.pieces import Queen, Rook, Bishop, Knight
        promotion_map = {'Q': Queen, 'R': Rook, 'B': Bishop, 'N': Knight}
        if req.promotion in promotion_map:
            board.set_piece(req.to_pos, promotion_map[req.promotion](piece.color))
            promotion_result = req.promotion

    # Record history
    game["move_history"].append({
        "from": req.from_pos,
        "to": req.to_pos,
        "piece": piece.symbol,
        "captured": captured.symbol if captured else None,
        "promotion": promotion_result,
        "castling": is_castling,
        "en_passant": is_en_passant,
    })

    # Switch turn to black
    board.turn = Color.BLACK

    # Check if game is over (black has no moves)
    black_moves = rules.get_all_legal_moves(Color.BLACK)
    black_in_check = rules.is_king_in_check(Color.BLACK)

    result = None
    game_over = False
    if not black_moves:
        game_over = True
        result = "white_win" if black_in_check else "draw"

    # Get legal moves for black (AI)
    legal_moves = {}
    if not game_over:
        rules = GameRules(board)
        for pos, piece in board.squares.items():
            if piece and piece.color == Color.BLACK:
                moves = rules.get_legal_moves(pos, Color.BLACK)
                if moves:
                    legal_moves[pos] = moves

    return {
        "legal": True,
        "promotion_required": False,
        "player_move": (req.from_pos, req.to_pos),
        "board": board.get_board_state(),
        "turn": "black",
        "check": black_in_check,
        "game_over": game_over,
        "result": result,
        "legal_moves": legal_moves,
        "move_history": game["move_history"],
    }


@app.post("/api/game/ai_move")
def ai_move(req: MoveRequest):
    """Execute AI move after player move is displayed"""
    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    rules = GameRules(board)

    # Check if game is already over
    white_moves = rules.get_all_legal_moves(Color.WHITE)
    white_in_check = rules.is_king_in_check(Color.WHITE)

    if not white_moves:
        return {
            "ai_move": None,
            "board": board.get_board_state(),
            "turn": "white",
            "game_over": True,
            "result": "black_win" if white_in_check else "draw",
            "legal_moves": {},
        }

    # Execute AI move
    if game["difficulty"] == "simple":
        ai = SimpleAI(board, Color.BLACK)
    elif game["difficulty"] == "medium":
        ai = MediumAI(board, Color.BLACK)
    else:
        ai = HardAI(board, Color.BLACK, time_limit=10.0)  # 10 second max

    ai_move_result = ai.get_move()
    if ai_move_result:
        from_pos, to_pos = ai_move_result
        ai_piece = board.remove_piece(from_pos)
        ai_captured = board.get_piece(to_pos)

        # Detect special moves
        is_castling = None
        is_en_passant = False

        # Castling detection
        if isinstance(ai_piece, King) and abs(ord(to_pos[0]) - ord(from_pos[0])) == 2:
            is_castling = 'K' if to_pos[0] == 'g' else 'Q'
            if is_castling == 'K':
                rook = board.remove_piece(from_pos[0] + 'h')
                board.set_piece('f' + from_pos[1], rook)
            else:
                rook = board.remove_piece(from_pos[0] + 'a')
                board.set_piece('d' + from_pos[1], rook)

        # En passant detection
        if isinstance(ai_piece, Pawn) and from_pos[0] != to_pos[0] and ai_captured is None:
            is_en_passant = True
            ai_captured = board.get_piece(to_pos[0] + from_pos[1])
            board.remove_piece(to_pos[0] + from_pos[1])

        board.set_piece(to_pos, ai_piece)

        # Handle AI promotion (black pawn reaching rank 1)
        promotion_result = None
        if isinstance(ai_piece, Pawn) and int(to_pos[1]) == 1:
            board.set_piece(to_pos, Queen(Color.BLACK))
            promotion_result = 'Q'

        game["move_history"].append({
            "from": from_pos,
            "to": to_pos,
            "piece": ai_piece.symbol,
            "captured": ai_captured.symbol if ai_captured else None,
            "promotion": promotion_result,
            "castling": is_castling,
            "en_passant": is_en_passant,
        })

    board.turn = Color.WHITE

    # Check game over
    white_moves = rules.get_all_legal_moves(Color.WHITE)
    white_in_check = rules.is_king_in_check(Color.WHITE)
    game_over = False
    result = None
    if not white_moves:
        game_over = True
        result = "black_win" if white_in_check else "draw"

    # Get legal moves for player (white)
    legal_moves = {}
    if not game_over:
        rules = GameRules(board)
        for pos, piece in board.squares.items():
            if piece and piece.color == Color.WHITE:
                moves = rules.get_legal_moves(pos, Color.WHITE)
                if moves:
                    legal_moves[pos] = moves

    return {
        "ai_move": ai_move_result,
        "board": board.get_board_state(),
        "turn": "white",
        "check": rules.is_king_in_check(Color.WHITE),
        "game_over": game_over,
        "result": result,
        "legal_moves": legal_moves,
        "move_history": game["move_history"],
    }


@app.get("/api/game/state/{game_id}")
def get_state(game_id: str):
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    rules = GameRules(board)

    legal_moves = {}
    for pos, piece in board.squares.items():
        if piece and piece.color == board.turn:
            moves = rules.get_legal_moves(pos, board.turn)
            if moves:
                legal_moves[pos] = moves

    return {
        "game_id": game_id,
        "board": board.get_board_state(),
        "turn": "white" if board.turn == Color.WHITE else "black",
        "check": rules.is_king_in_check(board.turn),
        "legal_moves": legal_moves,
        "move_history": game.get("move_history", []),
    }

@app.get("/api/replay/list")
def list_replays():
    replays = replay_storage.list_replays()
    return [{"id": r["id"], "created_at": r.get("created_at"), "result": r.get("result")} for r in replays]

@app.get("/api/replay/{replay_id}")
def get_replay(replay_id: str):
    replay = replay_storage.load(replay_id)
    if not replay:
        raise HTTPException(status_code=404, detail="Replay not found")
    return replay

@app.delete("/api/replay/{replay_id}")
def delete_replay(replay_id: str):
    success = replay_storage.delete(replay_id)
    if not success:
        raise HTTPException(status_code=404, detail="Replay not found")
    return {"success": True}


@app.post("/api/game/undo")
def undo_move(req: MoveRequest):
    """Undo last move(s) - returns to previous white turn"""
    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    move_history = game.get("move_history", [])

    # Need at least one move to undo
    if not move_history:
        return {"success": False, "reason": "No moves to undo"}

    # Undo moves until we get back to white's turn
    # Typically this means undoing 1 move (player's move) if AI hasn't moved yet,
    # or 2 moves (player's move + AI's move) if AI has moved
    # We need to undo at least one move if available
    moves_undone = 0
    while move_history and (board.turn == Color.BLACK or moves_undone == 0):
        last_move = move_history.pop()
        from_pos = last_move["from"]
        to_pos = last_move["to"]
        piece_symbol = last_move["piece"]
        captured_symbol = last_move["captured"]
        promotion = last_move["promotion"]
        castling = last_move["castling"]
        en_passant = last_move["en_passant"]

        # Recreate the piece
        from backend.game.pieces import Pawn, King, Rook, Bishop, Knight, Queen
        piece_map = {
            'P': lambda color: Pawn(color),
            'R': lambda color: Rook(color),
            'N': lambda color: Knight(color),
            'B': lambda color: Bishop(color),
            'Q': lambda color: Queen(color),
            'K': lambda color: King(color)
        }

        color = Color.WHITE if piece_symbol.isupper() else Color.BLACK
        piece = piece_map[piece_symbol.upper()](color)

        # Put the piece back to its original position
        board.remove_piece(to_pos)
        board.set_piece(from_pos, piece)

        # Handle captured piece
        if captured_symbol:
            captured_color = Color.BLACK if captured_symbol.isupper() else Color.WHITE
            captured_piece = piece_map[captured_symbol.upper()](captured_color)
            board.set_piece(to_pos, captured_piece)

        # Handle castling
        if castling:
            if castling == 'K':
                # Undo kingside castling
                rook = board.remove_piece('f' + from_pos[1])
                board.set_piece(from_pos[0] + 'h', rook)
            else:
                # Undo queenside castling
                rook = board.remove_piece('d' + from_pos[1])
                board.set_piece(from_pos[0] + 'a', rook)

        # Handle en passant
        if en_passant:
            # The captured pawn was on the same rank as the original position
            captured_pawn = Pawn(Color.BLACK if color == Color.WHITE else Color.WHITE)
            board.set_piece(to_pos[0] + from_pos[1], captured_pawn)

        # Handle promotion (need to revert to pawn)
        if promotion:
            board.set_piece(from_pos, Pawn(color))

        # Switch turn
        board.turn = Color.WHITE if board.turn == Color.BLACK else Color.BLACK
        moves_undone += 1

    # Get legal moves for white
    rules = GameRules(board)
    legal_moves = {}
    for pos, piece in board.squares.items():
        if piece and piece.color == Color.WHITE:
            moves = rules.get_legal_moves(pos, Color.WHITE)
            if moves:
                legal_moves[pos] = moves

    return {
        "success": True,
        "board": board.get_board_state(),
        "turn": "white",
        "check": rules.is_king_in_check(Color.WHITE),
        "game_over": False,
        "result": None,
        "legal_moves": legal_moves,
        "move_history": move_history,
    }