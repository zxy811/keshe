"""PC simulator calls the actual portable DSP C code; not a board connection.
Use --board-dir to watch CCS-exported .dat snapshots instead of simulation.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from host_api import DSP,ROOT
from image_tool import read_dat

MODES=['','LPF','BPF','BRF','FFT C (DIT)','FFT assembly source model (DIF)','AM','DSB']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image');p.add_argument('--board-dir',type=Path)
    a=p.parse_args()
    if a.board_dir:
        watch_board(a.board_dir);return
    dsp=DSP()
    if a.image:dsp.upload(a.image)
    fig,axes=plt.subplots(2,2,figsize=(11,7));fig.subplots_adjust(bottom=.20,hspace=.35)
    buttons=[]
    def redraw():
        for ax in axes.flat:ax.clear()
        axes[0,0].imshow(dsp.image('dbImage'),cmap='gray',vmin=0,vmax=255);axes[0,0].set_title('Input 80 x 80')
        axes[0,1].imshow(dsp.image('dbTargetImage'),cmap='gray',vmin=0,vmax=255);axes[0,1].set_title('DSP C result')
        mode=dsp.scalar('gMode'); n=np.arange(256)
        if mode in (4,5):
            r=dsp.signal('gFFTReal').astype(float);i=dsp.signal('gFFTImag').astype(float)
            axes[1,0].plot(np.arange(80),dsp.image('dbImage')[40].astype(float)-128)
            axes[1,0].set_xlabel('Image column (pixel)');axes[1,0].set_title('Middle-row samples')
            axes[1,1].plot(np.arange(129)/256,20*np.log10(np.maximum(abs(r+1j*i)[:129],1e-6)))
            axes[1,1].set_xlabel('Spatial frequency (cycles/pixel)');axes[1,1].set_ylabel('dB re 1 integer count')
        else:
            x=dsp.signal('gSignalIn');y=dsp.signal('gSignalOut')
            axes[1,0].plot(n/32,x,label='Input');axes[1,0].plot(n/32,y,label='Output');axes[1,0].legend()
            axes[1,0].set_xlabel('Time (ms), fs=32 kHz')
            axes[1,1].plot(np.arange(129)*125/1000,20*np.log10(np.maximum(abs(np.fft.rfft(y)/256),1e-6)))
            axes[1,1].set_xlabel('Frequency (kHz)');axes[1,1].set_ylabel('dB re 1 integer count')
        edge=dsp.scalar('gCutoffIndex')+1
        filt=f'{edge} kHz' if mode not in (2,3) else f'{(edge-1)%9+1}-{(edge-1)%9+2} kHz'
        fig.suptitle(f'PC SIMULATION ONLY | {MODES[mode]} | edge {filt} | source {dsp.scalar("gSource")} | frame {dsp.scalar("gResultSeq")}')
        fig.canvas.draw_idle()
    def press(k):dsp.key(k);redraw()
    for k,label in enumerate(['1 LPF','2 BPF','3 BRF','4 FFT-C','5 FFT-DIF','6 AM','7 DSB','8 Edge','9 Source'],1):
        ax=fig.add_axes([.03+(k-1)*.105,.07,.095,.045]);b=Button(ax,label)
        b.on_clicked(lambda event,k=k:press(k));buttons.append(b)
    fig.canvas.mpl_connect('key_press_event',lambda e:press(int(e.key)) if e.key in list('123456789') else None)
    redraw();plt.show()


def watch_board(folder):
    folder.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(9,5));last={};images={}
    for ax,name in zip(axes,['input.dat','result.dat']):
        images[name]=ax.imshow(np.zeros((80,80)),cmap='gray',vmin=0,vmax=255)
        ax.set_title(name+' (waiting for CCS export)')
    def update():
        for ax,name in zip(axes,['input.dat','result.dat']):
            path=folder/name
            if not path.exists():continue
            stamp=path.stat().st_mtime_ns
            if last.get(name)==stamp:continue
            try:
                data=read_dat(path)
                if len(data)!=6400 or np.max(data)>255:raise ValueError('Expected 6400 grayscale words.')
                images[name].set_data(data.reshape(80,80));last[name]=stamp
                ax.set_title(name+' (CCS exported snapshot)')
            except (OSError,ValueError) as e:ax.set_title(str(e)[:65])
        fig.canvas.draw_idle()
    timer=fig.canvas.new_timer(interval=750);timer.add_callback(update);timer.start()
    fig.suptitle('BOARD SNAPSHOTS | CCS must halt and export each new frame')
    plt.show()


if __name__=='__main__':main()
