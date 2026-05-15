# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

HTML5网页版 + Python FastAPI 后端的人机国际象棋对弈系统。玩家执白棋对战AI。

## 技术栈

- **前端**: HTML5, CSS3 (3D立体棋子), JavaScript (ES6+)
- **后端**: Python 3.11+, FastAPI, Pydantic
- **AI算法**: 随机选择, Minimax, Alpha-Beta剪枝

## 项目结构

```
chess/
├── backend/
│   ├── main.py              # FastAPI 应用入口，路由定义
│   ├── requirements.txt      # Python 依赖
│   ├── game/
│   │   ├── pieces.py        # 棋子定义 (Pawn, Rook, Knight, Bishop, Queen, King)
│   │   ├── board.py         # 棋盘状态管理
│   │   └── rules.py         # 走棋规则、将军检测、合法移动计算
│   ├── ai/
│   │   ├── simple.py        # 简单AI (随机选择)
│   │   ├── medium.py        # 中等AI (Minimax 2层)
│   │   └── hard.py          # 困难AI (Alpha-Beta 4层 + 走法排序)
│   ├── storage/
│   │   └── replay.py        # 复盘存储
│   └── tests/
│       ├── test_rules.py    # 走棋规则测试
│       └── test_api.py      # API测试
├── frontend/
│   ├── index.html           # 开始页面
│   ├── game.html            # 对弈页面
│   ├── replay.html          # 复盘页面
│   └── static/
│       ├── css/style.css    # 样式
│       └── js/
│           ├── api.js       # API调用封装
│           ├── board.js     # 棋盘渲染 (ChessBoard类)
│           ├── game.js      # 对弈逻辑 (ChessGame类)
│           ├── sound.js     # Web Audio API 音效
│           └── replay.js    # 复盘逻辑
└── replays/                 # 复盘JSON文件
```

## 常用命令

### 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 运行测试
```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

### 运行单个测试
```bash
PYTHONPATH=. python -m pytest backend/tests/test_rules.py::test_get_legal_moves -v
```

### 一键启动 (Windows)
双击根目录的 `start_full.bat` 启动完整服务（后端 + 前端HTTP服务器 + 浏览器）

### 前端开发
前端无需编译，直接修改文件后刷新浏览器即可。API base URL 在 `frontend/static/js/api.js` 中配置。

## API 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/game/start` | 开始新游戏 |
| POST | `/api/game/move` | 玩家走棋 |
| POST | `/api/game/ai_move` | 获取AI走棋 |
| GET | `/api/game/state/{game_id}` | 获取游戏状态 |
| GET | `/api/replay/list` | 复盘列表 |
| GET | `/api/replay/{replay_id}` | 获取复盘详情 |
| DELETE | `/api/replay/{replay_id}` | 删除复盘 |

## 架构要点

### 坐标系统 (重要!)

**后端棋盘表示**: `board.squares` 是字典，key为 `'a1'` 到 `'h8'` 字符串
**前端棋盘表示**: `boardState` 是二维数组 `board[rank][file]`

| 数组索引 | rank值 | 说明 |
|---------|--------|------|
| board[0] | rank 8 | 棋盘顶行 |
| board[6] | rank 2 | 棋盘第2行 |
| board[7] | rank 1 | 棋盘底行 |

**board.js 坐标转换函数** (所有参数都是**数组索引 0-7**):
- `coordsToPos(file, rank)` - file/rank是数组索引，如 `coordsToPos(4, 6)` → `'e2'` (file=4即e列，rank=6即第2行)
- `posToCoords('e2')` → `[4, 6]`，返回数组索引

### API 请求/响应

**MoveRequest**:
```python
{
    "game_id": str,
    "from_pos": str,   # 如 "e2"
    "to_pos": str,     # 如 "e4"
    "promotion": str   # 可选，升变时填 "Q"/"R"/"B"/"N"
}
```

**Move响应** (玩家走棋，包含 `promotion_required: true` 时需要二次请求):
```python
{
    "legal": bool,
    "promotion_required": bool,
    "board": List[List],
    "turn": str,        # "white" 或 "black"
    "check": bool,
    "game_over": bool,
    "result": str,      # "white_win", "black_win", "draw"
    "legal_moves": Dict[str, List[str]]
}
```

**AI Move响应** (`/api/game/ai_move`):
```python
{
    "ai_move": Tuple[str, str],  # AI的移动，如 (("g1", "f3"))
    "board": List[List],
    "turn": str,
    "check": bool,
    "game_over": bool,
    "result": str,
    "legal_moves": Dict[str, List[str]],
    "move_history": List[dict]  # 完整走棋记录
}
```

### 游戏流程

玩家走棋是**两步请求**：
1. `POST /api/game/move` - 玩家走棋，服务器返回结果
2. `POST /api/game/ai_move` - 客户端**主动调用**获取AI走棋（不是服务器推送）

客户端在收到 move 响应后，需自行调用 `ai_move` 接口获取AI的回应。

### AI 算法优化

AI模块使用 **do/undo 模式** 而非 board.copy()，避免深度复制开销:
- `_do_move(from, to)` - 执行移动，返回 `(piece, captured)`
- `_undo_move(from, to, captured, original_piece)` - 撤销移动（hard.py需要传入原始棋子处理升变）

hard.py 还使用迭代深化+转置表+MVV-LVA走法排序提升剪枝效率。

### Board 状态字段

Board 类包含以下状态字段：
- `squares` - 棋盘位置到棋子的映射
- `turn` - 当前回合 (Color.WHITE 或 Color.BLACK)
- `move_history` - 走棋记录
- `castling_rights` - 王车易位权限
- `en_passant_target` - 吃过路兵目标格
- `halfmove_clock` - 半回合计数（用于和棋判定）

### 复盘存储

- 存储位置：`backend/replays/`（使用 `Path(__file__).parent / "replays"` 绝对路径）
- 每个复盘保存为 JSON 文件，包含 `id`、`difficulty`、`moves`、`result`、`created_at`

### 游戏状态存储

- 游戏状态存在内存中（`games` 字典），非持久化
- 复盘文件持久化存储，不依赖游戏内存状态
- 生产环境应使用 Redis 等外部存储

### 棋子表示

| 符号 | 棋子 |
|------|------|
| K/k | 王 |
| Q/q | 后 |
| R/r | 车 |
| B/b | 象 |
| N/n | 马 |
| P/p | 兵 |

大写 = 白棋，小写 = 黑棋

## 功能特性

- [x] 完整走棋规则
- [x] 王车易位 (短易位/长易位)
- [x] 吃过路兵
- [x] 兵升变 (玩家选择升变棋子)
- [x] 将军检测
- [x] 将死/困毙判定
- [x] 三种AI难度
- [x] 复盘保存/回放
- [x] 实时胜率分析（基于棋子价值评估）
- [x] 音效系统（移动、吃子、将军、升变等）
- [x] 思考时间显示（困难AI）
- [x] 复盘删除功能
