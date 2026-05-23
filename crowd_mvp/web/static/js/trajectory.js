'use strict';
// trajectory.js — Gaussian-splat accumulation canvas with PLASMA colormap.
// Agents land on the canvas on every WS frame; frequently-visited pixels
// accumulate value and map to brighter PLASMA colours (dark purple → yellow).
// Requires colormaps.js (PLASMA_LUT) to be loaded first.

class TrajectoryCanvas {
    /**
     * @param {HTMLCanvasElement} canvasEl
     * @param {number} mapW   — simulation map width  (from geometry.map_size)
     * @param {number} mapH   — simulation map height
     */
    constructor(canvasEl, mapW, mapH) {
        this.canvas = canvasEl;
        this.ctx    = canvasEl.getContext('2d', { willReadFrequently: false });
        this.W      = canvasEl.width;   // canvas pixel width
        this.H      = canvasEl.height;  // canvas pixel height
        this.mapW   = mapW;
        this.mapH   = mapH;

        // Gaussian splat radius in canvas pixels (scaled from map coords)
        this.sigma  = Math.round(8 * this.W / 500);  // ~8px at 500w
        this.sigma3 = Math.ceil(this.sigma * 2.5);

        // Float accumulation buffer — one cell per canvas pixel
        this.accum      = new Float32Array(this.W * this.H);
        this.runningMax = 1e-4;   // avoids div-by-zero on first render

        // Pre-compute Gaussian kernel weights (one quadrant, reused)
        this._kernel = this._buildKernel();

        // Rendering throttle — only repaint every N frames to keep it smooth
        this._frameCount = 0;
        this._renderEvery = 2;   // repaint every 2nd WS update (1 Hz effective)
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /** Add current agent positions to accumulation buffer. */
    addAgents(agents) {
        const scaleX = this.W / this.mapW;
        const scaleY = this.H / this.mapH;
        const { sigma3, W, H, accum, _kernel } = this;

        for (const [ax, ay] of agents) {
            const cx = Math.round(ax * scaleX);
            const cy = Math.round(ay * scaleY);

            for (let dy = -sigma3; dy <= sigma3; dy++) {
                const py = cy + dy;
                if (py < 0 || py >= H) continue;
                for (let dx = -sigma3; dx <= sigma3; dx++) {
                    const px = cx + dx;
                    if (px < 0 || px >= W) continue;
                    const w   = _kernel[dy + sigma3][dx + sigma3];
                    const idx = py * W + px;
                    accum[idx] += w;
                    if (accum[idx] > this.runningMax) this.runningMax = accum[idx];
                }
            }
        }
    }

    /** Apply PLASMA colormap and paint to canvas. */
    render() {
        this._frameCount++;
        if (this._frameCount % this._renderEvery !== 0) return;

        const { W, H, accum, runningMax, ctx } = this;
        const imgData = ctx.createImageData(W, H);
        const d       = imgData.data;
        const invMax  = 1.0 / runningMax;
        const lut     = PLASMA_LUT;

        for (let i = 0; i < W * H; i++) {
            const v = Math.min(1.0, accum[i] * invMax);
            if (v < 0.004) {
                // leave alpha=0 (transparent — dark map bg shows through)
                continue;
            }
            const li   = Math.round(v * 255);
            const rgb  = lut[li];
            const base = i * 4;
            d[base]     = rgb[0];
            d[base + 1] = rgb[1];
            d[base + 2] = rgb[2];
            d[base + 3] = Math.round(v * 215);   // fade-in with density
        }

        ctx.putImageData(imgData, 0, 0);
    }

    /** Clear all accumulated data (call on scenario change / reset). */
    reset() {
        this.accum.fill(0);
        this.runningMax  = 1e-4;
        this._frameCount = 0;
        this.ctx.clearRect(0, 0, this.W, this.H);
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /** Build sigma3×sigma3 Gaussian kernel (2-D array). */
    _buildKernel() {
        const { sigma, sigma3 } = this;
        const size   = sigma3 * 2 + 1;
        const k      = [];
        const inv2s2 = 1.0 / (2 * sigma * sigma);
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
