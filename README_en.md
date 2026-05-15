# Chess Game - Human vs AI Chess System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)

[English](README_en.md) | [简体中文](README.md) | [日本語](README_ja.md) | [한국어](README_ko.md) | [Español](README_es.md)

A human vs AI chess game system where the player controls white pieces against an AI opponent. Supports two modes: full version (FastAPI backend + frontend) and standalone version (pure frontend single file).

## Features

- [x] Complete chess rules (movement, capture)
- [x] Castling (kingside/queenside)
- [x] En passant
- [x] Pawn promotion (player chooses promotion piece)
- [x] Check detection
- [x] Checkmate/Stalemate detection
- [x] Three AI difficulty levels (Easy/Medium/Hard)
- [x] Real-time win probability analysis
- [x] Sound effects
- [x] Game replay

## Quick Start

### Standalone Version (Recommended, no installation required)

Open [chess_all_in_one.html](chess_all_in_one.html) directly in your browser.

### Full Version

```bash
# Clone the project
git clone https://github.com/yourusername/chess.git
cd chess

# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Windows quick start
.\start_full.bat
```

### Run Tests

```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

## Project Structure

```
chess/
├── chess_all_in_one.html   # Standalone single-file version
├── backend/                # FastAPI backend
│   ├── main.py             # Routes
│   ├── game/               # Game logic
│   │   ├── pieces.py       # Piece definitions
│   │   ├── board.py        # Board state
│   │   └── rules.py        # Movement rules
│   ├── ai/                 # AI algorithms
│   │   ├── simple.py       # Random selection
│   │   ├── medium.py       # Minimax 2-ply
│   │   └── hard.py         # Alpha-Beta 4-ply
│   └── tests/              # Unit tests
├── frontend/               # Multi-file frontend
└── replays/                # Game recordings
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5, CSS3 (3D pieces), JavaScript ES6+ |
| Backend | Python 3.11+, FastAPI, Pydantic |
| AI | Random, Minimax, Alpha-Beta pruning |

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/game/start` | Start new game |
| POST | `/api/game/move` | Player move |
| POST | `/api/game/ai_move` | Get AI move |
| GET | `/api/game/state/{game_id}` | Get game state |
| DELETE | `/api/game/{game_id}` | Delete game |

## Contributing

Issues and Pull Requests are welcome!

## License

This project is open source under MIT License - see [LICENSE](LICENSE) file.