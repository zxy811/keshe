#include "dsp_app.h"
/* fs=32 kHz, fc=8 kHz, carrier [1,0,-1,0] is exactly periodic.
   AM=(16384+0.5*m)*c, DSB=m*c; signal m peak=12000.
   Picture modulation is a visualization of row samples, not image encoding. */
void app_modulate(unsigned int dsb)
{
    int x, y, n;
    dsp_i32 v, carrier, m;
    for (n = 0; n < FFT_N; ++n) {
        m = gSignalIn[n]; carrier = gCarrier[n % 4];
        if (!dsb) m = 16384L + m / 2L;
        gSignalOut[n] = dsp_sat(dsp_q15(m * carrier));
    }
    for (y = 0; y < IMAGEHEIGHT; ++y) {
        for (x = 0; x < IMAGEWIDTH; ++x) {
            m = (dsp_i32)dbImage[y * IMAGEWIDTH + x] - 128L;
            carrier = gCarrier[x % 4];
            if (!dsb) m = 64L + m / 2L;
            v = dsp_q15(m * carrier) + 128L;
            if (v < 0) v = 0;
            if (v > 255) v = 255;
            dbTargetImage[y * IMAGEWIDTH + x] = (unsigned char)v;
        }
    }
}
