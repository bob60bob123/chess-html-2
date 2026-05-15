// Sound effects using Web Audio API
class SoundEffect {
    constructor() {
        this.audioCtx = null;
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        try {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            this.initialized = true;
        } catch (e) {
            console.warn('Web Audio API not supported');
        }
    }

    playMove() {
        this.init();
        if (!this.audioCtx) return;
        this._playTone(400, 0.1, 'sine', 0.3);
    }

    playCapture() {
        this.init();
        if (!this.audioCtx) return;
        this._playTone(300, 0.15, 'triangle', 0.5);
        setTimeout(() => this._playTone(200, 0.1, 'triangle', 0.3), 50);
    }

    playCheck() {
        this.init();
        if (!this.audioCtx) return;
        this._playTone(500, 0.1, 'square', 0.3);
        setTimeout(() => this._playTone(600, 0.15, 'square', 0.3), 100);
    }

    playVictory() {
        this.init();
        if (!this.audioCtx) return;
        const notes = [523, 659, 784, 1047]; // C5, E5, G5, C6
        notes.forEach((freq, i) => {
            setTimeout(() => this._playTone(freq, 0.3, 'sine', 0.4), i * 150);
        });
    }

    playDefeat() {
        this.init();
        if (!this.audioCtx) return;
        const notes = [400, 350, 300, 250];
        notes.forEach((freq, i) => {
            setTimeout(() => this._playTone(freq, 0.3, 'sawtooth', 0.3), i * 200);
        });
    }

    playPromotion() {
        this.init();
        if (!this.audioCtx) return;
        const notes = [523, 659, 784, 880, 1047];
        notes.forEach((freq, i) => {
            setTimeout(() => this._playTone(freq, 0.15, 'sine', 0.3), i * 80);
        });
    }

    playCastle() {
        this.init();
        if (!this.audioCtx) return;
        this._playTone(350, 0.1, 'triangle', 0.4);
        setTimeout(() => this._playTone(450, 0.15, 'triangle', 0.4), 100);
    }

    playThinkTick() {
        this.init();
        if (!this.audioCtx) return;
        // Short tick sound for thinking
        this._playTone(800, 0.05, 'square', 0.15);
    }

    _playTone(frequency, duration, type, volume) {
        if (!this.audioCtx) return;

        const oscillator = this.audioCtx.createOscillator();
        const gainNode = this.audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioCtx.destination);

        oscillator.type = type;
        oscillator.frequency.setValueAtTime(frequency, this.audioCtx.currentTime);

        gainNode.gain.setValueAtTime(volume, this.audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + duration);

        oscillator.start(this.audioCtx.currentTime);
        oscillator.stop(this.audioCtx.currentTime + duration);
    }
}

const sound = new SoundEffect();
