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
        return String.fromCharCode(97 + file) + (rank + 1);
    }

    posToCoords(pos) {
        return [pos.charCodeAt(0) - 97, parseInt(pos[1]) - 1];
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