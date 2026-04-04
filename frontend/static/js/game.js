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

        // Get initial state
        try {
            this.state = await API.getState(this.gameId);
            this.render();

            // Set board click callback
            this.board.onSquareClick = (pos) => this.handleSquareClick(pos);

            // Save button
            document.getElementById('saveBtn').addEventListener('click', () => this.saveGame());
        } catch (error) {
            alert('无法连接服务器！');
            window.location.href = 'index.html';
        }
    }

    async handleSquareClick(pos) {
        if (!this.isMyTurn) return;

        // Deselect if clicking same square
        if (this.board.selectedSquare === pos) {
            this.board.setSelected(null);
            this.board.setLegalMoves([]);
            this.board.render(this.state.board, this.state.turn);
            return;
        }

        // If clicking a legal move target, make the move
        if (this.board.legalMoves.includes(pos)) {
            await this.makeMove(this.board.selectedSquare, pos);
            return;
        }

        // Select piece
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

        try {
            const result = await API.makeMove(this.gameId, from, to);

            if (!result.legal) {
                // Move was rejected, refresh state
                this.state = await API.getState(this.gameId);
                this.render();
                this.isMyTurn = true;
                return;
            }

            this.state.board = result.board;
            this.state.turn = result.turn;
            this.state.check = result.check;
            this.state.legal_moves = result.legal_moves;

            // Update last move
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

            // AI has moved, update state again
            if (result.ai_move) {
                this.state.board = result.board;
                this.state.turn = result.turn;
                this.state.legal_moves = result.legal_moves;
                this.board.setLastMove(result.ai_move[0], result.ai_move[1]);
                this.render();
            }

            this.isMyTurn = true;
        } catch (error) {
            alert('移动失败！');
            this.isMyTurn = true;
        }
    }

    getPieceAt(pos) {
        const [file, rank] = this.board.posToCoords(pos);
        return this.state.board[7 - rank][file]; // Coordinate conversion
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
        if (this.state.turn === 'white') {
            turnEl.textContent = '白方回合 (你)';
            turnEl.className = 'turn-indicator white-turn';
        } else {
            turnEl.textContent = '黑方回合 (AI思考...)';
            turnEl.className = 'turn-indicator black-turn';
        }
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

    async saveGame() {
        try {
            const result = await API.saveReplay(this.gameId);
            alert('复盘已保存！');
        } catch (error) {
            alert('保存失败！');
        }
    }

    restart() {
        sessionStorage.removeItem('game_id');
        sessionStorage.removeItem('difficulty');
        window.location.href = 'index.html';
    }
}

// Start game
const game = new ChessGame();