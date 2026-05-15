# Chess Game - 인간 vs AI 체스 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)

[English](README_en.md) | [简体中文](README.md) | [日本語](README_ja.md) | [한국어](README_ko.md) | [Español](README_es.md)

인간 vs AI 체스 시스템. 플레이어가 백색으로 AI와对战할 수 있습니다. 완전 버전(FastAPI 백엔드 + 프론트엔드)과 독립 버전(순수 프론트엔드 단일 파일) 두 가지 모드를 지원합니다.

## 기능

- [x] 완전한 체스 규칙 (이동, 잡기)
- [x] 캐슬링 (숏/롱)
- [x] 앙파상
- [x] 폰 프로모션 (플레이어가昇変棋子 선택)
- [x] 체크 감지
- [x] 체크메이트/스테일메이트 판정
- [x] 세 가지 AI 난이도 (쉬움/보통/어려움)
- [x] 실시간 승률 분석
- [x]音效 시스템
- [x] 게임 리플레이

## 빠른 시작

### 독립 버전 (권장, 설치 불필요)

[chess_all_in_one.html](chess_all_in_one.html)을 브라우저에서 직접 열으세요.

### 완전 버전

```bash
# 클론
git clone https://github.com/yourusername/chess.git
cd chess

# 백엔드 시작
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Windows 빠른 시작
.\start_full.bat
```

### 테스트 실행

```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

## 프로젝트 구조

```
chess/
├── chess_all_in_one.html   # 독립 단일 파일 버전
├── backend/                # FastAPI 백엔드
│   ├── main.py             # 라우팅
│   ├── game/               # 게임 로직
│   │   ├── pieces.py       #棋子 정의
│   │   ├── board.py        # 체스판 상태
│   │   └── rules.py        # 움직임 규칙
│   ├── ai/                 # AI 알고리즘
│   │   ├── simple.py       # 랜덤 선택
│   │   ├── medium.py       # 미니맥스 2층
│   │   └── hard.py         # Alpha-Beta 4층
│   └── tests/              # 유닛 테스트
├── frontend/              # 멀티 파일 프론트엔드
└── replays/               # 게임 기록
```

## 기여

Issue와 Pull Request를 환영합니다!

## 라이선스

MIT 라이선스로 오픈 소스 - 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.