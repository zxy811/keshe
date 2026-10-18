"""Generate delivered figures from verified C outputs and SciPy references.
These files are explicitly Python-generated, not claimed as MATLAB runs.
"""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'results'/'mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from scipy.signal import freqz
from PIL import Image,ImageDraw
from host_api import DSP
from generate_tables import designs
from image_tool import write_dat


def main():
    out=ROOT/'results'/'figures';out.mkdir(exist_ok=True)
    img=Image.new('L',(80,80),25);draw=ImageDraw.Draw(img)
    for x in range(80):draw.line((x,0,x,79),fill=round(255*x/79))
    draw.rectangle((8,8,32,32),fill=230);draw.ellipse((40,8,70,38),fill=25)
    draw.rectangle((8,45,70,70),fill=128)
    for x in range(10,69,4):draw.line((x,47,x,68),fill=230,width=1)
    img.save(ROOT/'assets'/'demo_input.png');write_dat(ROOT/'assets'/'demo_input.dat',np.array(img))
    # Plot all filter responses, preserving magnitude AND phase.
    all_designs=list(designs())
    with PdfPages(out/'all_28_bode_Python.pdf') as pdf:
        for idx,(name,typ,lo,hi,h) in enumerate(all_designs):
            q=np.rint(h*32768)/32768
            f,H=freqz(q,worN=16384,fs=32000)
            fig,ax=plt.subplots(2,1,figsize=(9,6),sharex=True)
            ax[0].plot(f/1000,20*np.log10(np.maximum(abs(H),1e-12)))
            ax[0].set_ylim(-110,5);ax[0].set_ylabel('Magnitude (dB)')
            ax[1].plot(f/1000,np.unwrap(np.angle(H))*180/np.pi)
            ax[1].set_ylabel('Unwrapped phase (degree)');ax[1].set_xlabel('Frequency (kHz)')
            for a in ax:
                a.grid(True,alpha=.3)
                for edge in ([lo] if not hi else [lo,hi]):a.axvline(edge/1000,color='r',ls='--',lw=.7)
            fig.suptitle(f'{idx}: {name} | 257-tap Q15 FIR | fs=32 kHz | Python/SciPy')
            fig.tight_layout();pdf.savefig(fig);fig.savefig(out/(name+'_bode.png'),dpi=130);plt.close(fig)
    fig,ax=plt.subplots(3,2,figsize=(10,8))
    for row,idx in enumerate([3,13,22]):
        name,typ,lo,hi,h=all_designs[idx];f,H=freqz(np.rint(h*32768)/32768,worN=8192,fs=32000)
        ax[row,0].plot(f/1000,20*np.log10(np.maximum(abs(H),1e-12)));ax[row,0].set_ylim(-100,3)
        ax[row,1].plot(f/1000,np.unwrap(np.angle(H))*180/np.pi)
        ax[row,0].set_title(name+' magnitude (dB)');ax[row,1].set_title(name+' phase (deg)')
        for a in ax[row]:a.set_xlabel('Frequency (kHz)');a.grid(alpha=.3)
    fig.suptitle('Representative Bode plots | Python-generated');fig.tight_layout();fig.savefig(out/'bode_summary.png',dpi=160);plt.close(fig)
    dsp=DSP();dsp.upload(img)
    fig,ax=plt.subplots(2,4,figsize=(12,6))
    ax[0,0].imshow(img,cmap='gray',vmin=0,vmax=255);ax[0,0].set_title('Input / source=2')
    for key,a in zip(range(1,8),list(ax.flat)[1:]):
        dsp.key(key);v=dsp.image('dbTargetImage').copy()
        Image.fromarray(v).save(out/f'key_{key}_result.png')
        a.imshow(v,cmap='gray',vmin=0,vmax=255);a.set_title(f'Key {key}: '+['LPF','BPF','BRF','FFT DIT','FFT DIF model','AM','DSB'][key-1])
    for a in ax.flat:a.axis('off')
    fig.suptitle('Actual portable C outputs, run on host | not board photographs')
    fig.tight_layout();fig.savefig(out/'image_results.png',dpi=180);plt.close(fig)
    n=np.arange(256);x=dsp.signal('gSignalIn').copy()
    # Restore test signal, then independently exercise both FFT entry points.
    dsp.key(1);x=dsp.signal('gSignalIn').copy();ref=np.fft.fft(x)/256
    c=dsp.fft(x);d=dsp.fft(x,asm=True)
    np.savetxt(ROOT/'results'/'fft_c_and_dif.csv',np.c_[n,x,ref.real,ref.imag,c.real,c.imag,d.real,d.imag],delimiter=',',header='n,input,reference_re,reference_im,c_re,c_im,dif_model_re,dif_model_im',comments='')
    fig,ax=plt.subplots(2,1,figsize=(10,6))
    ax[0].plot(n/32,x);ax[0].set_xlabel('Time (ms)');ax[0].set_ylabel('Input count');ax[0].grid(alpha=.3)
    ax[1].stem(n[:129]*.125,abs(ref[:129]),label='NumPy FFT/N',basefmt=' ')
    ax[1].plot(n[:129]*.125,abs(c[:129]),'r.',label='Portable C DIT')
    ax[1].plot(n[:129]*.125,abs(d[:129]),'gx',ms=4,label='DIF source model')
    ax[1].set_xlabel('Frequency (kHz)');ax[1].set_ylabel('Magnitude count');ax[1].legend();ax[1].grid(alpha=.3)
    fig.suptitle('FFT verification | Python + actual C | peaks 0.5, 4, 9, 13 kHz');fig.tight_layout();fig.savefig(out/'fft_validation.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(10,6))
    for row,key in enumerate([6,7]):
        dsp.key(key);y=dsp.signal('gSignalOut').copy();x=dsp.signal('gSignalIn').copy();Y=np.fft.rfft(y)/256
        ax[row,0].plot(n/32,y);ax[row,0].set_xlabel('Time (ms)');ax[row,0].set_ylabel('Output count')
        ax[row,1].stem(n[:129]*.125,abs(Y),basefmt=' ');ax[row,1].set_xlabel('Frequency (kHz)');ax[row,1].set_ylabel('Magnitude count')
        ax[row,0].set_title('AM' if key==6 else 'DSB-SC')
        for a in ax[row]:a.grid(alpha=.3)
        np.savetxt(ROOT/'results'/('am_c.csv' if key==6 else 'dsb_c.csv'),np.c_[n,x,y],delimiter=',',header='n,message,output',comments='')
    fig.suptitle('C modulation results | carrier 8 kHz, message 1 kHz | Python plots')
    fig.tight_layout();fig.savefig(out/'modulation_validation.png',dpi=160);plt.close(fig)
    # Example exported snapshots support the board viewer's real parser.
    snapshots=ROOT/'assets'/'example_board_exports';snapshots.mkdir(exist_ok=True)
    write_dat(snapshots/'input.dat',dsp.image('dbImage'))
    write_dat(snapshots/'result.dat',dsp.image('dbTargetImage'))
    (snapshots/'SIMULATED_EXAMPLES.txt').write_text('These are host-generated parser examples, not physical-board measurements.\n')
    print(out)


if __name__=='__main__':main()
