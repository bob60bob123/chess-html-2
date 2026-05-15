# 国际象棋游戏实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个完整的HTML5网页版人机国际象棋对弈系统，包含前端、后端AI和复盘功能

**Architecture:** 前后端分离架构，前端HTML5通过REST API与Python/FastAPI后端通信。棋盘逻辑和AI在后端实现，前端仅负责渲染和交互。

**Tech Stack:** Python 3.11+ / FastAPI / HTML5 / CSS3 / JavaScript (ES6+)

---

## 文件结构

```
chess/
├── backend/
│   ├── main.py                      # FastAPI入口，路由定义
│   ├── requirements.txt             # 依赖：fastapi, uvicorn, pydantic
│   ├── game/
│   │   ├── __init__.py
│   │   ├── board.py               # 棋盘类，表示棋盘状态
│   │   ├── pieces.py              # 棋子基类和6种棋子实现
│   │   └── rules.py               # 走棋规则、将军检测、胜负判定
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── simple.py              # 简单AI：随机选择
│   │   ├── medium.py              # 中等AI：Minimax 2-3层
│   │   └── hard.py                # 困难AI：Alpha-Beta 4-6层
│   └── storage/
│       ├── __init__.py
│       └── replay.py              # 复盘文件读写
├── frontend/
│   ├── index.html                 # 开始页面
│   ├── game.html                  # 对弈页面
│   ├── replay.html                # 复盘页面
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css          # 3D立体棋子样式
│   │   └── js/
│   │       ├── api.js             # API调用封装
│   │       ├── board.js           # 棋盘渲染
│   │       ├── game.js            # 对弈逻辑
│   │       └── replay.js          # 复盘逻辑
│   └── replay.html
└── replays/                        # 复盘JSON文件目录
```

---

## Task 1: 后端基础设施 - 棋盘数据结构和棋子表示

**Files:**
- Create: `backend/game/pieces.py`
- Create: `backend/game/__init__.py`
- Test: `backend/tests/test_pieces.py`

- [ ] **Step 1: 编写棋子测试**

```python
# backend/tests/test_pieces.py
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_pieces.py -v`
Expected: FAIL - module not found

- [ ] **Step 3: 实现棋子基类和6种棋子**

```python
# backend/game/pieces.py
from enum import Enum
from typing import List, Tuple, Optional

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def opponent(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class Piece:
    def __init__(self, color: Color):
        self.color = color
        self.symbol = ""
        self.value = 0

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        raise NotImplementedError

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'P' if color == Color.WHITE else 'p'
        self.value = 1

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        file_from = ord(from_pos[0])
        rank_from = int(from_pos[1])
        file_to = ord(to_pos[0])
        rank_to = int(to_pos[1])

        direction = 1 if self.color == Color.WHITE else -1
        start_rank = 2 if self.color == Color.WHITE else 7

        # 前进一格
        if file_from == file_to and rank_to == rank_from + direction:
            return True
        # 初始两步
        if file_from == file_to and rank_from == start_rank and rank_to == rank_from + 2 * direction:
            return True
        # 吃子（斜一格）
        if abs(file_to - file_from) == 1 and rank_to == rank_from + direction:
            return True
        return False
```

- [ ] **Step 4: 实现其余5种棋子（Rook, Knight, Bishop, Queen, King）**

```python
# Rook - 车：横竖直线任意格
class Rook(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'R' if color == Color.WHITE else 'r'
        self.value = 5

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        if from_pos[0] != to_pos[0] and from_pos[1] != to_pos[1]:
            return False  # 必须同列或同行
        return True

    def get_move_squares(self, from_pos: str, board: 'Board' = None) -> List[str]:
        # 返回所有可移动到的位置（不检查路径遮挡）
        squares = []
        file_idx = ord(from_pos[0]) - ord('a')
        rank_idx = int(from_pos[1]) - 1
        # 横竖四方向
        for direction in [(0,1),(0,-1),(1,0),(-1,0)]:
            for i in range(1, 8):
                new_file = file_idx + direction[0] * i
                new_rank = rank_idx + direction[1] * i
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    squares.append(chr(ord('a') + new_file) + str(new_rank + 1))
        return squares

# Knight - 马：L形状
class Knight(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'N' if color == Color.WHITE else 'n'
        self.value = 3

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return (df == 1 and dr == 2) or (df == 2 and dr == 1)

# Bishop - 象：斜线任意格
class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'B' if color == Color.WHITE else 'b'
        self.value = 3

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return df == dr and df > 0  # 必须斜走且距离相等

# Queen - 皇后：横竖斜任意格
class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'Q' if color == Color.WHITE else 'q'
        self.value = 9

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        # 同列、同行、或对角线
        return (from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]) or (df == dr and df > 0)

# King - 国王：八方一格
class King(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
        self.symbol = 'K' if color == Color.WHITE else 'k'
        self.value = 1000

    def can_move(self, from_pos: str, to_pos: str, board: 'Board' = None) -> bool:
        df = abs(ord(to_pos[0]) - ord(from_pos[0]))
        dr = abs(int(to_pos[1]) - int(from_pos[1]))
        return df <= 1 and dr <= 1 and (df + dr > 0)  # 最多一格且不是不动
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_pieces.py -v`
Expected: PASS

- [ ] **Step 6: 提交代码**

```bash
cd backend
git add game/pieces.py game/__init__.py tests/test_pieces.py
git commit -m "feat: 实现6种棋子的数据结构和基础移动规则"
```

---

## Task 2: 棋盘类 - 完整棋盘状态管理

**Files:**
- Create: `backend/game/board.py`
- Modify: `backend/game/pieces.py` (添加辅助方法)
- Test: `backend/tests/test_board.py`

- [ ] **Step 1: 编写Board测试**

```python
# backend/tests/test_board.py
import pytest
from backend.game.board import Board
from backend.game.pieces import Color

def test_board_initialization():
    board = Board()
    assert board.turn == Color.WHITE
    # 检查初始布局
    assert board.get_piece("a1").symbol == "R"  # 白车
    assert board.get_piece("e1").symbol == "K"  # 白王
    assert board.get_piece("d1").symbol == "Q"  # 白后
    assert board.get_piece("a8").symbol == "r"  # 黑车
    assert board.get_piece("e8").symbol == "k"  # 黑王

def test_get_piece():
    board = Board()
    piece = board.get_piece("e2")
    assert piece.symbol == "P"  # 白兵

def test_pos_to_coords():
    from backend.game.board import Board
    assert Board.pos_to_coords("a1") == (0, 0)
    assert Board.pos_to_coords("h8") == (7, 7)
    assert Board.pos_to_coords("e4") == (4, 3)

def test_coords_to_pos():
    from backend.game.board import Board
    assert Board.coords_to_pos(0, 0) == "a1"
    assert Board.coords_to_pos(4, 3) == "e4"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_board.py -v`
Expected: FAIL - module not found

- [ ] **Step 3: 实现Board类**

```python
# backend/game/board.py
from typing import Dict, List, Optional, Tuple
from .pieces import (
    Piece, Pawn, Rook, Knight, Bishop, Queen, King, Color
)

class Board:
    def __init__(self):
        self.squares: Dict[str, Optional[Piece]] = {}
        self.turn = Color.WHITE
        self.move_history: List[dict] = []
        self.castling_rights = {
            Color.WHITE: {"K": True, "Q": True},  # 白方短易位、长易位
            Color.BLACK: {"k": True, "q": True},  # 黑方短易位、长易位
        }
        self.en_passant_target: Optional[str] = None  # 吃过路兵的目标格
        self.halfmove_clock: int = 0  # 半回合计数（用于和棋判定）
        self._initialize_board()

    def _initialize_board(self):
        # 初始化8x8棋盘
        for file in 'abcdefgh':
            for rank in '12345678':
                pos = file + rank
                self.squares[pos] = None

        # 放置棋子
        # 白方
        self.squares['a1'] = Rook(Color.WHITE)
        self.squares['b1'] = Knight(Color.WHITE)
        self.squares['c1'] = Bishop(Color.WHITE)
        self.squares['d1'] = Queen(Color.WHITE)
        self.squares['e1'] = King(Color.WHITE)
        self.squares['f1'] = Bishop(Color.WHITE)
        self.squares['g1'] = Knight(Color.WHITE)
        self.squares['h1'] = Rook(Color.WHITE)
        for file in 'abcdefgh':
            self.squares[file + '2'] = Pawn(Color.WHITE)

        # 黑方
        self.squares['a8'] = Rook(Color.BLACK)
        self.squares['b8'] = Knight(Color.BLACK)
        self.squares['c8'] = Bishop(Color.BLACK)
        self.squares['d8'] = Queen(Color.BLACK)
        self.squares['e8'] = King(Color.BLACK)
        self.squares['f8'] = Bishop(Color.BLACK)
        self.squares['g8'] = Knight(Color.BLACK)
        self.squares['h8'] = Rook(Color.BLACK)
        for file in 'abcdefgh':
            self.squares[file + '7'] = Pawn(Color.BLACK)

    @staticmethod
    def pos_to_coords(pos: str) -> Tuple[int, int]:
        """将位置字符串（如'e4'）转换为坐标(列, 行)"""
        file_idx = ord(pos[0]) - ord('a')
        rank_idx = int(pos[1]) - 1
        return file_idx, rank_idx

    @staticmethod
    def coords_to_pos(file_idx: int, rank_idx: int) -> str:
        """将坐标转换为位置字符串"""
        return chr(ord('a') + file_idx) + str(rank_idx + 1)

    def get_piece(self, pos: str) -> Optional[Piece]:
        """获取指定位置的棋子"""
        return self.squares.get(pos)

    def set_piece(self, pos: str, piece: Optional[Piece]):
        """设置指定位置的棋子"""
        self.squares[pos] = piece

    def remove_piece(self, pos: str) -> Optional[Piece]:
        """移除并返回指定位置的棋子"""
        piece = self.squares[pos]
        self.squares[pos] = None
        return piece

    def is_empty(self, pos: str) -> bool:
        """检查位置是否为空"""
        return self.squares[pos] is None

    def get_board_state(self) -> List[List[Optional[str]]]:
        """获取棋盘状态的2D数组表示（用于前端渲染）"""
        board = []
        for rank in range(8, 0, -1):  # 从8到1（黑方视角）
            row = []
            for file in 'abcdefgh':
                pos = file + str(rank)
                piece = self.squares[pos]
                row.append(piece.symbol if piece else None)
            board.append(row)
        return board

    def copy(self) -> 'Board':
        """创建棋盘深拷贝"""
        new_board = Board()
        new_board.squares = {pos: piece for pos, piece in self.squares.items()}
        new_board.turn = self.turn
        new_board.move_history = self.move_history.copy()
        new_board.castling_rights = {
            color: rights.copy() for color, rights in self.castling_rights.items()
        }
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        return new_board
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_board.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add game/board.py tests/test_board.py
git commit -m "feat: 实现Board类管理棋盘状态"
```

---

## Task 3: 走棋规则 - 合法性判断、王车易位、吃过路兵

**Files:**
- Create: `backend/game/rules.py`
- Test: `backend/tests/test_rules.py`

- [ ] **Step 1: 编写规则测试**

```python
# backend/tests/test_rules.py
import pytest
from backend.game.board import Board
from backend.game.rules import GameRules
from backend.game.pieces import Color

def test_king_in_check():
    board = Board()
    # 简单测试：白王在e1，黑后在e8（同列中间无子）
    rules = GameRules(board)
    # 当前局面无将军
    assert not rules.is_king_in_check(Color.WHITE)
    assert not rules.is_king_in_check(Color.BLACK)

def test_legal_move_validation():
    board = Board()
    rules = GameRules(board)
    # 白兵从e2到e4是合法的两步
    assert rules.is_legal_move("e2", "e4", Color.WHITE)
    # 但e2到e5不合法
    assert not rules.is_legal_move("e2", "e5", Color.WHITE)

def test_castling():
    board = Board()
    # 清理e1到h1之间的格子（模拟王车易位前）
    for pos in ['f1', 'g1']:
        board.set_piece(pos, None)
    rules = GameRules(board)
    # 检查能否短易位
    assert rules.can_castle(Color.WHITE, "K") == True

def test_en_passant():
    board = Board()
    rules = GameRules(board)
    # 模拟吃过路兵：白兵在e4，黑兵在d4，黑兵走到d5
    board.set_piece("e4", board.remove_piece("e2"))  # 白兵e2->e4
    board.set_piece("d4", board.remove_piece("d7"))  # 黑兵d7->d4
    # 模拟黑兵从d4走到d5，白兵从e4吃过路兵到d5
    board.turn = Color.WHITE
    assert rules.is_legal_move("e4", "d5", Color.WHITE) == True  # 吃过路兵
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_rules.py -v`
Expected: FAIL - module not found

- [ ] **Step 3: 实现GameRules类**

```python
# backend/game/rules.py
from typing import List, Optional, Tuple
from .board import Board
from .pieces import Color, Piece, Pawn, Rook, King

class GameRules:
    def __init__(self, board: Board):
        self.board = board

    def is_legal_move(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """判断某颜色的棋子从from_pos到to_pos是否合法"""
        piece = self.board.get_piece(from_pos)
        if piece is None or piece.color != color:
            return False

        # 检查目标位置是否有己方棋子
        target = self.board.get_piece(to_pos)
        if target and target.color == color:
            return False

        # 基础移动规则检查
        if not piece.can_move(from_pos, to_pos, self.board):
            return False

        # 兵的吃子规则（斜走吃子，直走不吃）
        if isinstance(piece, Pawn):
            file_same = from_pos[0] == to_pos[0]
            if file_same and not self.board.is_empty(to_pos):
                return False  # 兵直走时目标必须为空
            if not file_same and self.board.is_empty(to_pos):
                # 斜走时检查是否是吃过路兵
                if not self._is_en_passant(from_pos, to_pos, color):
                    return False

        # 王车易位检查
        if isinstance(piece, King):
            if self._is_castling(from_pos, to_pos, color):
                return True

        # 检查移动后是否会导致己方王被将军（不能送吃）
        temp_board = self.board.copy()
        temp_board.set_piece(to_pos, temp_board.remove_piece(from_pos))
        temp_rules = GameRules(temp_board)
        if temp_rules.is_king_in_check(color):
            return False

        return True

    def is_king_in_check(self, color: Color) -> bool:
        """检测指定颜色的王是否被将军"""
        # 找到王的位置
        king_pos = self._find_king(color)
        if not king_pos:
            return False

        opponent = color.opponent()
        # 检查对手所有棋子是否能攻击到王
        for pos, piece in self.board.squares.items():
            if piece and piece.color == opponent:
                if piece.can_move(pos, king_pos, self.board):
                    # 检查路径是否被遮挡（对于车、象、后的直线攻击）
                    if self._is_path_clear(pos, king_pos):
                        return True
        return False

    def _find_king(self, color: Color) -> Optional[str]:
        """找到指定颜色王的位置"""
        for pos, piece in self.board.squares.items():
            if isinstance(piece, King) and piece.color == color:
                return pos
        return None

    def _is_path_clear(self, from_pos: str, to_pos: str) -> bool:
        """检查两个位置之间的路径是否畅通（排除起点和终点）"""
        fx, fy = Board.pos_to_coords(from_pos)
        tx, ty = Board.pos_to_coords(to_pos)

        # 只处理直线和斜线路径
        dx = tx - fx
        dy = ty - fy

        if dx == 0:  # 同列
            step_x, step_y = 0, 1 if dy > 0 else -1
        elif dy == 0:  # 同行
            step_x, step_y = 1 if dx > 0 else -1, 0
        elif abs(dx) == abs(dy):  # 斜线
            step_x, step_y = 1 if dx > 0 else -1, 1 if dy > 0 else -1
        else:
            return True  # 非直线/斜线，假设畅通（用于马的跳跃）

        x, y = fx + step_x, fy + step_y
        while (x, y) != (tx, ty):
            pos = Board.coords_to_pos(x, y)
            if not self.board.is_empty(pos):
                return False
            x += step_x
            y += step_y
        return True

    def can_castle(self, color: Color, side: str) -> bool:
        """检查能否王车易位
        side: 'K'=短易位(王翼), 'Q'=长易位(后翼)
        """
        rank = '1' if color == Color.WHITE else '8'
        king_pos = f'e{rank}'

        # 检查王是否动过
        if not self.board.castling_rights[color][side.upper()]:
            return False

        # 检查王是否在被将军位置
        if self.is_king_in_check(color):
            return False

        if side.upper() == 'K':  # 短易位
            rook_pos = f'h{rank}'
            if not isinstance(self.board.get_piece(rook_pos), Rook):
                return False
            # 检查f,g格是否为空且王不过被将军的位置
            for pos in [f'f{rank}', f'g{rank}']:
                if not self.board.is_empty(pos):
                    return False
            # 王不能经过被将军的位置
            king_pos_list = [f'e{rank}', f'f{rank}', f'g{rank}']
        else:  # 长易位
            rook_pos = f'a{rank}'
            if not isinstance(self.board.get_piece(rook_pos), Rook):
                return False
            # 检查b,c,d格是否为空
            for pos in [f'b{rank}', f'c{rank}', f'd{rank}']:
                if not self.board.is_empty(pos):
                    return False
            king_pos_list = [f'e{rank}', f'd{rank}', f'c{rank}']

        # 检查王经过的格子是否被将军
        temp_board = self.board.copy()
        for i, pos in enumerate(king_pos_list[:-1]):
            temp_board.set_piece(king_pos_list[i+1], temp_board.remove_piece(pos))
            temp_rules = GameRules(temp_board)
            if temp_rules.is_king_in_check(color):
                return False

        return True

    def _is_castling(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """判断是否是王车易位"""
        piece = self.board.get_piece(from_pos)
        if not isinstance(piece, King):
            return False

        fx, fy = Board.pos_to_coords(from_pos)
        tx, ty = Board.pos_to_coords(to_pos)

        # 王只能横走一格且是易位
        if fy != ty or abs(tx - fx) != 2:
            return False

        rank = '1' if color == Color.WHITE else '8'
        if from_pos != f'e{rank}':
            return False

        side = 'K' if tx > fx else 'Q'  # tx>fx短易位，tx<fx长易位
        return self.can_castle(color, side)

    def _is_en_passant(self, from_pos: str, to_pos: str, color: Color) -> bool:
        """判断是否是吃过路兵"""
        piece = self.board.get_piece(from_pos)
        if not isinstance(piece, Pawn):
            return False

        # 兵斜走一格吃子时，如果目标是en_passant_target则是吃过路兵
        if self.board.en_passant_target == to_pos:
            return True
        return False

    def get_legal_moves(self, pos: str, color: Color) -> List[str]:
        """获取指定位置棋子的所有合法走法"""
        piece = self.board.get_piece(pos)
        if piece is None or piece.color != color:
            return []

        legal_moves = []
        for target_pos in piece.get_move_squares(pos, self.board):
            if self.is_legal_move(pos, target_pos, color):
                legal_moves.append(target_pos)
        return legal_moves

    def get_all_legal_moves(self, color: Color) -> List[Tuple[str, str]]:
        """获取指定颜色的所有合法走法"""
        all_moves = []
        for pos, piece in self.board.squares.items():
            if piece and piece.color == color:
                legal_targets = self.get_legal_moves(pos, color)
                for target in legal_targets:
                    all_moves.append((pos, target))
        return all_moves
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_rules.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add game/rules.py tests/test_rules.py
git commit -m "feat: 实现走棋规则、王车易位、吃过路兵、将死检测"
```

---

## Task 4: AI引擎 - 三种难度实现

**Files:**
- Create: `backend/ai/__init__.py`
- Create: `backend/ai/simple.py`
- Create: `backend/ai/medium.py`
- Create: `backend/ai/hard.py`
- Test: `backend/tests/test_ai.py`

- [ ] **Step 1: 编写AI测试**

```python
# backend/tests/test_ai.py
import pytest
from backend.game.board import Board
from backend.game.pieces import Color

def test_simple_ai():
    from backend.ai.simple import SimpleAI
    board = Board()
    ai = SimpleAI(board, Color.BLACK)
    move = ai.get_move()
    # 简单AI返回的是(from, to)元组
    assert move is not None
    assert len(move) == 2

def test_medium_ai():
    from backend.ai.medium import MediumAI
    board = Board()
    ai = MediumAI(board, Color.BLACK)
    move = ai.get_move()
    assert move is not None

def test_hard_ai():
    from backend.ai.hard import HardAI
    board = Board()
    ai = HardAI(board, Color.BLACK)
    move = ai.get_move()
    assert move is not None
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_ai.py -v`
Expected: FAIL

- [ ] **Step 3: 实现简单AI（随机选择）**

```python
# backend/ai/simple.py
import random
from typing import Optional, Tuple
from backend.game.board import Board
from backend.game.pieces import Color
from backend.game.rules import GameRules

class SimpleAI:
    def __init__(self, board: Board, color: Color):
        self.board = board
        self.color = color
        self.rules = GameRules(board)

    def get_move(self) -> Optional[Tuple[str, str]]:
        """随机选择一个合法走法"""
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None
        return random.choice(legal_moves)
```

- [ ] **Step 4: 实现中等AI（Minimax 2-3层）**

```python
# backend/ai/medium.py
from typing import Optional, Tuple, List
from backend.game.board import Board
from backend.game.pieces import Color, Piece
from backend.game.rules import GameRules
import random

class MediumAI:
    def __init__(self, board: Board, color: Color, depth: int = 2):
        self.board = board
        self.color = color
        self.depth = depth
        self.rules = GameRules(board)

    def get_move(self) -> Optional[Tuple[str, str]]:
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None

        best_score = float('-inf')
        best_moves = []

        for from_pos, to_pos in legal_moves:
            new_board = self._simulate_move(from_pos, to_pos)
            score = self._minimax(new_board, self.depth - 1, False)

            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)]
            elif score == best_score:
                best_moves.append((from_pos, to_pos))

        return random.choice(best_moves)

    def _minimax(self, board: Board, depth: int, is_maximizing: bool) -> float:
        if depth == 0:
            return self._evaluate(board)

        rules = GameRules(board)
        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = rules.get_all_legal_moves(color)

        if not legal_moves:
            # 无合法走法
            if rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0  # 困毙（和棋）

        if is_maximizing:
            best_score = float('-inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._minimax(new_board, depth - 1, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._minimax(new_board, depth - 1, True)
                best_score = min(best_score, score)
            return best_score

    def _evaluate(self, board: Board) -> float:
        """简单局面评估：棋子价值总和"""
        score = 0
        for pos, piece in board.squares.items():
            if piece:
                value = piece.value
                if piece.color == self.color:
                    score += value
                else:
                    score -= value
        return score

    def _simulate_move(self, from_pos: str, to_pos: str) -> Board:
        """模拟走棋并返回新棋盘"""
        return self._simulate_move_on_board(self.board, from_pos, to_pos)

    def _simulate_move_on_board(self, board: Board, from_pos: str, to_pos: str) -> Board:
        """在给定棋盘上模拟走棋"""
        new_board = board.copy()
        piece = new_board.remove_piece(from_pos)
        new_board.set_piece(to_pos, piece)
        new_board.turn = board.turn.opponent()
        return new_board
```

- [ ] **Step 5: 实现困难AI（Alpha-Beta 4-6层）**

```python
# backend/ai/hard.py
from typing import Optional, Tuple, List
from backend.game.board import Board
from backend.game.pieces import Color, Piece
from backend.game.rules import GameRules
import random

class HardAI:
    def __init__(self, board: Board, color: Color, depth: int = 4):
        self.board = board
        self.color = color
        self.depth = depth
        self.rules = GameRules(board)

    def get_move(self) -> Optional[Tuple[str, str]]:
        legal_moves = self.rules.get_all_legal_moves(self.color)
        if not legal_moves:
            return None

        best_score = float('-inf')
        best_moves = []

        for from_pos, to_pos in legal_moves:
            new_board = self._simulate_move(from_pos, to_pos)
            score = self._alphabeta(new_board, self.depth - 1, float('-inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)]
            elif score == best_score:
                best_moves.append((from_pos, to_pos))

        return random.choice(best_moves)

    def _alphabeta(self, board: Board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        if depth == 0:
            return self._evaluate(board)

        rules = GameRules(board)
        color = self.color if is_maximizing else self.color.opponent()
        legal_moves = rules.get_all_legal_moves(color)

        if not legal_moves:
            if rules.is_king_in_check(color):
                return float('-inf') if is_maximizing else float('inf')
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._alphabeta(new_board, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta剪枝
            return best_score
        else:
            best_score = float('inf')
            for from_pos, to_pos in legal_moves:
                new_board = self._simulate_move_on_board(board, from_pos, to_pos)
                score = self._alphabeta(new_board, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha剪枝
            return best_score

    def _evaluate(self, board: Board) -> float:
        """改进的评估函数：棋子价值 + 位置价值"""
        piece_square_table = self._get_piece_square_table()
        score = 0

        for pos, piece in board.squares.items():
            if piece:
                # 基础价值
                value = piece.value * 100
                # 位置价值
                if piece.color == self.color:
                    score += value + piece_square_table.get(piece.symbol, {}).get(pos, 0)
                else:
                    score -= value + piece_square_table.get(piece.symbol.upper(), {}).get(pos, 0)

        return score

    def _get_piece_square_table(self) -> dict:
        """棋子位置价值表（简化版）"""
        # P=兵, R=车, N=马, B=象, Q=后, K=王
        pawn_table = {
            'a': [0, 0, 0, 0, 0, 0, 0, 0],
            'b': [0, 0, 0, 0, 0, 0, 0, 0],
            'c': [0, 0, 0, 0, 0, 0, 0, 0],
            'd': [0, 0, 0, 0, 0, 0, 0, 0],
            'e': [0, 0, 0, 0, 0, 0, 0, 0],
            'f': [0, 0, 0, 0, 0, 0, 0, 0],
            'g': [0, 0, 0, 0, 0, 0, 0, 0],
            'h': [0, 0, 0, 0, 0, 0, 0, 0],
        }
        return {
            'P': pawn_table,
            'p': pawn_table,
            'R': {}, 'r': {},
            'N': {}, 'n': {},
            'B': {}, 'b': {},
            'Q': {}, 'q': {},
            'K': {}, 'k': {},
        }

    def _simulate_move(self, from_pos: str, to_pos: str) -> Board:
        return self._simulate_move_on_board(self.board, from_pos, to_pos)

    def _simulate_move_on_board(self, board: Board, from_pos: str, to_pos: str) -> Board:
        new_board = board.copy()
        piece = new_board.remove_piece(from_pos)
        new_board.set_piece(to_pos, piece)
        new_board.turn = board.turn.opponent()
        return new_board
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_ai.py -v`
Expected: PASS

- [ ] **Step 7: 提交代码**

```bash
git add ai/__init__.py ai/simple.py ai/medium.py ai/hard.py tests/test_ai.py
git commit -m "feat: 实现三种难度AI引擎"
```

---

## Task 5: 复盘存储

**Files:**
- Create: `backend/storage/replay.py`
- Create: `backend/storage/__init__.py`
- Test: `backend/tests/test_replay.py`

- [ ] **Step 1: 编写复盘测试**

```python
# backend/tests/test_replay.py
import pytest
import os
import tempfile
from backend.storage.replay import ReplayStorage

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        replay_data = {
            "id": "test-123",
            "moves": [{"from": "e2", "to": "e4"}],
            "result": "white_win"
        }
        storage.save(replay_data)
        loaded = storage.load("test-123")
        assert loaded["id"] == "test-123"
        assert len(loaded["moves"]) == 1

def test_list_replays():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        storage.save({"id": "game-1", "moves": []})
        storage.save({"id": "game-2", "moves": []})
        replays = storage.list()
        assert len(replays) == 2
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_replay.py -v`
Expected: FAIL

- [ ] **Step 3: 实现复盘存储**

```python
# backend/storage/replay.py
import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime

class ReplayStorage:
    def __init__(self, storage_dir: str = "replays"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save(self, replay_data: Dict) -> str:
        """保存复盘数据，返回ID"""
        if "id" not in replay_data:
            replay_data["id"] = str(uuid.uuid4())[:8]
        if "created_at" not in replay_data:
            replay_data["created_at"] = datetime.now().isoformat()

        filepath = os.path.join(self.storage_dir, f"{replay_data['id']}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, ensure_ascii=False, indent=2)
        return replay_data["id"]

    def load(self, replay_id: str) -> Optional[Dict]:
        """加载指定ID的复盘"""
        filepath = os.path.join(self.storage_dir, f"{replay_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list(self) -> List[Dict]:
        """列出所有复盘"""
        replays = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    replays.append(json.load(f))
        return sorted(replays, key=lambda x: x.get('created_at', ''), reverse=True)

    def delete(self, replay_id: str) -> bool:
        """删除指定复盘"""
        filepath = os.path.join(self.storage_dir, f"{replay_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_replay.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add storage/replay.py storage/__init__.py tests/test_replay.py
git commit -m "feat: 实现复盘存储功能"
```

---

## Task 6: FastAPI 后端路由

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: 编写API测试**

```python
# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_start_game():
    response = client.post("/api/game/start", json={"difficulty": "medium"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["turn"] == "white"

def test_invalid_move():
    client.post("/api/game/start", json={"difficulty": "medium"})
    response = client.post("/api/game/move", json={"from": "e2", "to": "e5"})
    assert response.status_code == 200
    data = response.json()
    assert data["legal"] == False
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: FAIL

- [ ] **Step 3: 实现FastAPI主程序**

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

from game.board import Board
from game.pieces import Color
from game.rules import GameRules
from ai.simple import SimpleAI
from ai.medium import MediumAI
from ai.hard import HardAI
from storage.replay import ReplayStorage

app = FastAPI(title="Chess Game API")

# 游戏状态存储（生产环境用Redis等）
games: dict = {}
replay_storage = ReplayStorage()

class StartGameRequest(BaseModel):
    difficulty: str  # simple, medium, hard

class MoveRequest(BaseModel):
    game_id: str
    from_pos: str
    to_pos: str

class GameState(BaseModel):
    game_id: str
    board: List[List[Optional[str]]]
    turn: str
    check: bool
    game_over: bool
    result: Optional[str]
    legal_moves: dict

@app.post("/api/game/start")
def start_game(req: StartGameRequest):
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
    game = games.get(req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    rules = GameRules(board)
    color = Color.WHITE  # 玩家总是白方

    # 验证走法合法性
    if not rules.is_legal_move(req.from_pos, req.to_pos, color):
        return {"legal": False, "reason": "illegal move"}

    # 执行走棋
    piece = board.remove_piece(req.from_pos)
    captured = board.get_piece(req.to_pos)
    board.set_piece(req.to_pos, piece)

    # 记录历史
    game["move_history"].append({
        "from": req.from_pos,
        "to": req.to_pos,
        "piece": piece.symbol,
        "captured": captured.symbol if captured else None,
    })

    # 切换回合
    board.turn = Color.BLACK

    # 检查游戏是否结束
    black_moves = rules.get_all_legal_moves(Color.BLACK)
    black_in_check = rules.is_king_in_check(Color.BLACK)

    result = None
    game_over = False
    if not black_moves:
        game_over = True
        result = "white_win" if black_in_check else "draw"

    # AI走棋
    ai_move = None
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

        # 再次检查游戏结束
        white_moves = rules.get_all_legal_moves(Color.WHITE)
        white_in_check = rules.is_king_in_check(Color.WHITE)
        if not white_moves:
            game_over = True
            result = "black_win" if white_in_check else "draw"

    # 获取白方合法走法
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
    # 撤销最后两步（玩家+AI）
    if len(game["move_history"]) >= 2:
        game["move_history"] = game["move_history"][:-2]
        # 重新构建棋盘（简化处理：重新初始化）
        game["board"] = Board()
        # TODO: 重新应用历史走法
    return {"success": True}

@app.get("/api/replay/list")
def list_replays():
    replays = replay_storage.list()
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

    # 判断结果
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
```

- [ ] **Step 4: 创建requirements.txt**

```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
pytest==7.4.0
httpx==0.26.0
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 6: 提交代码**

```bash
git add main.py requirements.txt
git commit -m "feat: 实现FastAPI后端路由"
```

---

## Task 7: 前端 - 开始页面和棋盘渲染

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/static/css/style.css`
- Create: `frontend/static/js/api.js`

- [ ] **Step 1: 创建index.html（开始页面）**

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>国际象棋 - 人机对弈</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>♔ 国际象棋 ♚</h1>
        <p class="subtitle">人机对弈</p>

        <div class="difficulty-selection">
            <h2>选择难度</h2>
            <div class="difficulty-buttons">
                <button class="btn difficulty-btn" data-difficulty="simple">
                    <span class="difficulty-icon">🌱</span>
                    <span class="difficulty-name">简单</span>
                    <span class="difficulty-desc">随机走法</span>
                </button>
                <button class="btn difficulty-btn" data-difficulty="medium">
                    <span class="difficulty-icon">🌳</span>
                    <span class="difficulty-name">中等</span>
                    <span class="difficulty-desc">Minimax 2层</span>
                </button>
                <button class="btn difficulty-btn" data-difficulty="hard">
                    <span class="difficulty-icon">🏔️</span>
                    <span class="difficulty-name">困难</span>
                    <span class="difficulty-desc">Alpha-Beta 4层</span>
                </button>
            </div>
        </div>

        <div class="actions">
            <button id="startBtn" class="btn btn-primary" disabled>开始游戏</button>
        </div>

        <div class="history-link">
            <a href="replay.html">📜 查看复盘记录</a>
        </div>
    </div>

    <script src="static/js/api.js"></script>
    <script>
        let selectedDifficulty = null;

        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedDifficulty = btn.dataset.difficulty;
                document.getElementById('startBtn').disabled = false;
            });
        });

        document.getElementById('startBtn').addEventListener('click', async () => {
            if (!selectedDifficulty) return;
            const state = await API.startGame(selectedDifficulty);
            sessionStorage.setItem('game_id', state.game_id);
            sessionStorage.setItem('difficulty', selectedDifficulty);
            window.location.href = 'game.html';
        });
    </script>
</body>
</html>
```

- [ ] **Step 2: 创建CSS样式（3D立体棋子）**

```css
/* frontend/static/css/style.css */
:root {
    --board-light: #f0d9b5;
    --board-dark: #b58863;
    --highlight: #829769;
    --check-highlight: #e74c3c;
    --selected: #f6f669;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    text-align: center;
    color: #ecf0f1;
}

h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
    font-size: 1.2rem;
    color: #bdc3c7;
    margin-bottom: 2rem;
}

.difficulty-selection h2 {
    margin-bottom: 1rem;
}

.difficulty-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.difficulty-btn {
    background: linear-gradient(145deg, #34495e, #2c3e50);
    border: 2px solid #4a5f7f;
    border-radius: 12px;
    padding: 1.5rem;
    color: #ecf0f1;
    cursor: pointer;
    transition: all 0.3s;
    min-width: 140px;
}

.difficulty-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.difficulty-btn.selected {
    border-color: #3498db;
    background: linear-gradient(145deg, #3d566e, #2c3e50);
    box-shadow: 0 0 15px rgba(52, 152, 219, 0.4);
}

.difficulty-icon {
    font-size: 2rem;
    display: block;
}

.difficulty-name {
    font-size: 1.2rem;
    font-weight: bold;
    display: block;
    margin-top: 0.5rem;
}

.difficulty-desc {
    font-size: 0.85rem;
    color: #95a5a6;
    display: block;
    margin-top: 0.25rem;
}

.btn {
    padding: 0.8rem 2rem;
    font-size: 1rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: linear-gradient(145deg, #27ae60, #2ecc71);
    color: white;
    font-size: 1.2rem;
    margin-top: 2rem;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.4);
}

.btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.actions {
    margin-top: 1rem;
}

.history-link {
    margin-top: 2rem;
}

.history-link a {
    color: #3498db;
    text-decoration: none;
}

.history-link a:hover {
    text-decoration: underline;
}

/* 棋盘样式 */
.board-container {
    margin: 2rem auto;
}

.board {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    width: 480px;
    height: 480px;
    border: 4px solid #2c3e50;
    border-radius: 4px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.square {
    width: 60px;
    height: 60px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 2.8rem;
    cursor: pointer;
    position: relative;
}

.square.light {
    background: linear-gradient(145deg, #f5e1a4, #e6c88a);
}

.square.dark {
    background: linear-gradient(145deg, #c9a86c, #b58863);
}

.square.selected {
    background: var(--selected) !important;
}

.square.legal-move::after {
    content: '';
    width: 16px;
    height: 16px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 50%;
    position: absolute;
}

.square.last-move {
    box-shadow: inset 0 0 0 3px rgba(255, 255, 0, 0.5);
}

.square.check {
    background: radial-gradient(circle, #e74c3c 0%, #c0392b 100%) !important;
}

/* 棋子样式 - 3D立体效果 */
.piece {
    font-size: 2.8rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    filter: drop-shadow(0 3px 3px rgba(0,0,0,0.3));
    transition: transform 0.1s;
}

.piece.white {
    color: #ffffff;
    text-shadow:
        1px 1px 0 #d0d0d0,
        2px 2px 4px rgba(0,0,0,0.3),
        0 0 8px rgba(255,255,255,0.3);
}

.piece.black {
    color: #1a1a1a;
    text-shadow:
        1px 1px 0 #4a4a4a,
        2px 2px 4px rgba(0,0,0,0.5),
        0 0 8px rgba(0,0,0,0.2);
}

/* 游戏信息栏 */
.game-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 480px;
    margin: 1rem auto;
    padding: 1rem;
    background: rgba(44, 62, 80, 0.8);
    border-radius: 8px;
}

.turn-indicator {
    font-size: 1.2rem;
    font-weight: bold;
}

.turn-indicator.white-turn {
    color: #fff;
}

.turn-indicator.black-turn {
    color: #aaa;
}

.game-controls {
    display: flex;
    gap: 0.5rem;
}

.game-controls .btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background: #34495e;
    color: #ecf0f1;
}

.game-controls .btn:hover {
    background: #4a5f7f;
}

/* 被吃棋子 */
.captured-pieces {
    width: 480px;
    margin: 0 auto;
    min-height: 40px;
    padding: 0.5rem;
    background: rgba(44, 62, 80, 0.6);
    border-radius: 4px;
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
}

.captured-pieces span {
    font-size: 1.5rem;
}
```

- [ ] **Step 3: 创建api.js**

```javascript
// frontend/static/js/api.js
const API = {
    baseUrl: 'http://localhost:8000',

    async startGame(difficulty) {
        const res = await fetch(`${this.baseUrl}/api/game/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({difficulty})
        });
        return res.json();
    },

    async makeMove(gameId, from, to) {
        const res = await fetch(`${this.baseUrl}/api/game/move`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId, from_pos: from, to_pos: to})
        });
        return res.json();
    },

    async getState(gameId) {
        const res = await fetch(`${this.baseUrl}/api/game/state/${gameId}`);
        return res.json();
    },

    async undoMove(gameId) {
        const res = await fetch(`${this.baseUrl}/api/game/undo`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId})
        });
        return res.json();
    },

    async getReplayList() {
        const res = await fetch(`${this.baseUrl}/api/replay/list`);
        return res.json();
    },

    async getReplay(replayId) {
        const res = await fetch(`${this.baseUrl}/api/replay/${replayId}`);
        return res.json();
    },

    async saveReplay(gameId) {
        const res = await fetch(`${this.baseUrl}/api/replay/save`, {
            method: 'POST',
            headers:{'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId})
        });
        return res.json();
    }
};
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/index.html frontend/static/css/style.css frontend/static/js/api.js
git commit -m "feat: 前端开始页面和3D棋子样式"
```

---

## Task 8: 前端 - 对弈页面和复盘页面

**Files:**
- Create: `frontend/game.html`
- Create: `frontend/static/js/board.js`
- Create: `frontend/static/js/game.js`
- Create: `frontend/replay.html`
- Create: `frontend/static/js/replay.js`

- [ ] **Step 1: 创建board.js（棋盘渲染）**

```javascript
// frontend/static/js/board.js
class ChessBoard {
    constructor(container) {
        this.container = container;
        this.selectedSquare = null;
        this.legalMoves = [];
        this.lastMove = null;
        this.onSquareClick = null;
    }

    render(boardState, turn) {
        this.container.innerHTML = '';
        const board = document.createElement('div');
        board.className = 'board';

        // 从黑方视角渲染（黑方在下）
        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                const square = document.createElement('div');
                const isLight = (file + rank) % 2 === 0;
                square.className = `square ${isLight ? 'light' : 'dark'}`;
                square.dataset.pos = this.coordsToPos(file, rank);

                const piece = boardState[rank][file];
                if (piece) {
                    const pieceSpan = document.createElement('span');
                    pieceSpan.className = `piece ${this.getPieceColor(piece)}`;
                    pieceSpan.textContent = this.getPieceUnicode(piece);
                    square.appendChild(pieceSpan);
                }

                // 高亮
                if (this.selectedSquare === square.dataset.pos) {
                    square.classList.add('selected');
                }
                if (this.legalMoves.includes(square.dataset.pos)) {
                    square.classList.add('legal-move');
                }
                if (this.lastMove && (this.lastMove.includes(square.dataset.pos))) {
                    square.classList.add('last-move');
                }

                square.addEventListener('click', () => {
                    if (this.onSquareClick) {
                        this.onSquareClick(square.dataset.pos);
                    }
                });

                board.appendChild(square);
            }
        }

        this.container.appendChild(board);
    }

    coordsToPos(file, rank) {
        return String.fromCharCode(97 + file) + (rank + 1);
    }

    posToCoords(pos) {
        return [pos.charCodeAt(0) - 97, parseInt(pos[1]) - 1];
    }

    getPieceUnicode(symbol) {
        const pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        return pieces[symbol] || '';
    }

    getPieceColor(symbol) {
        return symbol === symbol.toUpperCase() ? 'white' : 'black';
    }

    setSelected(pos) {
        this.selectedSquare = pos;
    }

    setLegalMoves(moves) {
        this.legalMoves = moves || [];
    }

    setLastMove(from, to) {
        this.lastMove = [from, to];
    }
}
```

- [ ] **Step 2: 创建game.js（对弈逻辑）**

```javascript
// frontend/static/js/game.js
class ChessGame {
    constructor() {
        this.gameId = sessionStorage.getItem('game_id');
        this.difficulty = sessionStorage.getItem('difficulty');
        this.board = new ChessBoard(document.getElementById('board-container'));
        this.state = null;
        this.isMyTurn = true;

        this.init();
    }

    async init() {
        if (!this.gameId) {
            window.location.href = 'index.html';
            return;
        }

        // 获取初始状态
        this.state = await API.getState(this.gameId);
        this.render();

        // 设置棋盘点击回调
        this.board.onSquareClick = (pos) => this.handleSquareClick(pos);
    }

    async handleSquareClick(pos) {
        if (!this.isMyTurn) return;

        // 如果点击的是已选中的格子，取消选中
        if (this.board.selectedSquare === pos) {
            this.board.setSelected(null);
            this.board.setLegalMoves([]);
            this.board.render(this.state.board, this.state.turn);
            return;
        }

        // 如果点击的是合法走法目标，执行走棋
        if (this.board.legalMoves.includes(pos)) {
            await this.makeMove(this.board.selectedSquare, pos);
            return;
        }

        // 选中棋子
        const piece = this.getPieceAt(pos);
        if (piece && this.isWhitePiece(piece)) {
            this.board.setSelected(pos);
            const moves = this.state.legal_moves[pos] || [];
            this.board.setLegalMoves(moves);
            this.board.render(this.state.board, this.state.turn);
        }
    }

    async makeMove(from, to) {
        this.isMyTurn = false;
        this.board.setSelected(null);
        this.board.setLegalMoves([]);

        const result = await API.makeMove(this.gameId, from, to);
        this.state.board = result.board;
        this.state.turn = result.turn;
        this.state.check = result.check;
        this.state.legal_moves = result.legal_moves;

        // 更新最后一步
        if (result.ai_move) {
            this.board.setLastMove(result.ai_move[0], result.ai_move[1]);
        } else {
            this.board.setLastMove(from, to);
        }

        this.render();

        if (result.game_over) {
            this.showGameOver(result.result);
            return;
        }

        // AI走棋后更新
        if (result.ai_move) {
            // AI已走棋，更新局面
            this.state.board = result.board;
            this.state.turn = result.turn;
            this.state.legal_moves = result.legal_moves;
            this.board.setLastMove(result.ai_move[0], result.ai_move[1]);
            this.render();
        }

        this.isMyTurn = true;
    }

    getPieceAt(pos) {
        const [file, rank] = this.board.posToCoords(pos);
        return this.state.board[7 - rank][file]; // 转换坐标
    }

    isWhitePiece(symbol) {
        return symbol && symbol === symbol.toUpperCase();
    }

    render() {
        this.board.render(this.state.board, this.state.turn);
        this.updateInfo();
    }

    updateInfo() {
        const turnEl = document.getElementById('turn-indicator');
        turnEl.textContent = this.state.turn === 'white' ? '白方回合 (你)' : '黑方回合 (AI思考...)';
        turnEl.className = `turn-indicator ${this.state.turn}-turn`;
    }

    showGameOver(result) {
        const messages = {
            'white_win': '恭喜！你赢了！',
            'black_win': 'AI获胜！',
            'draw': '和棋！'
        };
        document.getElementById('game-over-message').textContent = messages[result] || '游戏结束';
        document.getElementById('game-over-modal').style.display = 'flex';
    }

    async restart() {
        sessionStorage.removeItem('game_id');
        sessionStorage.removeItem('difficulty');
        window.location.href = 'index.html';
    }
}

// 启动游戏
const game = new ChessGame();
```

- [ ] **Step 3: 创建game.html（对弈页面）**

```html
<!-- frontend/game.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>国际象棋 - 对弈中</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>♔ 国际象棋</h1>

        <div class="game-info">
            <div class="turn-indicator" id="turn-indicator">白方回合 (你)</div>
            <div class="game-controls">
                <button class="btn" onclick="game.restart()">重新开始</button>
                <button class="btn" id="saveBtn">保存复盘</button>
            </div>
        </div>

        <div class="captured-pieces" id="captured-white"></div>
        <div class="board-container">
            <div id="board-container"></div>
        </div>
        <div class="captured-pieces" id="captured-black"></div>

        <div id="game-over-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <h2 id="game-over-message">游戏结束</h2>
                <button class="btn btn-primary" onclick="game.restart()">再来一局</button>
                <button class="btn" onclick="window.location.href='index.html'">返回主页</button>
            </div>
        </div>
    </div>

    <script src="static/js/api.js"></script>
    <script src="static/js/board.js"></script>
    <script src="static/js/game.js"></script>
</body>
</html>
```

- [ ] **Step 4: 创建replay.js和replay.html**

```javascript
// frontend/static/js/replay.js
class ReplayView {
    constructor() {
        this.replays = [];
        this.currentReplay = null;
        this.currentMoveIndex = 0;
        this.board = new ChessBoard(document.getElementById('board-container'));
        this.init();
    }

    async init() {
        this.replays = await API.getReplayList();
        this.renderList();
    }

    renderList() {
        const listEl = document.getElementById('replay-list');
        if (this.replays.length === 0) {
            listEl.innerHTML = '<p class="no-replays">暂无复盘记录</p>';
            return;
        }

        listEl.innerHTML = this.replays.map(r => `
            <div class="replay-item" onclick="replayView.loadReplay('${r.id}')">
                <span class="replay-id">#${r.id}</span>
                <span class="replay-date">${new Date(r.created_at).toLocaleString()}</span>
                <span class="replay-result">${this.getResultText(r.result)}</span>
            </div>
        `).join('');
    }

    async loadReplay(replayId) {
        this.currentReplay = await API.getReplay(replayId);
        this.currentMoveIndex = 0;
        this.board.onSquareClick = null;
        this.renderReplay();
    }

    renderReplay() {
        if (!this.currentReplay) return;

        // 构建初始棋盘
        let board = this.getInitialBoard();
        const moves = this.currentReplay.moves;

        // 应用到当前步数
        for (let i = 0; i < this.currentMoveIndex && i < moves.length; i++) {
            board = this.applyMove(board, moves[i]);
        }

        this.board.render(board, 'white');
        this.updateControls();
    }

    getInitialBoard() {
        const board = [];
        const layout = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [null, null, null, null, null, null, null, null],
            [null, null, null, null, null, null, null, null],
            [null, null, null, null, null, null, null, null],
            [null, null, null, null, null, null, null, null],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ];
        for (let r = 0; r < 8; r++) {
            board.push(layout[r].slice());
        }
        return board;
    }

    applyMove(board, move) {
        const newBoard = board.map(row => row.slice());
        const [fromFile, fromRank] = [move.from.charCodeAt(0) - 97, parseInt(move.from[1]) - 1];
        const [toFile, toRank] = [move.to.charCodeAt(0) - 97, parseInt(move.to[1]) - 1];

        newBoard[7 - toRank][toFile] = newBoard[7 - fromRank][fromFile];
        newBoard[7 - fromRank][fromFile] = null;
        return newBoard;
    }

    updateControls() {
        const moves = this.currentReplay.moves;
        document.getElementById('move-counter').textContent =
            `${this.currentMoveIndex} / ${moves.length}`;

        document.getElementById('prevBtn').disabled = this.currentMoveIndex === 0;
        document.getElementById('nextBtn').disabled = this.currentMoveIndex >= moves.length;
    }

    prevMove() {
        if (this.currentMoveIndex > 0) {
            this.currentMoveIndex--;
            this.renderReplay();
        }
    }

    nextMove() {
        if (this.currentMoveIndex < this.currentReplay.moves.length) {
            this.currentMoveIndex++;
            this.renderReplay();
        }
    }

    getResultText(result) {
        const map = {
            'player_win': '玩家获胜',
            'ai_win': 'AI获胜',
            'draw': '和棋',
            'unknown': '未知'
        };
        return map[result] || result;
    }
}

const replayView = new ReplayView();
```

```html
<!-- frontend/replay.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>国际象棋 - 复盘</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>♔ 复盘记录</h1>

        <div class="replay-layout">
            <div class="replay-list-container">
                <h2>历史棋局</h2>
                <div id="replay-list" class="replay-list"></div>
            </div>

            <div class="replay-view-container">
                <div class="board-container">
                    <div id="board-container"></div>
                </div>

                <div class="replay-controls">
                    <button class="btn" id="prevBtn" onclick="replayView.prevMove()">◀ 上一步</button>
                    <span id="move-counter">0 / 0</span>
                    <button class="btn" id="nextBtn" onclick="replayView.nextMove()">下一步 ▶</button>
                </div>
            </div>
        </div>

        <div class="back-link">
            <a href="index.html">← 返回主页</a>
        </div>
    </div>

    <script src="static/js/api.js"></script>
    <script src="static/js/board.js"></script>
    <script src="static/js/replay.js"></script>
</body>
</html>
```

- [ ] **Step 5: 提交代码**

```bash
git add frontend/game.html frontend/static/js/board.js frontend/static/js/game.js
git add frontend/replay.html frontend/static/js/replay.js
git commit -m "feat: 前端对弈页面和复盘页面"
```

---

## 实施计划完成

Plan 编写完毕。两个执行选项：

**1. Subagent-Driven（推荐）** - 我dispatch独立子任务，并行实施，快速迭代

**2. Inline Execution** - 在此会话中顺序执行，批量处理有检查点

选择哪种方式？