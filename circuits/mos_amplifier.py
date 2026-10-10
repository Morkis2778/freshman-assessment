"""Common-source amplifier. K convention: ID=K*Vov^2*(1+lambda*VDS)."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import spice_compat  # preserve genuine errors; ignore only solver banner
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
OUT=Path(__file__).resolve().parent/'results';OUT.mkdir(exist_ok=True)
VDD,RG1,RG2,RD,K,VTH,LAM=5.,60000.,40000.,2000.,.0008,1.,.02

def build(k=K):
    c=Circuit('NMOS common source')
    c.V('dd','vdd',c.gnd,VDD@u_V)
    c.SinusoidalVoltageSource('in','vin',c.gnd,amplitude=10@u_mV,frequency=1@u_kHz)
    c.C('b1','vin','gate',100@u_uF)
    c.R('g1','vdd','gate',RG1@u_Ohm);c.R('g2','gate',c.gnd,RG2@u_Ohm);c.R('d','vdd','drain',RD@u_Ohm)
    # MOS1 saturation uses 0.5*KP*(W/L), hence KP=2*K and W/L=1.
    c.model('NM','NMOS',level=1,kp=2*k,vto=VTH,**{'lambda':LAM},gamma=0,tnom=27)
    c.MOSFET(1,'drain','gate',c.gnd,c.gnd,model='NM',w=10@u_um,l=10@u_um)
    return c

def theory(k=K):
    vgs=VDD*RG2/(RG1+RG2);ov=vgs-VTH
    i=k*ov**2*(1+LAM*VDD)/(1+k*ov**2*LAM*RD)
    vd=VDD-i*RD;gm=2*k*ov*(1+LAM*vd);gds=k*ov**2*LAM;ro=1/gds;av=-gm/(1/RD+gds)
    return {'VGS_V':vgs,'ID_A':i,'VDS_V':vd,'gm_S':gm,'gds_S':gds,'ro_ohm':ro,'Av':av,'saturation':vd>=ov}

def main():
    th=theory();c=build();sim=c.simulator(temperature=27,nominal_temperature=27)
    sim.save(['v(gate)','v(drain)','v(vin)','@m1[gm]','@m1[gds]'])
    op=sim.operating_point();vg=float(np.asarray(op['gate']).item());vd=float(np.asarray(op['drain']).item());id_=(VDD-vd)/RD
    gm=float(np.asarray(op['@m1[gm]']).item());gds=float(np.asarray(op['@m1[gds]']).item())
    tr=sim.transient(step_time=2@u_us,end_time=10@u_ms)
    t,vi,vo=map(np.asarray,(tr.time,tr['vin'],tr['drain']))
    # Fit sine/cosine and DC on the last five periods, preserving inversion sign.
    mask=t>=.005;A=np.column_stack([np.sin(2*np.pi*1000*t[mask]),np.cos(2*np.pi*1000*t[mask]),np.ones(mask.sum())])
    a_in=np.linalg.lstsq(A,vi[mask],rcond=None)[0];a_out=np.linalg.lstsq(A,vo[mask],rcond=None)[0]
    amp_in=float(np.hypot(*a_in[:2]));amp_out=float(np.hypot(*a_out[:2]));gain=-amp_out/amp_in
    phase=float(np.angle(complex(a_out[0],a_out[1])/complex(a_in[0],a_in[1]),deg=True))
    fig,ax=plt.subplots(2,1,figsize=(8,6),sharex=True)
    view=t>=.007;ax[0].plot(t[view]*1000,vi[view]*1000);ax[0].set_ylabel('Input (mV)');ax[0].set_title('Common-source amplifier: 10 mV / 1 kHz')
    ax[1].plot(t[view]*1000,vo[view]);ax[1].set_ylabel('Output (V)');ax[1].set_xlabel('Time (ms)')
    for a in ax:a.grid(alpha=.25)
    fig.tight_layout();fig.savefig(OUT/'mos_waveform.png',dpi=160);plt.close(fig)
    np.savetxt(OUT/'mos_transient.csv',np.column_stack([t,vi,vo]),delimiter=',',header='time_s,input_V,output_V',comments='')
    other=build(K/2).simulator(temperature=27,nominal_temperature=27).operating_point()
    result={'convention':'ID = K * Vov^2 * (1 + lambda * VDS); KP=2K at W/L=1','theory':th,'simulation':{'VGS_V':vg,'ID_A':id_,'VDS_V':vd,'gm_S':gm,'gds_S':gds,'Av_transient':gain,'phase_deg':phase,'input_amplitude_V':amp_in,'output_amplitude_V':amp_out,'saturation':vd>=vg-VTH},'alternative_half_K':{'theory':theory(K/2),'simulation':{'VGS_V':float(np.asarray(other['gate']).item()),'VDS_V':float(np.asarray(other['drain']).item()),'ID_A':(VDD-float(np.asarray(other['drain']).item()))/RD}}}
    (OUT/'mos.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    assert abs(id_/th['ID_A']-1)<.001 and abs(gm/th['gm_S']-1)<.001
    assert abs(gain/th['Av']-1)<.01 and abs(abs(phase)-180)<1
if __name__=='__main__':main()
