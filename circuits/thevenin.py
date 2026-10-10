"""Open circuit, short circuit, loaded network and loaded equivalent."""
from pathlib import Path
import json
import numpy as np
import spice_compat  # preserve genuine errors; ignore only solver banner
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
OUT=Path(__file__).resolve().parent/'results';OUT.mkdir(exist_ok=True)
VS,R1,R2,RL=12.0,1000.0,2000.0,1000.0

def network(load=None,short=False):
    c=Circuit('Thevenin original network');c.V('source','vcc',c.gnd,VS@u_V)
    c.R(1,'vcc','port',R1@u_Ohm);c.R(2,'port',c.gnd,R2@u_Ohm)
    if short:c.V('sense','port',c.gnd,0@u_V)
    elif load:c.R('load','port',c.gnd,load@u_Ohm)
    return c.simulator(temperature=27,nominal_temperature=27).operating_point()

def main():
    vth=VS*R2/(R1+R2);rth=R1*R2/(R1+R2)
    oc=network();sc=network(short=True);loaded=network(load=RL)
    voc=float(np.asarray(oc['port']).item());isc=float(np.asarray(sc.branches['vsense']).item());vl=float(np.asarray(loaded['port']).item())
    c=Circuit('Thevenin equivalent');c.V('th','n',c.gnd,vth@u_V);c.R('th','n','port',rth@u_Ohm);c.R('load','port',c.gnd,RL@u_Ohm)
    eq=c.simulator(temperature=27,nominal_temperature=27).operating_point();veq=float(np.asarray(eq['port']).item())
    result={'Voc_theory_V':vth,'Voc_sim_V':voc,'Isc_theory_A':VS/R1,'Isc_sim_A':isc,'Rth_theory_ohm':rth,'Rth_sim_ohm':voc/isc,'VL_theory_V':vth*RL/(rth+RL),'VL_original_sim_V':vl,'VL_equivalent_sim_V':veq,'IL_theory_A':vth/(rth+RL),'IL_original_sim_A':vl/RL,'IL_equivalent_sim_A':veq/RL}
    (OUT/'thevenin.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    assert abs(voc-vth)<1e-6 and abs(isc-VS/R1)<1e-8 and abs(vl-veq)<1e-6
if __name__=='__main__':main()
