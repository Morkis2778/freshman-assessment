"""Edit ../profile.json, then python docs/make_profile.py. Requires reportlab."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1]
info=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('NotoSansSC', str(ROOT/'assets/fonts/NotoSansSC-Regular.ttf')))
c=canvas.Canvas(str(ROOT/'profile.pdf'),pagesize=(595.28,841.89))
c.setTitle('个人简介 - '+info['name'])
c.setFillColor(HexColor('#f4f1eb'));c.rect(0,0,595.28,841.89,fill=1,stroke=0)
c.setFillColor(HexColor('#235d48'));c.rect(0,620,595.28,222,fill=1,stroke=0)
c.setFillColor(HexColor('#ffffff'));c.setFont('Helvetica',12);c.drawString(52,782,'FRESHMAN / PERSONAL PROFILE')
c.setFont('NotoSansSC',32);c.drawString(52,713,info['name']);c.setFont('NotoSansSC',14);c.drawString(52,669,info['major']+' / '+info['grade'])
y=578
for title,text in [('关于我',info['intro']),('兴趣方向',info['interests']),('学习目标',info['goals']),('联系方式',info['email'])]:
 c.setFillColor(HexColor('#235d48'));c.setFont('NotoSansSC',17);c.drawString(52,y,title);y-=29
 c.setFillColor(HexColor('#172d37'));c.setFont('NotoSansSC',12)
 lines=[];line=''
 for ch in text:
  if pdfmetrics.stringWidth(line+ch,'NotoSansSC',12)>485:lines.append(line);line=ch
  else:line+=ch
 lines.append(line)
 for line in lines:c.drawString(52,y,line);y-=21
 y-=25
 if y<120:raise ValueError('个人内容过长，请精简后重新生成，避免超出一页。')
c.setFillColor(HexColor('#607169'));c.setFont('NotoSansSC',10);c.drawString(52,66,'提交前请填写真实信息，并同步修改个人主页。')
c.setFont('Helvetica',9);c.drawRightString(543,66,'01 / PROFILE');c.showPage();c.save()
print(ROOT/'profile.pdf')
