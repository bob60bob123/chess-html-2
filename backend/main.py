from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

from game.board import Board
from game.pieces import Color
from game.rules import GameRules
from ai.simple import SimpleAI
from ai.medium import MediumAI
from ai.hard import HardAI
from storage.replay import ReplayStorage

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
replay_storage = ReplayStorage()

class StartGameRequest(BaseModel):
    difficulty: str  # simple, medium, hard

class MoveRequest(BaseModel):
    game_id: str
    from_pos: Optional[str] = None
    to_pos: Optional[str] = None

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

    # Execute move
    piece = board.remove_piece(req.from_pos)
    captured = board.get_piece(req.to_pos)
    board.set_piece(req.to_pos, piece)

    # Record history
    game["move_history"].append({
        "from": req.from_pos,
        "to": req.to_pos,
        "piece": piece.symbol,
        "captured": captured.symbol if captured else None,
    })

    # Switch turn
    board.turn = Color.BLACK

    # Check if game is over
    black_moves = rules.get_all_legal_moves(Color.BLACK)
    black_in_check = rules.is_king_in_check(Color.BLACK)

    result = None
    game_over = False
    if not black_moves:
        game_over = True
        result = "white_win" if black_in_check else "draw"

    ai_move = None
    # AI move
    if not game_over:
        if game["difficulty"] == "simple":
            ai = SimpleAI(board, Color.BLACK)
        elif game["difficulty"] == "medium":
            ai = MediumAI(board, Color.BLACK)
        else:
            ai = HardAI(board, Color.BLACK)

        ai_move = ai.get_move()
        if ai_move:
            from_pos, to_pos = ai_move
            ai_piece = board.remove_piece(from_pos)
            ai_captured = board.get_piece(to_pos)
            board.set_piece(to_pos, ai_piece)
            game["move_history"].append({
                "from": from_pos,
                "to": to_pos,
                "piece": ai_piece.symbol,
                "captured": ai_captured.symbol if ai_captured else None,
            })
            board.turn = Color.WHITE

        # Check game over again
        white_moves = rules.get_all_legal_moves(Color.WHITE)
        white_in_check = rules.is_king_in_check(Color.WHITE)
        if not white_moves:
            game_over = True
            result = "black_win" if white_in_check else "draw"

    # Get legal moves for player
    legal_moves = {}
    if not game_over:
        rules = GameRules(board)
        for pos, piece in board.squares.items():
            if piece and piece.color == Color.WHITE:
                moves = rules.get_legal_moves(pos, Color.WHITE)
                if moves:
                    legal_moves[pos] = moves

    return {
        "legal": True,
        "board": board.get_board_state(),
        "turn": "white" if board.turn == Color.WHITE else "black",
        "check": rules.is_king_in_check(Color.WHITE if board.turn == Color.WHITE else Color.BLACK),
        "game_over": game_over,
        "result": result,
        "ai_move": ai_move,
        "legal_moves": legal_moves,
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
    }

@app.post("/api/game/undo")
def undo_move(req: MoveRequest):
    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # Undo last two moves (player + AI)
    if len(game["move_history"]) >= 2:
        game["move_history"] = game["move_history"][:-2]
        game["board"] = Board()
        # Replay history
        for move in game["move_history"]:
            from_pos = move["from"]
            to_pos = move["to"]
            piece = game["board"].remove_piece(from_pos)
            game["board"].set_piece(to_pos, piece)
    return {"success": True}

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

@app.post("/api/replay/save")
def save_replay(req: MoveRequest):
    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    rules = GameRules(game["board"])
    black_moves = rules.get_all_legal_moves(Color.BLACK)
    if not black_moves:
        result = "player_win"
    else:
        result = "unknown"

    replay_data = {
        "difficulty": game["difficulty"],
        "moves": game["move_history"],
        "result": result,
    }
    replay_id = replay_storage.save(replay_data)
    return {"replay_id": replay_id}