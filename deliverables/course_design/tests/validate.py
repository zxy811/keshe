"""Meaningful algorithm and state-machine checks against independent references."""
from pathlib import Path
import sys
import json
import hashlib
import subprocess
import numpy as np
from scipy.signal import freqz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from host_build import build
from host_api import DSP
from image_tool import write_dat,read_dat


def main():
    build(); dsp=DSP(); checks=[];metrics={}
    def check(name,condition,detail=''):
        passed=bool(condition);checks.append(dict(name=name,passed=passed,detail=detail))
        print(('PASS' if passed else 'FAIL')+' '+name+' '+str(detail))
    specs=json.loads((ROOT/'results'/'filter_specs.json').read_text())
    check('all 28 filters stopband >= 55 dB',min(x['stop_attenuation_dB'] for x in specs)>=55)
    check('all 28 filters passband ripple <= 0.03 dB',max(x['ripple_dB'] for x in specs)<=.03)
    check('all 28 filters absolute passband gain within 0.03 dB',
          all(abs(x['pass_min_dB'])<.03 and abs(x['pass_max_dB'])<.03 for x in specs))
    import ctypes as ct
    fir=np.ctypeslib.as_array((ct.c_int16*(28*257)).in_dll(dsp.lib,'gFIR')).reshape(28,257).copy()
    from generate_tables import designs
    expected=np.array([np.clip(np.rint(h*32768),-32768,32767).astype(np.int16) for *_,h in designs()])
    check('compiled C FIR tables equal independently regenerated design',np.array_equal(fir,expected))
    check('FIR symmetry all banks',np.array_equal(fir,fir[:,::-1]))
    check('32-bit FIR accumulation bound',int(np.max(np.sum(abs(fir.astype(np.int64)),axis=1)))*18000<2**31)
    rng=np.random.default_rng(20261018);n=np.arange(256)
    vectors=[('zero',np.zeros(256)),('impulse',np.r_[16384,np.zeros(255)]),
             ('DC',np.full(256,5000)),('Nyquist',8000*(-1.)**n),
             ('bin_8',np.rint(12000*np.cos(2*np.pi*8*n/256))),
             ('multi',sum(np.rint(4000*np.cos(2*np.pi*k*n/256)) for k in (4,32,72,104))),
             ('random',rng.integers(-8000,8001,256))]
    fft_metrics=[]
    for name,x in vectors:
        ref=np.fft.fft(x)/256
        for asm in (False,True):
            y=dsp.fft(x,asm=asm);err=float(max(abs(y-ref)))
            fft_metrics.append(dict(vector=name,backend='DIF-source-model' if asm else 'DIT-C',max_complex_error=err))
            check('FFT '+name+(' DIF model' if asm else ' C'),err<=6.0,f'max error {err:.5f} integer counts')
    metrics['fft']=fft_metrics
    # Complex-valued vectors exercise both twiddle products and sign paths.
    cr=rng.integers(-5000,5001,256);ci=rng.integers(-5000,5001,256)
    for asm in (False,True):
        err=float(max(abs(dsp.fft(cr,ci,asm=asm)-np.fft.fft(cr+1j*ci)/256)))
        check('FFT complex '+str(asm),err<6,f'{err:.5f}')
    original=dsp.image('dbImage').copy()
    frame=dsp.scalar('gResultSeq');dsp.key(0)
    check('invalid key leaves frame unchanged',frame==dsp.scalar('gResultSeq'))
    for key in range(1,8):
        dsp.key(key)
        check(f'key {key} completes correct mode',dsp.scalar('gMode')==key and dsp.scalar('gBusy')==0)
        check(f'key {key} writes output',int(dsp.image('dbTargetImage').max())>0)
        check(f'key {key} preserves input',np.array_equal(dsp.image('dbImage'),original))
    # Scalar controls and output publication.
    dsp.key(1);start=dsp.scalar('gCutoffIndex')
    for _ in range(10):dsp.key(8)
    check('LPF 10-step cutoff cycle',start==dsp.scalar('gCutoffIndex'))
    dsp.key(2);dsp.scalar('gCutoffIndex',0)
    for _ in range(9):dsp.key(8)
    check('BPF 9-step band cycle',dsp.scalar('gCutoffIndex')==0)
    # Independent NumPy convolution of random uploaded pixels, including borders.
    a=rng.integers(0,256,(80,80),dtype=np.uint8)
    dsp.upload(Image.fromarray(a))
    for mode in (1,2,3):
        dsp.key(mode);idx=dsp.scalar('gFilterIndex')
        ref=np.empty((80,80),np.uint8)
        for row in range(80):
            pad=np.pad(a[row].astype(np.int64)-128,(128,128),mode='reflect')
            v=np.convolve(pad,fir[idx].astype(np.int64),mode='valid')
            ref[row]=np.clip(v//32768+128,0,255)
        check('image FIR independent reference '+str(mode),np.array_equal(ref,dsp.image('dbTargetImage')))
        # Standalone FIR uses periodic extension and centered alignment.
        x=dsp.signal('gSignalIn').astype(np.int64)
        refsig=sum(int(h)*np.roll(x,k-128) for k,h in enumerate(fir[idx]))//32768
        check('signal FIR reference '+str(mode),np.array_equal(refsig,dsp.signal('gSignalOut')))
    dsp.key(4);c=dsp.signal('gFFTReal').astype(float)+1j*dsp.signal('gFFTImag')
    dsp.key(5);d=dsp.signal('gFFTReal').astype(float)+1j*dsp.signal('gFFTImag')
    check('key4/key5 same transform within quantization',max(abs(c-d))<8)
    modulation=[]
    for key in (6,7):
        dsp.key(key);s=abs(np.fft.rfft(dsp.signal('gSignalOut'))/256)
        carrier=float(s[64]);lo=float(s[56]);hi=float(s[72])
        check(('AM' if key==6 else 'DSB')+' sidebands 7/9 kHz',abs(lo-hi)<2 and lo>1000)
        check(('AM' if key==6 else 'DSB')+' carrier behavior',(carrier>8000) if key==6 else carrier<2)
        modulation.append(dict(mode='AM' if key==6 else 'DSB',carrier_count=carrier,lower_count=lo,upper_count=hi))
    metrics['modulation']=modulation
    # Exact .dat round trip prevents pixel packing/endian mistakes.
    target=ROOT/'results'/'test_image.dat';write_dat(target,a)
    check('CCS DAT 6400-word roundtrip',np.array_equal(read_dat(target),a.ravel()))
    target.unlink()
    dsp.scalar('gUserImageReady',0);dsp.scalar('gSource',1);dsp.key(9)
    check('source cycles skip missing user picture',dsp.scalar('gSource')==0)
    dsp.upload(Image.fromarray(a));dsp.key(9)
    check('uploaded source cycle includes built-in source',dsp.scalar('gSource')==0)
    # Dedicated constant input: LPF/BRF retain DC, BPF rejects it.
    dsp.upload(Image.fromarray(np.full((80,80),200,dtype=np.uint8)))
    dsp.key(2)
    check('BPF maps removed DC to neutral gray',abs(float(dsp.image('dbTargetImage').mean())-128)<=1)
    metrics['filters']=specs
    metrics['summary']=dict(total=len(checks),passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks))
    metrics['checks']=checks
    metrics['scope']='Native portable C on Linux; DIF C source model. Not TI assembler, C55x ISA simulation, MATLAB execution, or physical-board testing.'
    metrics['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'v61').glob('*.c'))}
    (ROOT/'results'/'validation.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    print(metrics['summary'])
    return int(metrics['summary']['failed']>0)


if __name__=='__main__':sys.exit(main())
