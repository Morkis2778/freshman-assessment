"""RC low-pass: PySpice transient + AC. Run from any working directory."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import spice_compat  # preserve genuine errors; ignore only solver banner
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
OUT = Path(__file__).resolve().parent / 'results'
OUT.mkdir(exist_ok=True)
R, C = 1000.0, 1e-6

def main():
    circuit = Circuit('RC low pass')
    circuit.PulseVoltageSource('input', 'vin', circuit.gnd, initial_value=0@u_V,
        pulsed_value=1@u_V, delay_time=1@u_ms, rise_time=1@u_us,
        fall_time=1@u_us, pulse_width=5@u_ms, period=10@u_ms)
    circuit.R(1, 'vin', 'vout', R@u_Ohm)
    circuit.C(1, 'vout', circuit.gnd, C@u_F)
    sim = circuit.simulator(temperature=27, nominal_temperature=27)
    tr = sim.transient(step_time=5@u_us, end_time=31@u_ms)
    t, vi, vo = map(np.asarray, (tr.time, tr['vin'], tr['vout']))
    # Fit log(1-vout) during the first rising plateau; no analytic output substituted.
    mask = (t>0.00105)&(t<0.004)
    tau_measured = -1/np.polyfit(t[mask], np.log(1-vo[mask]), 1)[0]
    plt.figure(figsize=(8,4)); plt.plot(t*1000,vi,label='Input');plt.plot(t*1000,vo,label='Output')
    plt.xlabel('Time (ms)');plt.ylabel('Voltage (V)');plt.title('RC square-wave response');plt.legend();plt.grid(alpha=.25);plt.tight_layout();plt.savefig(OUT/'rc_transient.png',dpi=160);plt.close()
    ac_circuit = Circuit('RC AC response')
    ac_circuit.SinusoidalVoltageSource('input','vin',ac_circuit.gnd,amplitude=1@u_V)
    ac_circuit.R(1,'vin','vout',R@u_Ohm);ac_circuit.C(1,'vout',ac_circuit.gnd,C@u_F)
    ac = ac_circuit.simulator(temperature=27,nominal_temperature=27).ac(variation='dec',number_of_points=200,start_frequency=1@u_Hz,stop_frequency=100@u_kHz)
    f=np.asarray(ac.frequency); h=np.asarray(ac['vout'])/np.asarray(ac['vin']);db=20*np.log10(np.abs(h))
    fc_measured=float(np.exp(np.interp(20*np.log10(1/np.sqrt(2)),db[::-1],np.log(f[::-1]))))
    fig,ax=plt.subplots(2,1,figsize=(8,6),sharex=True)
    ax[0].semilogx(f,db);ax[0].axhline(-3.0103,color='gray',ls='--');ax[0].set_ylabel('Magnitude (dB)');ax[0].set_title('RC Bode plot')
    ax[1].semilogx(f,np.angle(h,deg=True));ax[1].set_ylabel('Phase (degrees)');ax[1].set_xlabel('Frequency (Hz)')
    for a in ax:a.grid(alpha=.25)
    fig.tight_layout();fig.savefig(OUT/'rc_bode.png',dpi=160);plt.close(fig)
    np.savetxt(OUT/'rc_transient.csv',np.column_stack([t,vi,vo]),delimiter=',',header='time_s,input_V,output_V',comments='')
    np.savetxt(OUT/'rc_ac.csv',np.column_stack([f,db,np.angle(h,deg=True)]),delimiter=',',header='frequency_Hz,magnitude_dB,phase_deg',comments='')
    result={'R_ohm':R,'C_F':C,'tau_theory_s':R*C,'tau_sim_s':float(tau_measured),'fc_theory_Hz':1/(2*np.pi*R*C),'fc_sim_Hz':fc_measured}
    (OUT/'rc.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    assert abs(tau_measured/(R*C)-1)<.01
    assert abs(fc_measured/result['fc_theory_Hz']-1)<.01
if __name__=='__main__':main()
