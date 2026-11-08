#!/usr/bin/env python3
"""Monta un vídeo vertical 1080x1920 a partir de capturas del juego.

Uso: python3 montar.py pieza.json salida.mp4
La pieza: {"escenas": [{"img": ruta, "recorte": [x0,y0,x1,y1] | null, "titulo": "...", "sub": "...", "dur": s}],
           "cierre": {"titulo": "...", "sub": "...", "dur": s}, "audio": {"fondo": ruta, "efectos": [[ruta, segundo], ...]}}
"""
import json, os, subprocess, sys, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
NOCHE = (11, 26, 51)
NOCHE2 = (20, 33, 58)
CREMA = (255, 245, 220)
AMARILLO = (242, 194, 48)
AQUI = os.path.dirname(os.path.abspath(__file__))
F_DISPLAY = os.path.join(AQUI, 'fonts', 'bebas-neue-latin-400-normal.ttf')
F_BODY = os.path.join(AQUI, 'fonts', 'source-sans-3-latin-600-normal.ttf')
F_BOLD = os.path.join(AQUI, 'fonts', 'source-sans-3-latin-700-normal.ttf')
FPS = 30


def fuente(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def texto_centrado(d, y, texto, f, color, ancho_max):
    # Parte en líneas que quepan
    palabras, lineas, actual = texto.split(), [], ''
    for p in palabras:
        prueba = (actual + ' ' + p).strip()
        if d.textlength(prueba, font=f) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual); actual = p
    if actual:
        lineas.append(actual)
    alto = f.size * 1.02
    for ln in lineas:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=color)
        y += alto
    return y


def fondo():
    im = Image.new('RGB', (W, H), NOCHE)
    d = ImageDraw.Draw(im)
    # franja sutil arriba, como la cabecera del juego
    d.rectangle([0, 0, W, 12], fill=AMARILLO)
    return im


def marca(d, y=70):
    f = fuente(F_DISPLAY, 46)
    t = 'MANDAMÁS FC'
    w = d.textlength(t, font=f)
    d.text(((W - w) / 2, y), t, font=f, fill=CREMA)


def escena(e):
    im = fondo()
    d = ImageDraw.Draw(im)
    marca(d)
    y = 150
    y = texto_centrado(d, y, e['titulo'].upper(), fuente(F_DISPLAY, 112), AMARILLO, 960)
    if e.get('sub'):
        y = texto_centrado(d, y + 10, e['sub'], fuente(F_BODY, 46), CREMA, 940)
    top = max(int(y) + 40, 430)
    cap = Image.open(e['img']).convert('RGB')
    if e.get('recorte'):
        cap = cap.crop(tuple(e['recorte']))
    max_w, max_h = 900, 1500 - top
    esc = min(max_w / cap.width, max_h / cap.height)
    cap = cap.resize((int(cap.width * esc), int(cap.height * esc)), Image.LANCZOS)
    x = (W - cap.width) // 2
    # sombra y borde amarillo, esquinas redondeadas
    sombra = Image.new('L', (cap.width + 40, cap.height + 40), 0)
    ImageDraw.Draw(sombra).rounded_rectangle([20, 20, cap.width + 20, cap.height + 20], 40, fill=150)
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    im.paste((0, 0, 0), (x - 20, top - 8), sombra)
    mask = Image.new('L', cap.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cap.width - 1, cap.height - 1], 34, fill=255)
    d.rounded_rectangle([x - 7, top - 7, x + cap.width + 6, top + cap.height + 6], 40, fill=AMARILLO)
    im.paste(cap, (x, top), mask)
    return im


def cierre(c):
    im = fondo()
    d = ImageDraw.Draw(im)
    y = 520
    y = texto_centrado(d, y, 'MANDAMÁS FC', fuente(F_DISPLAY, 170), AMARILLO, 1000)
    y = texto_centrado(d, y + 20, c.get('titulo', 'Eres el presidente. Que no te echen.'), fuente(F_BODY, 56), CREMA, 900)
    # botón
    f = fuente(F_DISPLAY, 70)
    t = c.get('boton', 'JUEGA GRATIS EN MANDAMASFC.COM')
    tw = d.textlength(t, font=f)
    bx0, by0 = (W - tw) / 2 - 50, y + 90
    d.rounded_rectangle([bx0, by0, bx0 + tw + 100, by0 + 120], 18, fill=AMARILLO)
    d.text((bx0 + 50, by0 + 22), t, font=f, fill=NOCHE)
    if c.get('sub'):
        texto_centrado(d, by0 + 170, c['sub'], fuente(F_BODY, 40), CREMA, 900)
    return im


def main(pieza_json, salida):
    p = json.load(open(pieza_json))
    tmp = tempfile.mkdtemp()
    imgs, durs = [], []
    for i, e in enumerate(p['escenas']):
        ruta = os.path.join(tmp, f'e{i}.png'); escena(e).save(ruta); imgs.append(ruta); durs.append(e.get('dur', 3))
    ruta = os.path.join(tmp, 'cierre.png'); cierre(p.get('cierre', {})).save(ruta); imgs.append(ruta); durs.append(p.get('cierre', {}).get('dur', 2.5))
    xf = 0.35
    # vídeo: cada imagen con un zoom suave, unidas con fundido
    args = ['ffmpeg', '-y', '-loglevel', 'error']
    for r, du in zip(imgs, durs):
        args += ['-framerate', str(FPS), '-loop', '1', '-t', str(du), '-i', r]
    filt, prev = [], None
    for i, du in enumerate(durs):
        n = int(du * FPS)
        filt.append(f'[{i}:v]scale={W*2}:{H*2},zoompan=z=\'1+0.025*in/{n}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih*0.55-(ih/zoom*0.55)\':d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[v{i}]')
    t = durs[0]
    prev = 'v0'
    for i in range(1, len(durs)):
        out = f'x{i}'
        filt.append(f'[{prev}][v{i}]xfade=transition=fade:duration={xf}:offset={t - xf:.3f}[{out}]')
        t = t - xf + durs[i]
        prev = out
    total = t
    # audio
    a = p.get('audio', {})
    na = len(imgs)
    ains, amix = [], []
    if a.get('fondo'):
        args += ['-stream_loop', '-1', '-i', a['fondo']]
        ains.append(f'[{na}:a]atrim=0:{total:.3f},volume=0.55,afade=t=out:st={total - 0.8:.3f}:d=0.8[a0]'); amix.append('[a0]'); na += 1
    for j, (ruta_e, seg) in enumerate(a.get('efectos', [])):
        args += ['-i', ruta_e]
        ains.append(f'[{na}:a]adelay={int(seg * 1000)}|{int(seg * 1000)},volume=0.9[e{j}]'); amix.append(f'[e{j}]'); na += 1
    if amix:
        ains.append(''.join(amix) + f'amix=inputs={len(amix)}:normalize=0,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]')
    fc = ';'.join(filt + ains)
    args += ['-filter_complex', fc, '-map', f'[{prev}]']
    if amix:
        args += ['-map', '[aout]', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
    args += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart', '-t', f'{total:.3f}', salida]
    subprocess.run(args, check=True)
    # portada (primera escena) para revisar
    Image.open(imgs[0]).save(salida.replace('.mp4', '.jpg'), quality=85)
    print(salida, f'{total:.1f}s', os.path.getsize(salida), 'bytes')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
