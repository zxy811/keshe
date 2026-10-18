#include "dsp_app.h"
unsigned char dbImage[IMAGEPIXELS];
unsigned char dbTargetImage[IMAGEPIXELS];
unsigned char dbUserImage[IMAGEPIXELS];
dsp_i16 gSignalIn[FFT_N], gSignalOut[FFT_N];
dsp_i16 gFFTReal[FFT_N], gFFTImag[FFT_N];
volatile unsigned int gBusy, gResultSeq, gMode, gCutoffIndex;
volatile unsigned int gSource, gUserImageReady, gCommand, gLastKey;
volatile unsigned int gError, gFilterIndex, gFFTBackend;
volatile unsigned int gResultMode, gResultCutoffIndex, gResultSource;
