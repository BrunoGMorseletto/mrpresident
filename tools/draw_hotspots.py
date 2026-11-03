"""Dibuja el contorno pixelado del hotspot del códex para cada fondo.
Polígonos en píxeles del fondo (1672x941). Los tramos sobre el borde de la pantalla no se dibujan."""
from PIL import Image, ImageDraw
import sys, json
W,H,PX=1672,941,4                     # PX = tamaño del "pixel" del contorno
POLYS={
 "bg_despacho":     [(42,640),(62,630),(97,620),(152,620),(207,627),(266,630),(280,656),(160,676),(130,722),(46,722)],
 "bg_decisions":    [(0,780),(215,754),(468,848),(480,941)],
 "bg_crisis_normal":[(0,768),(130,764),(480,808),(500,941)],
}
CLOSED={"bg_despacho":True,"bg_decisions":False,"bg_crisis_normal":False}
out=sys.argv[1]
spots={}
for tag,pts in POLYS.items():
    w,h=W//PX+1,H//PX+1
    lo=[(x/PX,y/PX) for x,y in pts]
    if CLOSED[tag]: lo=lo+[lo[0]]
    shadow=Image.new("RGBA",(w,h)); ds=ImageDraw.Draw(shadow)
    ds.line([(x+1,y+1) for x,y in lo],fill=(90,0,0,255),width=2)
    red=Image.new("RGBA",(w,h)); dr=ImageDraw.Draw(red)
    dr.line(lo,fill=(235,20,20,255),width=2)
    for x,y in lo: dr.rectangle([x-0.5,y-0.5,x+1,y+1],fill=(235,20,20,255))
    im=Image.alpha_composite(shadow,red).resize((w*PX,h*PX),Image.NEAREST).crop((0,0,W,H))
    im.save(f"{out}/{tag}.png",optimize=True)
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    spots[tag]=(min(xs),min(ys),max(xs)-min(xs),(H if not CLOSED[tag] else max(ys))-min(ys))
print(json.dumps(spots))
