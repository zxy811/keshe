/* Adapted from supplied Key.c: preserve actual C5509 PLL/SDRAM/CTR path. */
#include "myapp.h"
#include "ICETEK-VC5509-EDU.h"
#include "dsp_app.h"

void main(void)
{
    unsigned int key;
    PLL_Init(20);
    SDRAM_init();
    InitCTR();
    app_init();
    for (;;) {
        if (gCommand >= 1 && gCommand <= 9) {
            key = gCommand; gCommand = 0;
        } else key = GetKey() & 0x00ff;
        if (key >= 1 && key <= 9) app_handle_key(key);
        Delay(16);
    }
}
