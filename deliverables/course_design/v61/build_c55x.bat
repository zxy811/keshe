@echo off
setlocal
cd /d "%~dp0"
rem Set this to the INSTALLED C55x compiler folder, not the CCS root.
if not defined C55X_CGT set "C55X_CGT=C:\CCStudio_v3.3\C5500\cgtools"
if not exist "%C55X_CGT%\bin\cl55.exe" (
  echo C55x compiler missing. Set C55X_CGT to the folder containing bin\cl55.exe.
  exit /b 1
)
if not exist Debug mkdir Debug
if not exist generated mkdir generated
rem Preserve source-interlisted assembly for review; then assemble it below.
"%C55X_CGT%\bin\cl55.exe" -ml -g -n -ss -fs"generated" fft_dif_backend.c
if errorlevel 1 exit /b 1
if not exist "generated\fft_dif_backend.asm" (
  echo Assembly output missing. Inspect compiler output and -fs option for your compiler version.
  exit /b 1
)
"%C55X_CGT%\bin\cl55.exe" -ml -g -c -fr"Debug" Image.c InitImage.c Key.c app.c filters.c fft_c.c modulation.c tables.c sdram_init.c util.c generated\fft_dif_backend.asm
if errorlevel 1 exit /b 1
"%C55X_CGT%\bin\cl55.exe" -ml -z -c -i"%C55X_CGT%\lib" -m"Debug\course_design.map" -o"Debug\course_design.out" Debug\Image.obj Debug\InitImage.obj Debug\Key.obj Debug\app.obj Debug\filters.obj Debug\fft_c.obj Debug\modulation.obj Debug\tables.obj Debug\sdram_init.obj Debug\util.obj Debug\fft_dif_backend.obj ICETEK-VC5509-A.cmd
if errorlevel 1 exit /b 1
echo Built Debug\course_design.out. ONLY for the ICETEK C5509 target.
echo Read the .map memory report and compiler warnings before loading.
endlocal
