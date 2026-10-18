function run_all()
% Run in MATLAB: cd('<package>/matlab'); run_all
% No Signal Processing Toolbox needed. All charts created by THIS execution
% go in matlab_output, separate from Python-generated delivered figures.
here = fileparts(mfilename('fullpath'));
root = fileparts(here);
if exist('OCTAVE_VERSION','builtin')
    runtime=['GNU Octave ' OCTAVE_VERSION]; out=fullfile(here,'octave_output');
else
    runtime=['MATLAB ' version]; out=fullfile(here,'matlab_output');
end
if ~exist(out,'dir'), mkdir(out); end
fs = 32000; N = 256; taps = 257; beta = 5.65326;
m = -(taps-1)/2:(taps-1)/2;
win = besseli(0,beta*sqrt(max(0,1-(m/((taps-1)/2)).^2)))/besseli(0,beta);
banks = zeros(28,taps); names = cell(28,1);
for k=1:28
    if k<=10
        lo=k*1000; hi=0; h=(2*lo/fs)*sinc_local(2*lo/fs*m).*win;
        h=h/sum(h); names{k}=sprintf('LPF_%d',lo);
    else
        if k<=19, lo=(k-10)*1000; else, lo=(k-19)*1000; end
        hi=lo+1000;
        h=(2*hi/fs*sinc_local(2*hi/fs*m)-2*lo/fs*sinc_local(2*lo/fs*m));
        if k<=19
            h=h.*win; h=h/sum(h.*cos(2*pi*((lo+hi)/2)/fs*m));
            names{k}=sprintf('BPF_%d_%d',lo,hi);
        else
            h=-h;h((taps+1)/2)=h((taps+1)/2)+1;h=h.*win;h=h/sum(h);
            names{k}=sprintf('BRF_%d_%d',lo,hi);
        end
    end
    q=max(-32768,min(32767,round(h*32768)));banks(k,:)=q;
    H=fft(q/32768,131072);H=H(1:65536);f=(0:65535)*fs/131072;
    fig=figure('Visible','off','Position',[100 100 1000 650]);
    subplot(2,1,1);plot(f/1000,20*log10(max(abs(H),1e-12)));grid on;
    ylim([-110 5]);xlim([0 fs/2000]);xlabel('Frequency (kHz)');ylabel('Magnitude (dB)');
    title([names{k} ' | Q15 FIR | fs=32 kHz'],'Interpreter','none');
    subplot(2,1,2);plot(f/1000,unwrap(angle(H))*180/pi);grid on;
    xlim([0 fs/2000]);xlabel('Frequency (kHz)');ylabel('Unwrapped phase (deg)');
    print(fig,fullfile(out,[names{k} '_bode.png']),'-dpng','-r160');close(fig);
end
csvwrite(fullfile(out,'coefficients_q15.csv'),banks);
% Compare with delivered design, not with an independently rounded display.
fid=fopen(fullfile(root,'results','filter_coefficients.csv'),'r');
if fid<0, error('Missing results/filter_coefficients.csv'); end
C=textscan(fid,'%f%s%s%f%f%f%f%f%f','Delimiter',',','HeaderLines',1);fclose(fid);
delivered=reshape(C{8},taps,28).';
maxdiff=max(abs(banks(:)-delivered(:)));
fprintf('%s vs delivered Q15 coefficients max difference = %g counts\n',runtime,maxdiff);
assert(maxdiff==0,'Coefficient mismatch; inspect software versions before using tables.');
% Coherent 256-point multitone FFT, exact bin spacing 125 Hz.
n=0:N-1;x=round(4500*(cos(2*pi*500*n/fs)+cos(2*pi*4000*n/fs)+cos(2*pi*9000*n/fs)+cos(2*pi*13000*n/fs)));
X=fft(x)/N;XC=fft_fixed(x,0);XD=fft_fixed(x,1);
errC=max(abs(XC-X));errD=max(abs(XD-X));
fprintf('Fixed FFT max complex error: DIT %.9g, DIF %.9g counts\n',errC,errD);
assert(errC<6 && errD<6,'FFT error exceeds documented range.');
fig=figure('Visible','off','Position',[100 100 1000 650]);
subplot(2,1,1);plot(n/fs*1000,x);grid on;xlabel('Time (ms)');ylabel('Input counts');
subplot(2,1,2);stem((0:128)*fs/N/1000,abs(X(1:129)),'DisplayName',[runtime ' fft/N']);hold on;
plot((0:128)*fs/N/1000,abs(XC(1:129)),'r.','DisplayName','Q15 DIT model');
plot((0:128)*fs/N/1000,abs(XD(1:129)),'gx','DisplayName','Q15 DIF model');
xlabel('Frequency (kHz)');ylabel('Normalized DFT magnitude');grid on;legend('show');
print(fig,fullfile(out,'fft_reference.png'),'-dpng','-r160');close(fig);
csvwrite(fullfile(out,'fft_reference.csv'),[(0:N-1).',real(X(:)),imag(X(:)),real(XC(:)),imag(XC(:)),real(XD(:)),imag(XD(:))]);
% AM and DSB. Distinguish theoretical unquantized signals and Q15 outputs.
message=round(12000*cos(2*pi*1000*n/fs));carrier=repmat([32767 0 -32767 0],1,64);
am=floor((16384+fix(message/2)).*carrier/32768);dsb=floor(message.*carrier/32768);
fig=figure('Visible','off','Position',[100 100 1000 750]);
for k=1:2
    if k==1,y=am;lab='AM';else,y=dsb;lab='DSB-SC';end
    subplot(2,2,2*k-1);plot(n/fs*1000,y);grid on;title(lab);xlabel('Time (ms)');ylabel('Counts');
    Y=abs(fft(y)/N);
    subplot(2,2,2*k);stem((0:128)*fs/N/1000,Y(1:129));
    grid on;xlabel('Frequency (kHz)');ylabel('Magnitude');
end
print(fig,fullfile(out,'modulation_reference.png'),'-dpng','-r160');close(fig);
save(fullfile(out,'simulation.mat'),'banks','fs','N','x','X','XC','XD','am','dsb');
fid=fopen(fullfile(out,'RUN_COMPLETED.txt'),'w');
fprintf(fid,'Executed by: %s\n',runtime);
fprintf(fid,'Coefficient maxdiff=%g; DIT error=%g; DIF error=%g\n',maxdiff,errC,errD);fclose(fid);
fprintf('Outputs: %s\n',out);
end

function y=sinc_local(x)
y=ones(size(x));nz=(x~=0);y(nz)=sin(pi*x(nz))./(pi*x(nz));
end

function z=fft_fixed(x,dif)
N=256;z=complex(double(x),zeros(size(x)));w=round(32767*exp(-2i*pi*(0:127)/N));
if dif, spans=256./(2.^(0:7));else,z=bitreverse_local(z);spans=2.^(1:8);end
for span=spans
    half=span/2;
    for base=0:span:N-1
        for k=0:half-1
            i=base+k+1;j=i+half;idx=k*N/span;
            a=z(i);b=z(j);
            if dif
                z(i)=sat_complex(fix_complex((a+b)/2));d=fix_complex((a-b)/2);
                t=multiply_twiddle(d,w(idx+1),idx);z(j)=sat_complex(t);
            else
                t=multiply_twiddle(b,w(idx+1),idx);
                z(i)=sat_complex(fix_complex((a+t)/2));z(j)=sat_complex(fix_complex((a-t)/2));
            end
        end
    end
end
if dif,z=bitreverse_local(z);end
end

function y=multiply_twiddle(x,w,k)
if k==0,y=x;elseif k==64,y=complex(imag(x),-real(x));
else,y=complex(floor((real(x)*real(w)-imag(x)*imag(w))/32768),floor((real(x)*imag(w)+imag(x)*real(w))/32768));end
end

function y=fix_complex(x)
y=complex(fix(real(x)),fix(imag(x)));
end

function y=sat_complex(x)
y=complex(max(-32768,min(32767,real(x))),max(-32768,min(32767,imag(x))));
end

function y=bitreverse_local(x)
N=256;y=x;
for n=0:N-1
    b=n;r=0;
    for k=1:8,r=2*r+mod(b,2);b=floor(b/2);end
    y(r+1)=x(n+1);
end
end
