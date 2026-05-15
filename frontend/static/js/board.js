class ChessBoard {
    constructor(container) {
        this.container = container;
        this.selectedSquare = null;
        this.legalMoves = [];
        this.lastMove = null;
        this.onSquareClick = null;
    }

    render(boardState, turn) {
        this.container.innerHTML = '';
        const board = document.createElement('div');
        board.className = 'board';

        // Render from black's perspective (black at bottom)
        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                const square = document.createElement('div');
                const isLight = (file + rank) % 2 === 0;
                square.className = `square ${isLight ? 'light' : 'dark'}`;
                square.dataset.pos = this.coordsToPos(file, rank);

                const piece = boardState[rank][file];
                if (piece) {
                    const pieceSpan = document.createElement('span');
                    pieceSpan.className = `piece ${this.getPieceColor(piece)}`;
                    pieceSpan.textContent = this.getPieceUnicode(piece);
                    square.appendChild(pieceSpan);
                }

                // Highlighting
                if (this.selectedSquare === square.dataset.pos) {
                    square.classList.add('selected');
                }
                if (this.legalMoves.includes(square.dataset.pos)) {
                    square.classList.add('legal-move');
                }
                if (this.lastMove && this.lastMove.includes(square.dataset.pos)) {
                    square.classList.add('last-move');
                }

                square.addEventListener('click', () => {
                    if (this.onSquareClick) {
                        this.onSquareClick(square.dataset.pos);
                    }
                });

                board.appendChild(square);
            }
        }

        this.container.appendChild(board);
    }

    coordsToPos(file, rank) {
        // rank 0 = row 0 = should be rank 8 (black's back rank / top of board)
        // rank 7 = row 7 = should be rank 1 (white's back rank / bottom of board)
        return String.fromCharCode(97 + file) + (8 - rank);
    }

    posToCoords(pos) {
        // pos like 'e2' -> [file_idx, rank_idx] where rank_idx 0=rank8, 7=rank1
        // 'e2' has rank 2, which is rank_idx = 8 - 2 = 6
        return [pos.charCodeAt(0) - 97, 8 - parseInt(pos[1])];
    }

    getPieceUnicode(symbol) {
        const pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        return pieces[symbol] || '';
    }

    getPieceColor(symbol) {
        return symbol === symbol.toUpperCase() ? 'white' : 'black';
    }

    setSelected(pos) {
        this.selectedSquare = pos;
    }

    setLegalMoves(moves) {
        this.legalMoves = moves || [];
    }

    setLastMove(from, to) {
        this.lastMove = [from, to];
    }
}