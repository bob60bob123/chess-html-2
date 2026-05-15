# Chess Game - 人間vs AI チェスシステム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)

[English](README_en.md) | [简体中文](README.md) | [日本語](README_ja.md) | [한국어](README_ko.md) | [Español](README_es.md)

人間vs AIチェスシステム。白棋でAIと对战できます。完全版（FastAPIバックエンド＋フロントエンド）と独立版（ピュアフロントエンド単一ファイル）の2つのモードをサポート。

## 機能

- [x] 完全なチェスルール（移動、取る）
- [x] キャスリング（短く見る/長く見る）
- [x] アンパッサン
- [x] ポーンプロモーション（プレイヤーが昇格棋子を選択）
- [x] チェック検出
- [x] チェックメイト/ステイルメイト判定
- [x] 3つのAI難易度（簡単/普通/難しい）
- [x] リアルタイム勝率分析
- [x] サウンドエフェクト
- [x] ゲームリプレイ

## クイックスタート

### 独立版（推奨、インストール不要）

[chess_all_in_one.html](chess_all_in_one.html) をブラウザで直接開く。

### 完全版

```bash
# クローン
git clone https://github.com/yourusername/chess.git
cd chess

# バックエンド起動
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Windows 即起動
.\start_full.bat
```

### テスト実行

```bash
PYTHONPATH=. python -m pytest backend/tests/ -v
```

## プロジェクト構造

```
chess/
├── chess_all_in_one.html   # 独立単一ファイル版
├── backend/                # FastAPIバックエンド
│   ├── main.py             # ルーティング
│   ├── game/               # ゲームロジック
│   │   ├── pieces.py       # 棋子定義
│   │   ├── board.py        # 棋盤状態
│   │   └── rules.py        # 動きルール
│   ├── ai/                 # AIアルゴリズム
│   │   ├── simple.py       # ランダム選択
│   │   ├── medium.py       # ミニマックス 2層
│   │   └── hard.py         # Alpha-Beta 4層
│   └── tests/              # ユニットテスト
├── frontend/              # マルチファイルフロントエンド
└── replays/               # ゲーム記録
```

## 貢献

IssueとPull Requestを歓迎します！

## ライセンス

MITライセンスで开源 - 詳細は [LICENSE](LICENSE) を参照。