#include "dsp_app.h"

dsp_i16 dsp_sat(dsp_i32 x)
{
    if (x > 32767L) return 32767;
    if (x < -32768L) return -32768;
    return (dsp_i16)x;
}

/* Defined floor division, independent of host signed right-shift behavior. */
dsp_i32 dsp_q15(dsp_i32 x)
{
    if (x >= 0) return x / 32768L;
    return -1L - (-(x + 1L)) / 32768L;
}

/* In-place radix-2 DIT, natural order, forward FFT normalized by 1/N.
   A factor of 1/2 at every stage limits fixed-point growth. */
void fft_c(dsp_i16 *re, dsp_i16 *im)
{
    unsigned int i, j, bit, len, half, base, k, w;
    dsp_i16 temp, ar, ai;
    dsp_i32 tr, ti;
    j = 0;
    for (i = 1; i < FFT_N; ++i) {
        bit = FFT_N >> 1;
        while (j & bit) { j ^= bit; bit >>= 1; }
        j ^= bit;
        if (i < j) {
            temp = re[i]; re[i] = re[j]; re[j] = temp;
            temp = im[i]; im[i] = im[j]; im[j] = temp;
        }
    }
    for (len = 2; len <= FFT_N; len <<= 1) {
        half = len >> 1;
        for (base = 0; base < FFT_N; base += len) {
            for (k = 0; k < half; ++k) {
                i = base + k; j = i + half; w = k * (FFT_N / len);
                /* Unity and -j are exact; Q15 cannot represent +1.0. */
                if (w == 0) { tr = re[j]; ti = im[j]; }
                else if (w == FFT_N/4) { tr = im[j]; ti = -(dsp_i32)re[j]; }
                else {
                    tr = dsp_q15((dsp_i32)gTwiddleRe[w] * re[j]
                                - (dsp_i32)gTwiddleIm[w] * im[j]);
                    ti = dsp_q15((dsp_i32)gTwiddleRe[w] * im[j]
                                + (dsp_i32)gTwiddleIm[w] * re[j]);
                }
                ar = re[i]; ai = im[i];
                re[i] = dsp_sat(((dsp_i32)ar + tr) / 2L);
                im[i] = dsp_sat(((dsp_i32)ai + ti) / 2L);
                re[j] = dsp_sat(((dsp_i32)ar - tr) / 2L);
                im[j] = dsp_sat(((dsp_i32)ai - ti) / 2L);
            }
        }
    }
}
