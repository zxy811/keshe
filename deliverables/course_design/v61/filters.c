#include "dsp_app.h"
/* Reflect without repeating the end pixel: -1 -> 1, 80 -> 78. */
static int reflected(int n)
{
    while (n < 0 || n >= IMAGEWIDTH) {
        if (n < 0) n = -n;
        if (n >= IMAGEWIDTH) n = 2 * IMAGEWIDTH - 2 - n;
    }
    return n;
}
void app_filter_image(unsigned int index)
{
    int x, y, k, sx;
    dsp_i32 acc, value;
    const dsp_i16 *h;
    h = gFIR[index];
    for (y = 0; y < IMAGEHEIGHT; ++y) {
        for (x = 0; x < IMAGEWIDTH; ++x) {
            acc = 0;
            for (k = 0; k < FIR_TAPS; ++k) {
                sx = reflected(x + FIR_TAPS / 2 - k);
                value = (dsp_i32)dbImage[y * IMAGEWIDTH + sx] - 128L;
                acc += value * h[k];
            }
            value = dsp_q15(acc) + 128L;
            if (value < 0) value = 0;
            if (value > 255) value = 255;
            dbTargetImage[y * IMAGEWIDTH + x] = (unsigned char)value;
        }
    }
}
/* Periodic demonstration signal, centered FIR for delay-free comparison.
   This is offline frame filtering, not ADC streaming or a real-time claim. */
void app_filter_signal(unsigned int index)
{
    int n, k, p;
    dsp_i32 acc;
    for (n = 0; n < FFT_N; ++n) {
        acc = 0;
        for (k = 0; k < FIR_TAPS; ++k) {
            p = (n + FIR_TAPS / 2 - k + 2 * FFT_N) % FFT_N;
            acc += (dsp_i32)gSignalIn[p] * gFIR[index][k];
        }
        gSignalOut[n] = dsp_sat(dsp_q15(acc));
    }
}
