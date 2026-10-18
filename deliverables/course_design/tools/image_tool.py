"""Host image conversion and CCS 16-bit-per-pixel memory exchange."""
from pathlib import Path
import argparse
import re
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def write_dat(path, values):
    v = np.asarray(values).ravel()
    # TI CCS format: magic, radix/encoding, load-address, page, length (hex).
    # Zero header address is a PLACEHOLDER: override start address in CCS.
    text = f'1651 1 0 1 {len(v):x}\n' + '\n'.join(f'0x{int(x)&65535:04x}' for x in v) + '\n'
    Path(path).write_text(text,encoding='ascii')


def read_dat(path):
    lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    if not lines or not lines[0].split() or lines[0].split()[0] != '1651':
        raise ValueError('Expected a CCS text .dat file with 1651 header.')
    header = lines[0].split()
    if len(header) != 5 or header[1] != '1':
        raise ValueError('Export as CCS hexadecimal text format 1; other encodings are not supported.')
    expected = int(header[4],16)
    tokens=[]
    for line in lines[1:]:
        line=line.split('//')[0].split(';')[0].strip()
        if line: tokens.extend(re.split(r'[\s,]+',line))
    # Reject addresses/colon-formatted dumps instead of silently misreading.
    if any(not re.fullmatch(r'(?:0x)?[0-9a-fA-F]{1,4}', t) for t in tokens):
        raise ValueError('Not plain 16-bit hexadecimal CCS data; check the Save Memory format.')
    v=np.array([int(t,16) for t in tokens],dtype=np.uint16)
    if len(v) != expected: raise ValueError(f'Header length {expected}, actual {len(v)}')
    return v


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    c=sub.add_parser('convert');c.add_argument('image');c.add_argument('--out',default=str(ROOT/'assets'/'user_image.dat'))
    d=sub.add_parser('decode');d.add_argument('dat');d.add_argument('--out',default=str(ROOT/'results'/'board_result.png'))
    a=p.parse_args(); dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    if a.action=='convert':
        img=Image.open(a.image).convert('L').resize((80,80),Image.Resampling.LANCZOS)
        write_dat(dst,np.asarray(img));img.save(dst.with_suffix('.png'))
        print(f'{dst}: 6400 target words, each holds one grayscale pixel. Load into dbUserImage, NOT address 0.')
    else:
        v=read_dat(a.dat)
        if len(v)!=6400:raise SystemExit('Expected exactly 6400 words for 80x80 image.')
        if np.max(v)>255:raise SystemExit('Pixel value exceeds 255; wrong target data type/address?')
        Image.fromarray(v.astype(np.uint8).reshape(80,80)).save(dst)
        print(dst)


if __name__=='__main__':main()
