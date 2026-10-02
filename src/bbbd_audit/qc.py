"""Chunked statistics, BDF24 decoding and descriptive spectra."""
import json
import numpy as np
import pandas as pd
from scipy.signal import welch
from .io import ROOT

CONFIG=json.loads((ROOT/"audit_config.json").read_text())

def longest_true(a):
    a=np.asarray(a,bool)
    edges=np.diff(np.r_[False,a,False].astype(np.int8))
    starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
    return int(np.max(ends-starts)) if len(starts) else 0

def intervals_to_mask(intervals,n,fs=128):
    """Half-open seconds intervals; clipping and quantization explicitly counted."""
    mask=np.zeros(n,bool);out_of_bounds=0
    for start,end in intervals:
        if not np.isfinite(start+end) or end<start: raise ValueError("Invalid correction interval")
        lo=int(np.floor(start*fs+1e-6));hi=int(np.ceil(end*fs-1e-6))
        if lo<0 or hi>n:out_of_bounds+=1
        mask[max(0,lo):min(n,hi)]=True
    return mask,out_of_bounds

def decode_bdf24(b):
    v=np.frombuffer(b,dtype=np.uint8).reshape(-1,3).astype(np.int32)
    x=v[:,0]|(v[:,1]<<8)|(v[:,2]<<16)
    return (x ^ 0x800000)-0x800000

def bdf_header(f):
    base=f.read(256)
    if len(base)!=256 or base[:1]!=b'\xff':raise ValueError("Not BDF24")
    nc=int(base[252:256]);header_bytes=int(base[184:192]);nr=int(base[236:244]);rd=float(base[244:252])
    remaining=f.read(header_bytes-256)
    offset=0;fields={}
    for key,width in [("labels",16),("transducer",80),("units",8),("physical_min",8),("physical_max",8),("digital_min",8),("digital_max",8),("prefilter",80),("samples_per_record",8),("reserved",32)]:
        fields[key]=[remaining[offset+i*width:offset+(i+1)*width].decode('latin1').strip() for i in range(nc)];offset+=nc*width
    for key in ["physical_min","physical_max","digital_min","digital_max","samples_per_record"]:fields[key]=np.array(fields[key],float)
    fields.update(channels=nc,records=nr,record_seconds=rd,header_bytes=header_bytes)
    return fields

def bdf_chunks(f,h):
    ns=h["samples_per_record"].astype(int)
    if len(set(ns))!=1:raise ValueError("Mixed BDF rates unsupported; refuse rather than guess")
    per=int(ns[0]);record_bytes=3*int(ns.sum());nc=h['channels']
    gain=(h['physical_max']-h['physical_min'])/(h['digital_max']-h['digital_min'])
    intercept=h['physical_min']-gain*h['digital_min']
    left=h['records']
    while left:
        nr=min(CONFIG['bdf_chunk_records'],left);b=f.read(record_bytes*nr)
        if len(b)!=record_bytes*nr:raise ValueError("Truncated BDF")
        digital=decode_bdf24(b).reshape(nr,nc,per).transpose(0,2,1).reshape(nr*per,nc)
        yield digital*gain+intercept,digital
        left-=nr
    if f.read(1):raise ValueError("Unexpected BDF trailing bytes")

class Stats:
    def __init__(self,channels,fs=128):
        self.c=channels;self.fs=fs;self.n=0
        self.count=np.zeros(channels,np.int64);self.mean=np.zeros(channels);self.m2=np.zeros(channels)
        self.nan=np.zeros(channels,np.int64);self.inf=self.nan.copy();self.zero=self.nan.copy()
        self.minimum=np.full(channels,np.inf);self.maximum=-self.minimum
        self.saturation=self.nan.copy();self.samples=[];self.psd=None;self.psd_weight=0
        self.invalid_rows=0;self.all_zero_rows=0;self.zero_tail=0;self.longest_allzero=0
    def update(self,x,digital=None,dmin=None,dmax=None):
        x=np.asarray(x,float)
        if x.ndim==1:x=x[:,None]
        ok=np.isfinite(x);n=ok.sum(axis=0);sx=np.where(ok,x,0).sum(axis=0);mu=np.divide(sx,n,out=np.zeros(self.c),where=n>0)
        m2=np.where(ok,(x-mu)**2,0).sum(axis=0);delta=mu-self.mean;total=self.count+n
        self.m2+=m2+np.divide(delta**2*self.count*n,total,out=np.zeros(self.c),where=total>0)
        self.mean+=np.divide(delta*n,total,out=np.zeros(self.c),where=total>0);self.count=total
        self.nan+=np.isnan(x).sum(axis=0);self.inf+=np.isinf(x).sum(axis=0);self.zero+=(x==0).sum(axis=0)
        self.minimum=np.minimum(self.minimum,np.min(np.where(ok,x,np.inf),axis=0));self.maximum=np.maximum(self.maximum,np.max(np.where(ok,x,-np.inf),axis=0))
        self.invalid_rows+=int((~ok.all(axis=1)).sum())
        az=(x==0).all(axis=1);self.all_zero_rows+=int(az.sum())
        if len(az):
            lead=int(np.argmax(~az)) if (~az).any() else len(az)
            self.longest_allzero=max(self.longest_allzero,longest_true(az),self.zero_tail+lead)
            self.zero_tail=int(np.argmax(~az[::-1])) if (~az).any() else self.zero_tail+len(az)
        if digital is not None:self.saturation+=((digital==dmin)|(digital==dmax)).sum(axis=0)
        # Deterministic bounded decimation for quantile summaries, not exact quantiles.
        idx=np.arange((-self.n)%32,len(x),32)
        self.samples.append(x[idx])
        self.n+=len(x)
        nper=min(int(self.fs*CONFIG['welch_seconds']),len(x))
        if nper>=int(self.fs*4):
            freqs,psd=welch(np.where(ok,x,0),fs=self.fs,nperseg=nper,noverlap=nper//2,axis=0)
            if nper==int(self.fs*CONFIG['welch_seconds']):
                weight=1+(len(x)-nper)//(nper//2)
                if self.psd is None:self.psd=psd*weight;self.freqs=freqs
                else:self.psd+=psd*weight
                self.psd_weight+=weight
    def result(self,names):
        std=np.sqrt(np.divide(self.m2,self.count,out=np.zeros(self.c),where=self.count>0))
        samples=np.concatenate(self.samples) if self.samples else np.empty((0,self.c))
        rows=[]
        for c,name in enumerate(names):
            ss=samples[:,c];ss=ss[np.isfinite(ss)]
            row=dict(channel=name,samples=self.n,finite_samples=int(self.count[c]),nan_count=int(self.nan[c]),inf_count=int(self.inf[c]),zero_count=int(self.zero[c]),zero_fraction=float(self.zero[c]/self.n) if self.n else 0,mean=float(self.mean[c]),std=float(std[c]),minimum=float(self.minimum[c]),maximum=float(self.maximum[c]),flat=bool(std[c]<=CONFIG['basic_qc']['flat_std_epsilon']),saturated_samples=int(self.saturation[c]),decimated_q01=float(np.quantile(ss,.01)) if len(ss) else np.nan,decimated_q50=float(np.quantile(ss,.5)) if len(ss) else np.nan,decimated_q99=float(np.quantile(ss,.99)) if len(ss) else np.nan)
            if self.psd is not None:
                f=self.freqs;p=self.psd[:,c]/self.psd_weight
                def band(a,b):return float(np.sum(p[(f>=a)&(f<b)])*(f[1]-f[0]))
                total=band(.5,45)
                for name2,(lo,hi) in {'delta':(.5,4),'theta':(4,8),'alpha':(8,13),'beta':(13,30),'gamma':(30,45)}.items():row['power_'+name2]=band(lo,hi)
                peak=np.mean(p[(f>=15.75)&(f<=16.25)])
                ref=np.mean(p[((f>=14.5)&(f<=15.5))|((f>=16.5)&(f<=17.5))])
                row['excess_16hz_db']=float(10*np.log10(max(peak,1e-30)/max(ref,1e-30)))
                row['fraction_16hz']=band(15.75,16.375)/max(total,1e-30)
                peak60=np.mean(p[(f>=59.75)&(f<=60.25)]);ref60=np.mean(p[((f>=58)&(f<=59))|((f>=61)&(f<=62))])
                row['excess_60hz_db']=float(10*np.log10(max(peak60,1e-30)/max(ref60,1e-30)))
                rf=f[(f>=.067)&(f<=1)];rp=p[(f>=.067)&(f<=1)]
                row['low_frequency_dominant_hz']=float(rf[np.argmax(rp)]) if len(rf) else np.nan
            rows.append(row)
            if self.count[c]==0:
                for field in ['mean','std','minimum','maximum']:row[field]=np.nan
                row['flat']=False
        return rows

def timestamp_metrics(peaks, event_type='rpeak'):
    p=np.asarray(peaks,float);rr=np.diff(p);valid=rr[np.isfinite(rr)&(rr>0)]
    if event_type == 'breath_peak':
        return dict(peak_count=len(p),nonfinite_peak_count=int((~np.isfinite(p)).sum()),first_peak_seconds=float(p[0]) if len(p) else None,last_peak_seconds=float(p[-1]) if len(p) else None,duplicate_peaks=int((rr==0).sum()),nonmonotonic_peaks=int((rr<0).sum()),breath_interval_median_seconds=float(np.median(valid)) if len(valid) else None,breath_interval_min_seconds=float(np.min(valid)) if len(valid) else None,breath_interval_max_seconds=float(np.max(valid)) if len(valid) else None,median_breaths_per_minute=float(np.median(60/valid)) if len(valid) else None,breath_interval_outside_4_60_bpm_fraction=float(((valid<1)|(valid>15)).mean()) if len(valid) else None)
    if event_type != 'rpeak':raise ValueError('Unknown peak semantics')
    return dict(peak_count=len(p),first_peak_seconds=float(p[0]) if len(p) else None,last_peak_seconds=float(p[-1]) if len(p) else None,duplicate_peaks=int((rr==0).sum()),nonmonotonic_peaks=int((rr<0).sum()),rr_median_seconds=float(np.median(valid)) if len(valid) else None,rr_min_seconds=float(np.min(valid)) if len(valid) else None,rr_max_seconds=float(np.max(valid)) if len(valid) else None,rr_outside_40_160_fraction=float(((valid<.375)|(valid>1.5)).mean()) if len(valid) else None,rr_outside_30_200_fraction=float(((valid<.3)|(valid>2)).mean()) if len(valid) else None,median_hr_bpm=float(np.median(60/valid)) if len(valid) else None,rms_rr_seconds=float(np.sqrt(np.mean(valid**2))) if len(valid) else None,true_rmssd_seconds=float(np.sqrt(np.mean(np.diff(valid)**2))) if len(valid)>1 else None)
