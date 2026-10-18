#ifndef DSP_APP_H
#define DSP_APP_H
/* C5509: char/int/short are 16 bits, long is 32 bits. Never assume 8-bit char. */
#ifdef DSP_HOST
#include <stdint.h>
typedef int32_t dsp_i32;
#else
typedef signed long dsp_i32;
#endif
typedef signed short dsp_i16;
#define IMAGEWIDTH 80
#define IMAGEHEIGHT 80
#define IMAGEPIXELS 6400
#define FFT_N 256
#define FIR_TAPS 257
#define FS_HZ 32000L
#define FILTER_COUNT 28
#define MODE_LPF 1
#define MODE_BPF 2
#define MODE_BRF 3
#define MODE_FFT_C 4
#define MODE_FFT_ASM 5
#define MODE_AM 6
#define MODE_DSB 7

extern unsigned char dbImage[IMAGEPIXELS];
extern unsigned char dbTargetImage[IMAGEPIXELS];
extern unsigned char dbUserImage[IMAGEPIXELS];
extern dsp_i16 gSignalIn[FFT_N], gSignalOut[FFT_N];
extern dsp_i16 gFFTReal[FFT_N], gFFTImag[FFT_N];
extern volatile unsigned int gBusy, gResultSeq, gMode, gCutoffIndex;
extern volatile unsigned int gSource, gUserImageReady, gCommand, gLastKey;
extern volatile unsigned int gError, gFilterIndex, gFFTBackend;
extern volatile unsigned int gResultMode, gResultCutoffIndex, gResultSource;
extern const dsp_i16 gFIR[FILTER_COUNT][FIR_TAPS];
extern const dsp_i16 gTwiddleRe[FFT_N/2], gTwiddleIm[FFT_N/2];
extern const dsp_i16 gCarrier[4];
dsp_i16 dsp_sat(dsp_i32 x);
dsp_i32 dsp_q15(dsp_i32 x);
void fft_c(dsp_i16 *re, dsp_i16 *im);
void fft_asm(dsp_i16 *re, dsp_i16 *im);
void app_init(void);
void app_handle_key(unsigned int key);
void app_process(void);
void App_ResultReady(void);
void app_filter_image(unsigned int index);
void app_filter_signal(unsigned int index);
void app_modulate(unsigned int dsb);
#endif
