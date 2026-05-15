# Chess Game - 人机国际象棋对弈系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)

[English](README_en.md) | [简体中文](README.md) | [日本語](README_ja.md) | [한국어](README_ko.md) | [Español](README_es.md)

人机国际象棋对弈系统，玩家执白棋对战AI。支持两种运行模式：完整版（FastAPI后端+前端）和独立版（纯前端单文件）。

## 功能特点

- [x] 完整走棋规则（移动、吃子）
- [x] 王车易位 (短易位/长易位)
- [x] 吃过路兵
- [x] 兵升变 (玩家选择升变棋子)
- [x] 将军检测
- [x] 将死/困毙判定
- [x] 三种AI难度（简单/中等/困难）
- [x] 实时胜率分析
- [x] 音效系统
- [x] 游戏复盘功能

## 快速开始

### 独立版（推荐，无需安装）

直接用浏览器打开 [chess_all_in_one.html](chess_all_in_one.html) 即可运行。

### 完整版

```bash
# 克隆项目
git clone https://github.com/yourusername/chess.git
cd chess

# 启动后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Windows一键启动
.\start_full.bat
```

### 运行测试

```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

## 项目结构

```
chess/
├── chess_all_in_one.html   # 独立单文件版本
├── backend/                # FastAPI后端
│   ├── main.py             # 路由定义
│   ├── game/               # 游戏逻辑
│   │   ├── pieces.py       # 棋子定义
│   │   ├── board.py        # 棋盘状态
│   │   └── rules.py        # 走棋规则
│   ├── ai/                 # AI算法
│   │   ├── simple.py       # 随机选择
│   │   ├── medium.py       # Minimax 2层
│   │   └── hard.py         # Alpha-Beta 4层
│   └── tests/              # 单元测试
├── frontend/                # 多文件前端
└── replays/                # 游戏记录
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | HTML5, CSS3 (3D棋子), JavaScript ES6+ |
| 后端 | Python 3.11+, FastAPI, Pydantic |
| AI | 随机选择, Minimax, Alpha-Beta剪枝 |

## API路由

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/game/start` | 开始新游戏 |
| POST | `/api/game/move` | 玩家走棋 |
| POST | `/api/game/ai_move` | 获取AI走棋 |
| GET | `/api/game/state/{game_id}` | 获取游戏状态 |
| DELETE | `/api/game/{game_id}` | 删除游戏 |

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。# chess-html-2
