-w
-stack 1000
-sysstack 1000
-l rts55x.lib
MEMORY
{
    DARAM:  o=0x100,   l=0x7f00
    VECT:   o=0x8000,  l=0x100
    DARAM2: o=0x8100,  l=0x7f00
    SARAM:  o=0x10000, l=0x30000
    SDRAM:  o=0x40000, l=0x3e0000
}
SECTIONS
{
    .text:    {} > DARAM
    vectors:  {} > VECT
    .vectors: {} > VECT
    .trcinit: {} > DARAM
    .gblinit: {} > DARAM
    frt:      {} > DARAM
    .cinit:   {} > SARAM
    .pinit:   {} > DARAM
    .sysinit: {} > DARAM
    .bss:     {} > SARAM
    .far:     {} > SARAM
    .const:   {} > SARAM
    .switch:  {} > SARAM
    .sysmem:  {} > DARAM2
    .cio:     {} > DARAM2
    .MEM$obj: {} > SARAM
    .sysheap: {} > DARAM2
    .sysstack {} > DARAM2
    .stack:   {} > DARAM2
}
