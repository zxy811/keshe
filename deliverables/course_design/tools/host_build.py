"""Build exactly the portable DSP C sources; never compile MMIO on a PC."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['Image.c','InitImage.c','app.c','filters.c','fft_c.c',
           'fft_dif_backend.c','modulation.c','tables.c']


def build():
    out = ROOT/'results'
    out.mkdir(exist_ok=True)
    cc = os.environ.get('CC', 'gcc')
    if not shutil.which(cc):
        raise SystemExit('C compiler missing. Install GCC/MinGW-w64 or set CC.')
    lib = out/('dsp_host.dll' if sys.platform == 'win32' else 'libdsp_host.so')
    cmd = [cc, '-std=c89','-O2','-Wall','-Wextra','-Werror','-pedantic',
           '-DDSP_HOST','-shared']
    if sys.platform != 'win32': cmd += ['-fPIC']
    else: cmd += ['-static-libgcc','-Wl,--export-all-symbols']
    cmd += ['-I'+str(ROOT/'v61')] + [str(ROOT/'v61'/s) for s in SOURCES]+['-o',str(lib)]
    subprocess.run(cmd,check=True)
    return lib


if __name__ == '__main__': print(build())
