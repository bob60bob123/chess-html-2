class ChessGame {
    constructor() {
        this.gameId = sessionStorage.getItem('game_id');
        this.difficulty = sessionStorage.getItem('difficulty');
        this.board = new ChessBoard(document.getElementById('board-container'));
        this.state = null;
        this.stateHistory = []; // 保存棋盘状态历史
        this.isMyTurn = true;
        this.thinkingTimer = null;
        this.thinkingStartTime = 0;
        this.capturedByWhite = [];
        this.capturedByBlack = [];
        this.capturedHistory = []; // 保存吃子记录历史
        this.stats = this.loadStats();

        this.init();
    }

    loadStats() {
        const saved = localStorage.getItem('chess_stats');
        return saved ? JSON.parse(saved) : { white_wins: 0, black_wins: 0, draws: 0 };
    }

    saveStats() {
        localStorage.setItem('chess_stats', JSON.stringify(this.stats));
    }

    updateWinRateDisplay() {
        const total = this.stats.white_wins + this.stats.black_wins + this.stats.draws;
        const whiteRate = total > 0 ? Math.round((this.stats.white_wins / total) * 100) : 0;
        const blackRate = total > 0 ? Math.round((this.stats.black_wins / total) * 100) : 0;
        document.getElementById('white-win-rate').textContent = whiteRate + '%';
        document.getElementById('black-win-rate').textContent = blackRate + '%';
    }

    evaluatePosition() {
        // Piece values for evaluation
        const pieceValues = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0
        };

        let whiteScore = 0;
        let blackScore = 0;

        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                const piece = this.state.board[rank][file];
                if (piece) {
                    const value = pieceValues[piece] || 0;
                    // White pieces (uppercase) add to white score, black pieces subtract
                    if (piece === piece.toUpperCase()) {
                        whiteScore += value;
                        // Bonus for pawn advancement (closer to promotion)
                        if (piece === 'P') {
                            whiteScore += (rank - 6) * 0.1; // Pawns closer to rank 8 get bonus
                        }
                    } else {
                        blackScore += Math.abs(value);
                        // Bonus for black pawn advancement (closer to rank 1)
                        if (piece === 'p') {
                            blackScore += (1 - rank) * 0.1; // Pawns closer to rank 1 get bonus
                        }
                    }
                }
            }
        }

        // King safety: penalty for exposed king
        const whiteKingPos = this.findKing('K');
        const blackKingPos = this.findKing('k');
        if (whiteKingPos) {
            const [kf, kr] = this.board.posToCoords(whiteKingPos);
            if (kr < 2) whiteScore -= 0.5; // Exposed king
        }
        if (blackKingPos) {
            const [kf, kr] = this.board.posToCoords(blackKingPos);
            if (kr > 5) blackScore -= 0.5; // Exposed king
        }

        return { whiteScore, blackScore };
    }

    findKing(pieceSymbol) {
        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                if (this.state.board[rank][file] === pieceSymbol) {
                    return this.board.coordsToPos(file, rank);
                }
            }
        }
        return null;
    }

    calculateWinProbability() {
        const { whiteScore, blackScore } = this.evaluatePosition();
        const totalAdvantage = whiteScore - blackScore;

        // Convert advantage to win probability using sigmoid-like function
        // A 10 point advantage is considered winning (roughly 2 queens)
        const probability = 1 / (1 + Math.pow(10, -totalAdvantage / 10));

        return {
            whiteWin: Math.round(probability * 100),
            blackWin: Math.round((1 - probability) * 100)
        };
    }

    updateRealTimeWinRate() {
        const { whiteWin, blackWin } = this.calculateWinProbability();
        document.getElementById('white-win-rate').textContent = whiteWin + '%';
        document.getElementById('black-win-rate').textContent = blackWin + '%';
    }

    async init() {
        if (!this.gameId) {
            window.location.href = 'index.html';
            return;
        }

        this.updateWinRateDisplay();

        try {
            this.state = await API.getState(this.gameId);
            // 保存初始状态到历史记录
            this.stateHistory.push(JSON.parse(JSON.stringify(this.state)));
            this.capturedHistory.push({ white: [...this.capturedByWhite], black: [...this.capturedByBlack] });
            this.render();
            this.board.onSquareClick = (pos) => this.handleSquareClick(pos);
        } catch (error) {
            alert('无法连接服务器！');
            window.location.href = 'index.html';
        }
    }

    async handleSquareClick(pos) {
        if (!this.isMyTurn || this.state.game_over) return;

        if (this.board.selectedSquare === pos) {
            this.board.setSelected(null);
            this.board.setLegalMoves([]);
            this.board.render(this.state.board, this.state.turn);
            return;
        }

        if (this.board.legalMoves.includes(pos)) {
            await this.makeMove(this.board.selectedSquare, pos);
            return;
        }

        const piece = this.getPieceAt(pos);
        if (piece && this.isWhitePiece(piece)) {
            this.board.setSelected(pos);
            const moves = this.state.legal_moves[pos] || [];
            this.board.setLegalMoves(moves);
            this.board.render(this.state.board, this.state.turn);
        }
    }

    async makeMove(from, to, promotion) {
        this.isMyTurn = false;
        this.board.setSelected(null);
        this.board.setLegalMoves([]);

        try {
            const result = await API.makeMove(this.gameId, from, to, promotion);

            if (!result.legal) {
                this.state = await API.getState(this.gameId);
                this.render();
                this.isMyTurn = true;
                return;
            }

            if (result.promotion_required) {
                sound.playPromotion();
                this.showPromotionDialog(from, to);
                this.isMyTurn = true;
                return;
            }

            const isCapture = this.isCapture(from, to);

            // Track captured piece (white captured black piece)
            if (isCapture) {
                const capturedPiece = this.getPieceAt(to);
                this.capturedByWhite.push(capturedPiece);
                this.renderCaptured();
            }

            this.state.board = result.board;
            this.state.turn = result.turn;
            this.state.check = result.check;
            this.state.legal_moves = result.legal_moves;
            this.state.move_history = result.move_history;
            this.board.setLastMove(result.player_move[0], result.player_move[1]);
            this.render();

            if (isCapture) {
                sound.playCapture();
            } else {
                sound.playMove();
            }

            if (result.check) {
                setTimeout(() => sound.playCheck(), 150);
            }

            if (result.game_over) {
                this.showGameOver(result.result);
                return;
            }

            this.startThinkingTimer();

            const aiResult = await API.aiMove(this.gameId);
            this.stopThinkingTimer();

            if (aiResult.ai_move) {
                const aiFrom = aiResult.ai_move[0];
                const aiTo = aiResult.ai_move[1];
                const aiIsCapture = this.isCaptureForState(aiFrom, aiTo, this.state.board);

                // Track captured piece (black captured white piece)
                if (aiIsCapture) {
                    const [file, rank] = this.board.posToCoords(aiTo);
                    const capturedPiece = this.state.board[rank][file];
                    if (capturedPiece) {
                        this.capturedByBlack.push(capturedPiece);
                        this.renderCaptured();
                    }
                }

                this.state.board = aiResult.board;
                this.state.turn = aiResult.turn;
                this.state.check = aiResult.check;
                this.state.legal_moves = aiResult.legal_moves;
                this.state.move_history = aiResult.move_history;
                this.board.setLastMove(aiFrom, aiTo);
                this.render();

                if (aiIsCapture) {
                    sound.playCapture();
                } else {
                    sound.playMove();
                }

                if (aiResult.check) {
                    setTimeout(() => sound.playCheck(), 150);
                }
            }

            if (aiResult.game_over) {
                this.showGameOver(aiResult.result);
                return;
            }

            // 保存当前状态到历史记录
            this.stateHistory.push(JSON.parse(JSON.stringify(this.state)));
            this.capturedHistory.push({ white: [...this.capturedByWhite], black: [...this.capturedByBlack] });
            this.isMyTurn = true;
        } catch (error) {
            this.stopThinkingTimer();
            alert('移动失败！');
            this.isMyTurn = true;
        }
    }

    isCapture(from, to) {
        const targetPiece = this.getPieceAt(to);
        return targetPiece !== null;
    }

    isCaptureForState(from, to, boardState) {
        const [file, rank] = this.board.posToCoords(to);
        return boardState[rank][file] !== null;
    }

    startThinkingTimer() {
        this.thinkingStartTime = Date.now();
        this.updateThinkingDisplay();
        this.thinkingTimer = setInterval(() => {
            this.updateThinkingDisplay();
            sound.playThinkTick();
        }, 1000);
    }

    stopThinkingTimer() {
        if (this.thinkingTimer) {
            clearInterval(this.thinkingTimer);
            this.thinkingTimer = null;
        }
    }

    updateThinkingDisplay() {
        const turnEl = document.getElementById('turn-indicator');
        if (this.thinkingStartTime > 0) {
            const elapsed = Math.floor((Date.now() - this.thinkingStartTime) / 1000);
            const seconds = elapsed % 60;
            const timeStr = `${seconds}s`;
            turnEl.textContent = `黑方回合`;
            turnEl.innerHTML = `黑方回合 <span class="thinking-time">(AI思考 ${timeStr})</span>`;
        }
    }

    showPromotionDialog(from, to) {
        const modal = document.getElementById('game-over-modal');
        const message = document.getElementById('game-over-message');
        const result = document.getElementById('game-over-result');

        message.textContent = '选择升变棋子';
        result.innerHTML = `
            <div class="promotion-options">
                <button class="promotion-btn" data-piece="Q">♕</button>
                <button class="promotion-btn" data-piece="R">♖</button>
                <button class="promotion-btn" data-piece="B">♗</button>
                <button class="promotion-btn" data-piece="N">♘</button>
            </div>
        `;

        document.querySelectorAll('.promotion-btn').forEach(btn => {
            btn.onclick = () => {
                const promotion = btn.dataset.piece;
                modal.style.display = 'none';
                message.textContent = '游戏结束';
                result.textContent = '';
                this.makeMove(from, to, promotion);
            };
        });

        modal.style.display = 'flex';
    }

    getPieceAt(pos) {
        const [file, rank] = this.board.posToCoords(pos);
        return this.state.board[rank][file];
    }

    isWhitePiece(symbol) {
        return symbol && symbol === symbol.toUpperCase();
    }

    render() {
        this.board.render(this.state.board, this.state.turn);
        this.updateInfo();
        this.updateRealTimeWinRate();
    }

    updateInfo() {
        const turnEl = document.getElementById('turn-indicator');
        if (this.state.turn === 'white') {
            turnEl.textContent = '白方回合';
            turnEl.className = 'turn-indicator white-turn';
        } else {
            turnEl.textContent = '黑方回合';
            turnEl.className = 'turn-indicator black-turn';
        }
    }

    renderCaptured() {
        const whiteEl = document.getElementById('captured-by-white');
        const blackEl = document.getElementById('captured-by-black');

        // White captures (black pieces) - displayed in black color
        whiteEl.className = 'captured-pieces-display white-captures';
        whiteEl.innerHTML = this.capturedByWhite.map(p => `<span>${this.getPieceUnicode(p)}</span>`).join('');

        // Black captures (white pieces) - displayed in white color
        blackEl.className = 'captured-pieces-display black-captures';
        blackEl.innerHTML = this.capturedByBlack.map(p => `<span>${this.getPieceUnicode(p)}</span>`).join('');
    }

    getPieceUnicode(symbol) {
        const pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        return pieces[symbol] || '';
    }

    showGameOver(result) {
        if (result === 'white_win') {
            sound.playVictory();
            this.stats.white_wins++;
        } else if (result === 'black_win') {
            sound.playDefeat();
            this.stats.black_wins++;
        } else if (result === 'draw') {
            this.stats.draws++;
        }
        this.saveStats();
        this.updateWinRateDisplay();

        const messages = {
            'white_win': '恭喜！你赢了！',
            'black_win': 'AI获胜！',
            'draw': '和棋！'
        };

        const message = document.getElementById('game-over-message');
        const resultEl = document.getElementById('game-over-result');

        message.textContent = messages[result] || '游戏结束';
        resultEl.textContent = '';

        document.getElementById('game-over-modal').style.display = 'flex';
    }

    async undo() {
        if (!this.isMyTurn || this.state.game_over) return;

        try {
            console.log('悔棋请求：', this.gameId);
            const result = await API.undoMove(this.gameId);
            console.log('悔棋响应：', result);

            if (result.success) {
                this.state.board = result.board;
                this.state.turn = result.turn;
                this.state.check = result.check;
                this.state.legal_moves = result.legal_moves;
                this.state.move_history = result.move_history;
                this.board.setLastMove(null, null);
                this.board.setSelected(null);
                this.board.setLegalMoves([]);
                
                // 重置吃子记录
                this.capturedByWhite = [];
                this.capturedByBlack = [];
                this.renderCaptured();
                
                this.render();
                this.isMyTurn = true;
                alert('悔棋成功！');
            } else {
                alert('无法悔棋：' + (result.reason || '未知原因'));
            }
        } catch (error) {
            console.error('悔棋错误：', error);
            alert('悔棋失败：' + error.message);
        }
    }

    restart() {
        sessionStorage.removeItem('game_id');
        sessionStorage.removeItem('difficulty');
        window.location.href = 'index.html';
    }
}

const game = new ChessGame();
