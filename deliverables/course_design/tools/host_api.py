from pathlib import Path
import ctypes as ct
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


class DSP:
    def __init__(self):
        lib=ROOT/'results'/('dsp_host.dll' if sys.platform=='win32' else 'libdsp_host.so')
        if not lib.exists():
            from host_build import build
            lib=build()
        self.lib=ct.CDLL(str(lib))
        self.lib.app_handle_key.argtypes=[ct.c_uint]
        for name in ('fft_c','fft_asm'):
            getattr(self.lib,name).argtypes=[ct.POINTER(ct.c_int16)]*2
        self.lib.app_init()

    def scalar(self,name,value=None):
        v=ct.c_uint.in_dll(self.lib,name) # host unsigned int; NOT target memory layout
        if value is not None:v.value=value
        return v.value

    def image(self,name):
        return np.ctypeslib.as_array((ct.c_ubyte*6400).in_dll(self.lib,name)).reshape(80,80)

    def signal(self,name):
        return np.ctypeslib.as_array((ct.c_int16*256).in_dll(self.lib,name))

    def key(self,k):self.lib.app_handle_key(k)

    def upload(self,image):
        from PIL import Image
        if isinstance(image,(str,Path)):image=Image.open(image)
        a=np.array(image.convert('L').resize((80,80),Image.Resampling.LANCZOS),dtype=np.uint8)
        self.image('dbUserImage')[:]=a
        self.scalar('gUserImageReady',1);self.scalar('gSource',2)
        self.lib.app_process()

    def fft(self,re,im=None,asm=False):
        r=np.asarray(re,dtype=np.int16).copy()
        i=np.zeros(256,dtype=np.int16) if im is None else np.asarray(im,dtype=np.int16).copy()
        if r.shape!=(256,) or i.shape!=(256,):raise ValueError('FFT requires 256 samples.')
        getattr(self.lib,'fft_asm' if asm else 'fft_c')(r.ctypes.data_as(ct.POINTER(ct.c_int16)),i.ctypes.data_as(ct.POINTER(ct.c_int16)))
        return r.astype(float)+1j*i.astype(float)
