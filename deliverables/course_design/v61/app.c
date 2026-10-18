#include "dsp_app.h"
extern const dsp_i16 gTestSignal[FFT_N], gMessageSignal[FFT_N];
void app_load_source(void);

static void render_spectrum(void)
{
    int x, y, bin, first, last;
    dsp_i32 a, b, mag, top, height;
    top = 1;
    for (bin = 0; bin <= FFT_N / 2; ++bin) {
        a = gFFTReal[bin]; b = gFFTImag[bin];
        if (a < 0) a = -a;
        if (b < 0) b = -b;
        /* L1 magnitude used ONLY in 80x80 preview. Export exact Re/Im. */
        if (a + b > top) top = a + b;
    }
    for (x = 0; x < IMAGEWIDTH; ++x) {
        first = x * (FFT_N / 2 + 1) / IMAGEWIDTH;
        last = (x + 1) * (FFT_N / 2 + 1) / IMAGEWIDTH;
        mag = 0;
        for (bin = first; bin < last; ++bin) {
            a = gFFTReal[bin]; b = gFFTImag[bin];
            if (a < 0) a = -a;
            if (b < 0) b = -b;
            if (a + b > mag) mag = a + b;
        }
        height = mag * (IMAGEHEIGHT - 1L) / top;
        for (y = 0; y < IMAGEHEIGHT; ++y)
            dbTargetImage[y * IMAGEWIDTH + x] =
                (unsigned char)((IMAGEHEIGHT - 1 - y <= height) ? 240 : 10);
    }
}

void App_ResultReady(void)
{
    /* Put a CCS breakpoint HERE for a consistent result frame.
       Compile app.c without optimization so this marker remains visible. */
    gBusy = 0;
}

void app_init(void)
{
    gBusy = 0; gResultSeq = 0; gMode = MODE_LPF; gCutoffIndex = 3;
    gSource = 0; gUserImageReady = 0; gCommand = 0; gLastKey = 0;
    gError = 0; gFilterIndex = 0; gFFTBackend = 0;
    gResultMode = 0; gResultCutoffIndex = 0; gResultSource = 0;
    app_load_source();
    app_process();
}

void app_process(void)
{
    int n;
    gBusy = 1; gError = 0;
    app_load_source();
    gFFTBackend = 0;
    for (n = 0; n < FFT_N; ++n) {
        gSignalIn[n] = (gMode >= MODE_AM) ? gMessageSignal[n] : gTestSignal[n];
        gSignalOut[n] = 0;
    }
    if (gMode >= MODE_LPF && gMode <= MODE_BRF) {
        if (gMode == MODE_LPF) gFilterIndex = gCutoffIndex;
        else {
            /* Adjacent edges: 1-2,...,9-10 kHz. Index 9 wraps to 1-2. */
            gFilterIndex = (gMode == MODE_BPF ? 10 : 19) + gCutoffIndex % 9;
        }
        app_filter_image(gFilterIndex);
        app_filter_signal(gFilterIndex);
    } else if (gMode == MODE_FFT_C || gMode == MODE_FFT_ASM) {
        /* FFT the middle ROW of the input picture, zero-pad 80 to 256. */
        for (n = 0; n < FFT_N; ++n) {
            gFFTReal[n] = (n < IMAGEWIDTH) ?
                (dsp_i16)(((int)dbImage[(IMAGEHEIGHT/2) * IMAGEWIDTH + n] - 128) * 128) : 0;
            gFFTImag[n] = 0;
        }
        if (gMode == MODE_FFT_C) fft_c(gFFTReal, gFFTImag);
        else { fft_asm(gFFTReal, gFFTImag); gFFTBackend = 1; }
        render_spectrum();
        /* One-dimensional signal spectrum remains available as a separate
           operation in host validation; gFFTReal/Imag are the PICTURE row. */
    } else app_modulate(gMode == MODE_DSB);
    gResultMode = gMode; gResultCutoffIndex = gCutoffIndex;
    gResultSource = gSource;
    gResultSeq = (gResultSeq + 1U) & 65535U;
    App_ResultReady();
}

void app_handle_key(unsigned int key)
{
    gLastKey = key;
    if (key >= 1 && key <= 7) {
        gMode = key;
        if (key == MODE_BPF || key == MODE_BRF) gCutoffIndex %= 9U;
    }
    else if (key == 8) {
        if (gMode == MODE_BPF || gMode == MODE_BRF)
            gCutoffIndex = (gCutoffIndex + 1U) % 9U;
        else gCutoffIndex = (gCutoffIndex + 1U) % 10U;
    } else if (key == 9) {
        /* Only choose uploaded source if its flag was set deliberately. */
        gSource = (gSource + 1U) % (gUserImageReady ? 3U : 2U);
    } else return;
    app_process();
}
