"""Editable, vector-native schematic drawings. Requires matplotlib and numpy."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon
OUT=Path(__file__).resolve().parents[1]/'assets'
COLOR='#183648'
def start(title,xmax=11,ymax=8):
 global ax,fig
 fig,ax=plt.subplots(figsize=(10,6));ax.set(xlim=(-.5,xmax),ylim=(-.7,ymax));ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=17,pad=15)
def wire(*points):ax.plot(*zip(*points),color=COLOR,lw=2)
def label(x,y,text,ha='left'):ax.text(x,y,text,fontsize=11,ha=ha,va='center',color=COLOR)
def dot(x,y):ax.add_patch(Circle((x,y),.065,color=COLOR))
def ground(x,y):
 wire((x,y),(x,y-.18));
 for dy,w in [(.18,.35),(.31,.23),(.44,.1)]:wire((x-w,y-dy),(x+w,y-dy))
def rv(x,y1,y2,text,side=1):
 mid=(y1+y2)/2;wire((x,y1),(x,mid-.55));wire((x,mid+.55),(x,y2));ax.add_patch(Rectangle((x-.15,mid-.55),.3,1.1,fill=False,ec=COLOR,lw=2));label(x+side*.4,mid,text,'left' if side>0 else 'right')
def rh(x1,x2,y,text):
 mid=(x1+x2)/2;wire((x1,y),(mid-.55,y));wire((mid+.55,y),(x2,y));ax.add_patch(Rectangle((mid-.55,y-.15),1.1,.3,fill=False,ec=COLOR,lw=2));label(mid,y+.6,text,'center')
def cap(x1,x2,y,text):
 mid=(x1+x2)/2;wire((x1,y),(mid-.12,y));wire((mid+.12,y),(x2,y));wire((mid-.12,y-.4),(mid-.12,y+.4));wire((mid+.12,y-.4),(mid+.12,y+.4));label(mid,y+.65,text,'center')
def source(x,y1,y2,text,sine=False):
 mid=(y1+y2)/2;wire((x,y1),(x,mid-.5));wire((x,mid+.5),(x,y2));ax.add_patch(Circle((x,mid),.5,fill=False,ec=COLOR,lw=2));
 if sine:
  z=np.linspace(-.35,.35,60);ax.plot(x+z,mid+.2*np.sin(z/.35*np.pi),color=COLOR,lw=1.5)
 else:label(x,mid+.17,'+','center');label(x,mid-.2,'-','center')
 label(x-.7,mid,text,'right')
def fet(x,y):
 # D=(x,y+1), S=(x,y-1), G=(x-1.3,y); source and bulk tied.
 wire((x,y+1),(x,y+.6),(x-.5,y+.6));wire((x-.5,y-.6),(x,y-.6),(x,y-1));wire((x-.5,y-.6),(x-.5,y+.6));wire((x-.8,y-.6),(x-.8,y+.6));wire((x-1.3,y),(x-.8,y));wire((x-.5,y),(x+.55,y),(x+.55,y-1),(x,y-1));ax.annotate('',xy=(x-.5,y),xytext=(x-.13,y),arrowprops={'arrowstyle':'->','color':COLOR});label(x+.9,y,'M1\nNMOS');label(x+.2,y+.8,'D');label(x-1.2,y+.3,'G');label(x+.9,y-1.1,'S / B')
def save(name):
 fig.tight_layout();fig.savefig(OUT/(name+'.png'),dpi=170,bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig)
start('RC low-pass filter')
source(2,1,5,'Vin\n0-1 V square\n100 Hz');rh(2,7,5,'R = 1 kohm');dot(7,5);label(7.3,5.4,'Vout');wire((7,5),(7,3.2));wire((6.55,3.2),(7.45,3.2));wire((6.55,2.95),(7.45,2.95));wire((7,2.95),(7,1),(2,1));label(7.7,3.1,'C = 1 uF');ground(7,1);save('rc_circuit')
start('Two-terminal source network / A-B port',12)
source(2,1,5,'Vs = 12 V');rh(2,7,5,'R1 = 1 kohm');dot(7,5);label(7.2,5.5,'Port A');rv(7,1,5,'R2 = 2 kohm',-1);wire((7,1),(2,1));dot(7,1);ground(7,1);label(7.3,.8,'Port B');wire((7,5),(10,5));rv(10,1,5,'RL = 1 kohm');wire((10,1),(7,1));label(8.6,6.7,'Voc: remove RL\nIsc: replace RL with 0 V sensor','center');save('thevenin_circuit')
start('Thevenin equivalent / same load')
source(2,1,5,'Vth = 8 V');rh(2,7,5,'Rth = 666.667 ohm');dot(7,5);label(7.3,5.5,'Port A');rv(7,1,5,'RL = 1 kohm');wire((7,1),(2,1));ground(7,1);label(7.4,1,'Port B');save('thevenin_equivalent')
for dc in [False,True]:
 start('NMOS common-source / '+('DC path: Cb1 open' if dc else 'complete circuit'),12)
 fet(7,3);ground(7,2);wire((7,4),(7,4.7));dot(7,4.7);label(7.3,4.7,'Vout');rv(7,4.7,7,'RD = 2 kohm');dot(7,7);label(7.3,7.2,'VDD = 5 V');wire((7,7),(4.5,7));rv(4.5,3,7,'RG1 = 60 kohm',-1);dot(4.5,3);wire((4.5,3),(5.7,3));rv(4.5,0,3,'RG2 = 40 kohm');ground(4.5,0)
 if not dc:cap(1.5,4.5,3,'Cb1 = 100 uF');source(1.5,0,3,'Vi = 10 mV\n1 kHz',True);ground(1.5,0)
 else:wire((4.5,3),(3.5,3));ax.add_patch(Circle((3.5,3),.08,fill=False,ec=COLOR));label(.3,2.4,'Cb1 is open.\nInput disconnected.')
 save('mos_dc' if dc else 'mos_circuit')
start('NMOS small-signal model / AC ground',13)
source(1.5,1,5,'vi = vgs',True);wire((1.5,5),(4,5));dot(4,5);label(4,5.5,'gate','center');rv(4,1,5,'RG1 || RG2\n24 kohm');wire((4,1),(1.5,1));ground(4,1)
wire((7,1),(7,2.4));wire((7,3.6),(7,5));ax.add_patch(Polygon([[7,2.4],[7.5,3],[7,3.6],[6.5,3]],fill=False,ec=COLOR,lw=2));ax.annotate('',xy=(7,2.65),xytext=(7,3.35),arrowprops={'arrowstyle':'->','color':COLOR,'lw':1.5});label(6.4,2.1,'gm vgs','right');ground(7,1);dot(7,5);label(7,5.5,'vo / drain','center');wire((7,5),(12,5));rv(9.5,1,5,'ro =\n62.5 kohm',-1);rv(12,1,5,'RD =\n2 kohm',-1);ground(9.5,1);ground(12,1);label(6.6,6.8,'VDD -> AC ground; Cb1 -> short circuit','center');save('mos_small_signal')
