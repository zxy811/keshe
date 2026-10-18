This folder intentionally contains no fabricated TI assembly output.
Run ..\build_c55x.bat with the installed TI C55x compiler.
It compiles fft_dif_backend.c to fft_dif_backend.asm using -n -ss,
then assembles that actual C55x assembly source and links it into the DSP image.
The compiler-generated assembly is the backend for key 5.
This is not a handwritten assembly FFT, and host tests are not ISA tests.
If your teacher specifically requires handwritten assembly, this requirement
still needs separate implementation/approval; do not describe it as completed.
