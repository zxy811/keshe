"""Cloud-only runner for the verified, locally extracted Debian Octave tree.
For a normal Ubuntu installation simply run: octave --no-gui --eval run_all
"""
from pathlib import Path
import argparse
import os
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-root',type=Path,default=Path('/workspace/keshe/work/octave-root/usr'))
    a=p.parse_args();r=a.runtime_root.resolve();binary=r/'bin/octave-cli'
    if not binary.exists():raise SystemExit('Local cloud runtime absent. Use a normally installed MATLAB/Octave instead.')
    versions=sorted(p for p in (r/'lib/x86_64-linux-gnu/octave').iterdir() if re.fullmatch(r'\d+\.\d+\.\d+',p.name))
    if len(versions)!=1:raise SystemExit('Expected one explicit Octave runtime version.')
    e=os.environ.copy()
    e.update(OCTAVE_HOME=str(r),OCTAVE_FONTS_DIR=str(r/'share/fonts/opentype/freefont'),
             LD_LIBRARY_PATH=':'.join([str(versions[0]),str(r/'lib/x86_64-linux-gnu'),str(r/'lib')]),
             PATH=str(r/'bin')+os.pathsep+e.get('PATH',''),
             GNUPLOT_PS_DIR=str(r/'share/gnuplot/gnuplot/6.0/PostScript'),
             GNUTERM='pngcairo',XDG_CACHE_HOME=str(ROOT/'results'/'runtime_cache'))
    path=str(ROOT/'matlab').replace("'","''")
    code="set(0,'defaultfigurevisible','off'); graphics_toolkit('gnuplot'); set(0,'defaultaxesfontname','DejaVu Sans'); set(0,'defaulttextfontname','DejaVu Sans'); addpath('"+path+"'); run_all;"
    log=ROOT/'results'/'octave_run.log'
    with log.open('w') as f:
        result=subprocess.run([str(binary),'--no-gui','--no-history','--quiet','--eval',code],env=e,stdout=f,stderr=subprocess.STDOUT)
    print(log.read_text());return result.returncode


if __name__=='__main__':raise SystemExit(main())
