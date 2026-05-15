from typing import Optional, Tuple, List, Dict
from backend.game.board import Board
from backend.game.pieces import Color, Pawn, Rook, Knight, Bishop, Queen, King
from backend.game.rules import GameRules
import random
import time

class HardAI:
    """Hard AI using Iterative Deepening Alpha-Beta with Time Control"""
    def __init__(self, board: Board, color: Color, depth: int = 4, time_limit: float = 5.0):
        self.board = board
        self.color = color
        self.max_depth = depth
        self.time_limit = time_limit  # seconds
        self.rules = GameRules(board)
        self.tt: Dict[int, Tuple[int, int, int]] = {}
        self.start_time = 0
        self.best_move_found = None

    def get_move(self) -> Optional[Tuple[str, str]]:
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None

        legal_moves = self._order_moves(legal_moves)
        self.start_time = time.time()
        self.best_move_found = legal_moves[0]  # Fallback to first move

        # Start search at depth 1 and deepen
        for depth in range(1, self.max_depth + 1):
            # Check time limit before each depth
            if time.time() - self.start_time >= self.time_limit:
                break

            score, move = self._search_at_depth(depth, legal_moves)
            if move is not None:
                self.best_move_found = move

            # If time is running low, stop deepening
            elapsed = time.time() - self.start_time
            if elapsed >= self.time_limit * 0.8:
                break

        return self.best_move_found

    def _search_at_depth(self, depth: int, moves: List[Tuple[str, str]]) -> Tuple[float, Optional[Tuple[str, str]]]:
        """Search all moves at given depth, return best score and move"""
        best_score = float('-inf')
        best_move = None

        for from_pos, to_pos in moves:
            if time.time() - self.start_time >= self.time_limit:
                break

            original_piece, captured = self._do_move(from_pos, to_pos)
            score = self._alphabeta(depth - 1, float('-inf'), float('inf'), True)
            self._undo_move(from_pos, to_pos, captured, original_piece)

            if score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)

        return best_score, best_move

    def _order_moves(self, moves: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Order moves using MVV-LVA for better pruning"""
        def mvv_lva(m):
            from_pos, to_pos = m
            attacker = self.board.get_piece(from_pos)
            victim = self.board.get_piece(to_pos)
            if victim:
                return victim.value * 10 - attacker.value
            # Prioritize castling and queen moves early
            attacker_piece = self.board.get_piece(from_pos)
            if attacker_piece and isinstance(attacker_piece, King):
                return 500  # Boost castling
            if attacker_piece and isinstance(attacker_piece, Queen):
                return 100
            return -1000
        return sorted(moves, key=mvv_lva, reverse=True)

    def _do_move(self, from_pos: str, to_pos: str):
        """Execute move and return (original_piece, captured_piece)"""
        piece = self.board.remove_piece(from_pos)
        captured = self.board.get_piece(to_pos)
        self.board.set_piece(to_pos, piece)
        # Handle promotion: replace pawn with queen on the board
        if isinstance(piece, Pawn):
            rank = int(to_pos[1])
            if (piece.color == Color.WHITE and rank == 8) or (piece.color == Color.BLACK and rank == 1):
                self.board.set_piece(to_pos, Queen(piece.color))
        self.board.turn = self.board.turn.opponent()
        return piece, captured

    def _undo_move(self, from_pos: str, to_pos: str, captured, original_piece):
        """Undo move, restoring original_piece (not promoted piece)"""
        self.board.remove_piece(to_pos)  # Remove whatever's there (queen if promoted)
        self.board.set_piece(from_pos, original_piece)  # Restore original piece
        if captured:
            self.board.set_piece(to_pos, captured)
        self.board.turn = self.board.turn.opponent()

    def _alphabeta(self, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        # Time check
        if time.time() - self.start_time >= self.time_limit:
            return 0

        if depth == 0:
            return self._evaluate()

        # Transposition table lookup
        board_hash = hash(frozenset(self.board.squares.items()))
        if board_hash in self.tt:
            tt_depth, tt_score, tt_flag = self.tt[board_hash]
            if tt_depth >= depth:
                if tt_flag == 0:
                    return tt_score
                elif tt_flag == 1 and tt_score >= beta:
                    return tt_score
                elif tt_flag == 2 and tt_score <= alpha:
                    return tt_score

        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = self.rules.get_all_legal_moves(color)

        if not legal_moves:
            if self.rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0

        legal_moves = self._order_moves(legal_moves)

        best_score = float('-inf') if is_maximizing else float('inf')
        tt_flag = 0

        for from_pos, to_pos in legal_moves:
            if time.time() - self.start_time >= self.time_limit:
                break

            original_piece, captured = self._do_move(from_pos, to_pos)
            score = self._alphabeta(depth - 1, alpha, beta, not is_maximizing)
            self._undo_move(from_pos, to_pos, captured, original_piece)

            if is_maximizing:
                if score > best_score:
                    best_score = score
                alpha = max(alpha, score)
                if beta <= alpha:
                    tt_flag = 2
                    break
            else:
                if score < best_score:
                    best_score = score
                beta = min(beta, score)
                if beta <= alpha:
                    tt_flag = 1
                    break

        self.tt[board_hash] = (depth, best_score, tt_flag)
        return best_score

    def _evaluate(self) -> float:
        """Simple material evaluation"""
        score = 0
        for piece in self.board.squares.values():
            if piece:
                if piece.color == self.color:
                    score += piece.value
                else:
                    score -= piece.value
        return score
