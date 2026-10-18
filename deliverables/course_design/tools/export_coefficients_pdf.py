"""Readable complete 28-bank coefficient appendix, one bank per page."""
from pathlib import Path
import csv
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
ROOT=Path(__file__).resolve().parents[1]


def main():
    groups=defaultdict(list)
    with (ROOT/'results/filter_coefficients.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):groups[int(row['filter_index'])].append(row)
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    out=ROOT/'docs/FIR滤波系数表.pdf';c=canvas.Canvas(str(out),pagesize=(21*cm,29.7*cm))
    c.setTitle('28组257抽头FIR全量Q15系数')
    for idx,rows in sorted(groups.items()):
        c.setFont('STSong-Light',16);c.drawString(2*cm,27.5*cm,f'FIR 定点系数表：第 {idx+1} / 28 组')
        c.setFont('Courier',12);c.drawString(2*cm,26.5*cm,rows[0]['name'])
        c.setFont('STSong-Light',11)
        for j,line in enumerate(['采样率 32000 Hz；抽头数 257；实际系数 = 下列整数 / 32768。',
                                 '每行格式：起始抽头序号：接下来十个抽头；抽头从 0 开始。',
                                 '系数与 v61/tables.c 一致；浮点设计值另见 CSV。']):
            c.drawString(2*cm,(25.6-j*.7)*cm,line)
        c.setFont('Courier',9)
        vals=[int(r['q15_integer']) for r in rows]
        for j,start in enumerate(range(0,257,10)):
            s=f'{start:03d}: '+''.join(f'{v:7d}' for v in vals[start:start+10])
            c.drawString(1.6*cm,(22.7-j*.63)*cm,s)
        c.setFont('STSong-Light',10);c.drawCentredString(10.5*cm,1.2*cm,str(idx+1));c.showPage()
    c.save();print(out)


if __name__=='__main__':main()
