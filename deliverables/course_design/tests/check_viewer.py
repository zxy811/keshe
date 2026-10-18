"""Headless functional smoke test of actual GUI callbacks and snapshot timer."""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results'/'mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent
sys.path.insert(0,str(ROOT/'tools'))
import viewer


def main():
    saved=0
    def simulate_keys():
        nonlocal saved
        f=plt.gcf()
        for key in '123456789':
            f.canvas.callbacks.process('key_press_event',KeyEvent('key_press_event',f.canvas,key=key))
            f.canvas.draw()
        f.savefig(ROOT/'results'/'figures'/'viewer_smoke.png',dpi=120)
        saved+=1;plt.close(f)
    original=plt.show
    plt.show=simulate_keys
    sys.argv=['viewer.py','--image',str(ROOT/'assets'/'demo_input.png')]
    viewer.main()
    timers=[]
    from matplotlib.backend_bases import FigureCanvasBase
    orig_timer=FigureCanvasBase.new_timer
    def capture_timer(self,*args,**kw):
        t=orig_timer(self,*args,**kw);timers.append(t);return t
    FigureCanvasBase.new_timer=capture_timer
    def update_snapshot():
        nonlocal saved
        for t in timers:t._on_timer()
        f=plt.gcf();f.canvas.draw()
        assert all('CCS exported snapshot' in a.get_title() for a in f.axes)
        f.savefig(ROOT/'results'/'figures'/'snapshot_viewer_smoke.png',dpi=120)
        saved+=1;plt.close(f)
    plt.show=update_snapshot
    sys.argv=['viewer.py','--board-dir',str(ROOT/'assets'/'example_board_exports')]
    viewer.main()
    plt.show=original;FigureCanvasBase.new_timer=orig_timer
    assert saved==2
    print('PASS: all 9 PC key callbacks and both CCS-format snapshot refreshes rendered.')


if __name__=='__main__':main()
