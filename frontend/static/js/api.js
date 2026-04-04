const API = {
    baseUrl: 'http://localhost:8000',

    async startGame(difficulty) {
        const res = await fetch(`${this.baseUrl}/api/game/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({difficulty})
        });
        return res.json();
    },

    async makeMove(gameId, from, to) {
        const res = await fetch(`${this.baseUrl}/api/game/move`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId, from_pos: from, to_pos: to})
        });
        return res.json();
    },

    async getState(gameId) {
        const res = await fetch(`${this.baseUrl}/api/game/state/${gameId}`);
        return res.json();
    },

    async undoMove(gameId) {
        const res = await fetch(`${this.baseUrl}/api/game/undo`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId})
        });
        return res.json();
    },

    async getReplayList() {
        const res = await fetch(`${this.baseUrl}/api/replay/list`);
        return res.json();
    },

    async getReplay(replayId) {
        const res = await fetch(`${this.baseUrl}/api/replay/${replayId}`);
        return res.json();
    },

    async saveReplay(gameId) {
        const res = await fetch(`${this.baseUrl}/api/replay/save`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId})
        });
        return res.json();
    }
};