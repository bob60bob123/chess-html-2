# 国际象棋游戏设计文档

## 项目概述

- **项目名称**: Chess Game (人机对弈)
- **类型**: HTML5网页版 + Python后端
- **核心功能**: 完整走棋规则、王车易位、吃过路兵、将军检测、胜负判定、AI对弈、悔棋、复盘
- **目标用户**: Chess爱好者

---

## 技术架构

```
前端(HTML5) <--HTTP REST--> Python/FastAPI后端 <--> AI引擎
                                      |
                              replay_*.json 文件
```

### 后端 (Python/FastAPI)

| 模块 | 职责 |
|------|------|
| `main.py` | FastAPI 路由，HTTP 接口 |
| `ai/` | AI 引擎（简单/中等/困难） |
| `game/` | 棋盘逻辑、棋子移动、将军检测 |
| `storage/` | 复盘文件读写 |

### 前端 (HTML5)

| 文件 | 职责 |
|------|------|
| `index.html` | 入口页（难度选择） |
| `game.html` | 对弈页面（棋盘、交互） |
| `replay.html` | 复盘页面 |
| `static/css/` | 样式（3D立体棋子） |
| `static/js/` | 前端逻辑 |

---

## 核心功能

### 1. 棋盘与棋子
- 8x8 棋盘，立体质感风格
- 6种棋子：国王、皇后、车、象、马、兵
- 棋子用 Unicode 字符或 SVG 渲染，带阴影高光

### 2. 走棋规则
- 兵的前进、吃子、升变
- 兵的吃过路兵
- 王车易位（短易位/长易位）
- 兵的升变（默认为皇后）
- 特殊规则完整性

### 3. 将军检测
- 每步走棋后检测是否将军
- 将军时高亮提示
- 将死检测（无合法走法）

### 4. 胜负判定
- 将杀：另一方被将死
- 困毙：无合法走法但未被将军（判和）
- 超出步数（可选）

### 5. AI 对弈

| 难度 | 算法 | 搜索深度 |
|------|------|---------|
| 简单 | 随机选择 | 无 |
| 中等 | Minimax | 2-3层 |
| 困难 | Alpha-Beta剪枝 | 4-6层 |

### 6. 悔棋
- 撤销最后一步（双方各一步）
- 按钮触发，后端记录完整历史

### 7. 复盘
- 保存每一步走法到 JSON 文件
- 列表查看历史棋局
- 回放功能（单步/自动播放）

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/game/start` | 开始新游戏（传入难度） |
| POST | `/api/game/move` | 走棋（传入起点终点） |
| POST | `/api/game/undo` | 悔棋 |
| GET | `/api/game/state` | 获取当前局面 |
| GET | `/api/replay/list` | 复盘列表 |
| GET | `/api/replay/{id}` | 获取复盘详情 |
| POST | `/api/replay/save` | 保存当前棋局 |

### 走棋请求/响应示例

```json
// POST /api/game/move
// Request:
{ "from": "e2", "to": "e4" }

// Response:
{
  "legal": true,
  "board": [...],
  "captured": null,
  "special": "pawn_two_step",
  "check": false,
  "game_over": false,
  "result": null
}
```

---

## 复盘数据格式

```json
{
  "id": "uuid",
  "created_at": "2026-04-04T10:00:00",
  "difficulty": "medium",
  "moves": [
    { "from": "e2", "to": "e4", "piece": "P", "captured": null },
    { "from": "e7", "to": "e5", "piece": "p", "captured": null }
  ],
  "result": "white_win",
  "winner": "player"
}
```

---

## 前端页面

### index.html（开始页面）
- 标题
- 难度选择（简单/中等/困难）
- 开始按钮
- 历史复盘入口

### game.html（对弈页面）
- 棋盘（8x8，立体质感）
- 当前回合指示
- 被吃棋子栏
- 功能按钮（悔棋、重新开始、保存复盘）
- AI思考动画

### replay.html（复盘页面）
- 历史棋局列表
- 回放控制（上一步/下一步/自动播放）
- 棋盘显示

---

## 视觉风格

### 棋盘
- 深色格/浅色格，带木纹质感
- 选中格子高亮
- 可移动目标格高亮
- 将军时国王格子红色高亮

### 棋子
- Unicode 棋子字符
- CSS 3D 效果（阴影、渐变、光泽）
- 白色棋子：银白色
- 黑色棋子：深色带光泽

---

## 文件结构

```
chess/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── simple.py
│   │   ├── medium.py
│   │   └── hard.py
│   ├── game/
│   │   ├── __init__.py
│   │   ├── board.py
│   │   ├── pieces.py
│   │   └── rules.py
│   └── storage/
│       ├── __init__.py
│       └── replay.py
├── frontend/
│   ├── index.html
│   ├── game.html
│   ├── replay.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── game.js
│           └── replay.js
└── replays/
    └── *.json
```

---

## 下一步

进入实现计划阶段。
