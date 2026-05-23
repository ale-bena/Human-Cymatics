'use strict';
// trajectory.js — Gaussian-splat accumulation canvas with PLASMA colormap.
// Designed for a DARK canvas background (#0d1424).
// Requires colormaps.js (PLASMA_LUT) loaded first.

class TrajectoryCanvas {
    constructor(canvasEl, mapW, mapH) {
        this.canvas = canvasEl;
        this.ctx    = canvasEl.getContext('2d');
        this.W      = canvasEl.width;    // 1000
        this.H      = canvasEl.height;   // 700
        this.mapW   = mapW;              // simulation map width
        this.mapH   = mapH;              // simulation map height

        // Gaussian splat radius in canvas pixels
        this.sigma  = 10;
        this.sigma3 = Math.ceil(this.sigma * 2.8);  // ~28

        this.accum      = new Float32Array(this.W * this.H);
        this.runningMax = 1e-6;

        this._kernel = this._buildKernel();

        // Fill canvas with dark background once
        this.ctx.fillStyle = '#0d1424';
        this.ctx.fillRect(0, 0, this.W, this.H);
    }

    // ── Add current agent positions to accumulation buffer ───────────────
    addAgents(agents) {
        const scaleX = this.W / this.mapW;
        const scaleY = this.H / this.mapH;
        const { sigma3, W, H } = this;
        const kernel = this._kernel;
        const accum  = this.accum;

        for (const agent of agents) {
            const ax = agent[0], ay = agent[1];
            const cx = Math.round(ax * scaleX);
            const cy = Math.round(ay * scaleY);

            for (let di = 0, dy = -sigma3; dy <= sigma3; dy++, di++) {
                const py = cy + dy;
                if (py < 0 || py >= H) continue;
                const row = kernel[di];
                const rowBase = py * W;
                for (let dj = 0, dx = -sigma3; dx <= sigma3; dx++, dj++) {
                    const px = cx + dx;
                    if (px < 0 || px >= W) continue;
                    const idx = rowBase + px;
                    accum[idx] += row[dj];
                    if (accum[idx] > this.runningMax) this.runningMax = accum[idx];
                }
            }
        }
    }

    // ── Render accumulation buffer using PLASMA colormap ─────────────────
    render() {
        const { W, H, accum, ctx } = this;
        const invMax  = 1.0 / this.runningMax;
        const imgData = ctx.createImageData(W, H);
        const d       = imgData.data;
        const lut     = PLASMA_LUT;

        for (let i = 0; i < W * H; i++) {
            const raw = accum[i];
            if (raw <= 0) continue;

            const v  = Math.min(1.0, raw * invMax);
            const li = Math.round(v * 255);
            const rgb = lut[li];
            const b4  = i * 4;
            d[b4]     = rgb[0];
            d[b4 + 1] = rgb[1];
            d[b4 + 2] = rgb[2];
            // Alpha: power curve so low-density paths are still visible on dark bg
            d[b4 + 3] = Math.round(Math.pow(v, 0.5) * 255);
        }

        // Draw dark background first, then overlay accumulated colours
        ctx.fillStyle = '#0d1424';
        ctx.fillRect(0, 0, W, H);
        ctx.putImageData(imgData, 0, 0);
    }

    // ── Clear ─────────────────────────────────────────────────────────────
    reset() {
        this.accum.fill(0);
        this.runningMax = 1e-6;
        this.ctx.fillStyle = '#0d1424';
        this.ctx.fillRect(0, 0, this.W, this.H);
    }

    // ── Pre-build Gaussian kernel (2-D array) ─────────────────────────────
    _buildKernel() {
        const { sigma, sigma3 } = this;
        const inv2s2 = 1.0 / (2 * sigma * sigma);
        const k = [];
        for (let dy = -sigma3; dy <= sigma3; dy++) {
            const row = [];
            for (let dx = -sigma3; dx <= sigma3; dx++) {
                row.push(Math.exp(-(dx * dx + dy * dy) * inv2s2));
            }
            k.push(row);
        }
        return k;
    }
}
