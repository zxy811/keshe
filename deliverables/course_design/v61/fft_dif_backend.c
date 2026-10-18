#include "dsp_app.h"
/* Independent radix-2 DIF implementation, used to generate C55x assembly.
   Target build compiles this file to .asm, THEN assembles that .asm.
   Do not also add this C file to the CCS project: duplicate definitions.
   DSP_HOST uses this source as a behavioral model, not as an ISA emulator.
   This is compiler-generated assembly, not a handwritten assembly FFT. */
void fft_asm(dsp_i16 *re, dsp_i16 *im)
{
    unsigned int span, half, base, k, i, j, w, bit, rev;
    dsp_i32 ar, ai, br, bi, dr, di;
    dsp_i16 tmp;
    for (span = FFT_N; span >= 2; span >>= 1) {
        half = span >> 1;
        for (base = 0; base < FFT_N; base += span) {
            for (k = 0; k < half; ++k) {
                i = base + k; j = i + half; w = k * (FFT_N / span);
                ar = re[i]; ai = im[i]; br = re[j]; bi = im[j];
                re[i] = dsp_sat((ar + br) / 2L);
                im[i] = dsp_sat((ai + bi) / 2L);
                dr = (ar - br) / 2L; di = (ai - bi) / 2L;
                if (w == 0) { re[j] = dsp_sat(dr); im[j] = dsp_sat(di); }
                else if (w == FFT_N/4) { re[j] = dsp_sat(di); im[j] = dsp_sat(-dr); }
                else {
                    re[j] = dsp_sat(dsp_q15(dr * gTwiddleRe[w] - di * gTwiddleIm[w]));
                    im[j] = dsp_sat(dsp_q15(dr * gTwiddleIm[w] + di * gTwiddleRe[w]));
                }
            }
        }
    }
    /* DIF produces bit-reversed output; restore natural order. */
    rev = 0;
    for (i = 1; i < FFT_N; ++i) {
        bit = FFT_N >> 1;
        while (rev & bit) { rev ^= bit; bit >>= 1; }
        rev ^= bit;
        if (i < rev) {
            tmp = re[i]; re[i] = re[rev]; re[rev] = tmp;
            tmp = im[i]; im[i] = im[rev]; im[rev] = tmp;
        }
    }
}
