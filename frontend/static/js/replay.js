class ReplayView {
    constructor() {
        this.replays = [];
        this.currentReplay = null;
        this.currentMoveIndex = 0;
        this.board = new ChessBoard(document.getElementById('board-container'));
        this.init();
    }

    async init() {
        try {
            this.replays = await API.getReplayList();
            this.renderList();
        } catch (error) {
            document.getElementById('replay-list').innerHTML = '<p class="no-replays">无法加载复盘记录</p>';
        }
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
                <button class="replay-delete-btn" onclick="event.stopPropagation(); replayView.deleteReplay('${r.id}')">×</button>
            </div>
        `).join('');
    }

    async loadReplay(replayId) {
        try {
            this.currentReplay = await API.getReplay(replayId);
            this.currentMoveIndex = 0;
            this.board.onSquareClick = null;
            this.renderReplay();
        } catch (error) {
            alert('无法加载复盘！');
        }
    }

    renderReplay() {
        if (!this.currentReplay) return;

        // Build initial board
        let board = this.getInitialBoard();
        const moves = this.currentReplay.moves;

        // Apply moves up to current index
        for (let i = 0; i < this.currentMoveIndex && i < moves.length; i++) {
            board = this.applyMove(board, moves[i]);
        }

        this.board.render(board, 'white');
        this.updateControls();
    }

    getInitialBoard() {
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
        return layout.map(row => row.slice());
    }

    applyMove(board, move) {
        const newBoard = board.map(row => row.slice());
        const [fromFile, fromRank] = [move.from.charCodeAt(0) - 97, parseInt(move.from[1]) - 1];
        const [toFile, toRank] = [move.to.charCodeAt(0) - 97, parseInt(move.to[1]) - 1];

        // Backend uses rank 8 as row 0, rank 1 as row 7
        newBoard[8 - toRank][toFile] = newBoard[8 - fromRank][fromFile];
        newBoard[8 - fromRank][fromFile] = null;
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

    async deleteReplay(replayId) {
        if (!confirm('确定要删除这条复盘记录吗？')) return;
        try {
            await API.deleteReplay(replayId);
            this.replays = this.replays.filter(r => r.id !== replayId);
            if (this.currentReplay && this.currentReplay.id === replayId) {
                this.currentReplay = null;
                this.board.render(this.getInitialBoard(), 'white');
            }
            this.renderList();
        } catch (error) {
            alert('删除失败！');
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