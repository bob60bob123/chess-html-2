# Chess Game - Sistema de Ajedrez Humano vs IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)

[English](README_en.md) | [简体中文](README.md) | [日本語](README_ja.md) | [한국어](README_ko.md) | [Español](README_es.md)

Sistema de ajedrez humano vs IA. El jugador controla las piezas blancas contra un oponente IA. Soporta dos modos: versión completa (FastAPI backend + frontend) y versión independiente (frontend puro en un solo archivo).

## Características

- [x] Reglas completas de ajedrez (movimiento, captura)
- [x] Enroque (corto/largo)
- [x] Captura al paso
- [x] Coronación de peón (el jugador elige la pieza de promoción)
- [x] Detección de jaque
- [x] Detección de jaque mate/ahogado
- [x] Tres niveles de dificultad IA (Fácil/Medio/Difícil)
- [x] Análisis de probabilidad de victoria en tiempo real
- [x] Efectos de sonido
- [x] Repetición de partidas

## Inicio Rápido

### Versión Independiente (Recomendado, sin instalación)

Abre [chess_all_in_one.html](chess_all_in_one.html) directamente en tu navegador.

### Versión Completa

```bash
# Clonar el proyecto
git clone https://github.com/yourusername/chess.git
cd chess

# Iniciar backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Inicio rápido en Windows
.\start_full.bat
```

### Ejecutar Tests

```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

## Estructura del Proyecto

```
chess/
├── chess_all_in_one.html   # Versión independiente de archivo único
├── backend/                # Backend FastAPI
│   ├── main.py             # Rutas
│   ├── game/               # Lógica del juego
│   │   ├── pieces.py       # Definiciones de piezas
│   │   ├── board.py        # Estado del tablero
│   │   └── rules.py        # Reglas de movimiento
│   ├── ai/                 # Algoritmos de IA
│   │   ├── simple.py       # Selección aleatoria
│   │   ├── medium.py       # Minimax 2 niveles
│   │   └── hard.py         # Alpha-Beta 4 niveles
│   └── tests/              # Pruebas unitarias
├── frontend/               # Frontend multi-archivo
└── replays/                # Grabaciones de partidas
```

## Contribuir

¡Issues y Pull Requests son bienvenidos!

## Licencia

Este proyecto es código abierto bajo licencia MIT - ver archivo [LICENSE](LICENSE).