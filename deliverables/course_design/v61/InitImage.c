#include "dsp_app.h"
/* Built-in sources are deterministic and require no target fopen/CIO. */
void app_load_source(void)
{
    int x, y, dx, dy, value;
    unsigned int p;
    if (gSource == 2 && !gUserImageReady) { gError = 1; gSource = 0; }
    for (y = 0; y < IMAGEHEIGHT; ++y) {
        for (x = 0; x < IMAGEWIDTH; ++x) {
            p = (unsigned int)(y * IMAGEWIDTH + x);
            if (gSource == 2) value = dbUserImage[p] & 255;
            else if (gSource == 1) {
                dx = x - 40; dy = y - 40;
                value = 255 - (dx * dx + dy * dy) / 12;
                if (value < 0) value = 0;
            } else {
                /* Vertical bars contain horizontal spatial frequencies. */
                value = ((x / 5) % 2) ? 220 : 35;
                if (y > 25 && y < 55 && x > 25 && x < 55) value = 128;
            }
            dbImage[p] = (unsigned char)value;
        }
    }
}
