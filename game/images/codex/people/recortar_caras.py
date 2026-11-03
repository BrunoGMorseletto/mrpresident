"""Recorta la cara de un sprite (fondo magenta) para el códice.
Uso: python recortar_caras.py "Nikita Khrushchev BASE.png" PER-KHRUSHCHEV.png
Saca un cuadrado centrado en la cabeza (tamaño según el ancho de la cabeza), lo lleva a 600x600
y convierte el magenta (y el borde rosado que deja) en transparente."""
import sys
import numpy as np
from PIL import Image, ImageFilter

def recortar(src, dst, OUT=600):
    a = np.array(Image.open(src).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mag = ((r - g) > 70) & ((b - g) > 70)                 # fondo y halo magenta
    fg = ~mag
    rows = np.where(fg.sum(1) > 5)[0]; y0 = rows[0]        # parte de arriba de la cabeza
    xs = np.where(fg[y0:y0 + 320].sum(0) > 5)[0]           # ancho de la cabeza
    cx = (xs[0] + xs[-1]) // 2; hw = xs[-1] - xs[0]
    S = int(min(max(hw * 1.45, 600), min(a.shape[:2])))
    x1 = max(0, min(a.shape[1] - S, cx - S // 2)); y1 = max(0, y0 - int(S * 0.08))
    alpha = Image.fromarray(np.where(mag, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
    im = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); im.putalpha(alpha)
    im.crop((x1, y1, x1 + S, y1 + S)).resize((OUT, OUT), Image.LANCZOS).save(dst)

if __name__ == '__main__':
    recortar(sys.argv[1], sys.argv[2])
