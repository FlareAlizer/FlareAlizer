"""Карточки проектов. У каждой своё небесное тело и своё движение."""
import math
import random

import header
from header import BG, CREAM, INK, MUTED, SAND
from typeset import num

W, H, GAP = 412, 160, 4          # вокруг карточки прозрачное поле, оно даёт зазор между соседями
SPOT = (346, 72)                 # где в карточке живёт объект
COLUMN = 262                     # ширина текстовой колонки
BODY = "#b5b1bd"
COOL = "#cdd5f0"

STYLE = """
@keyframes flow{to{stroke-dashoffset:100}}
@keyframes turn{to{transform:rotate(360deg)}}
@keyframes blink{50%{opacity:.15}}
@keyframes wave{from{transform:scale(.1);opacity:.6}to{transform:scale(1);opacity:0}}
@keyframes sway{50%{transform:rotate(4deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def wrap(face, text, size, limit):
    """Разбивает текст на строки не шире limit пикселей."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and face.width(candidate, size) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    return lines + [current]


def pulsar(rng):
    """Лучи метут небо, от звезды расходятся импульсы."""
    x, y = SPOT
    waves = "".join(
        f'<circle r="50" vector-effect="non-scaling-stroke" style="animation:wave 4.5s -{delay}s linear infinite"/>'
        for delay in (0, 1.5, 3)
    )
    return f"""
<g transform="translate({x} {y}) rotate(-22) scale(1 .42)">
  <g fill="none" stroke="{COOL}" stroke-width=".9">{waves}</g>
  <g style="animation:turn 7s linear infinite"><path d="M0 0L58 -6 58 6ZM0 0L-58 -6 -58 6Z" fill="url(#ray)"/></g>
</g>
<circle cx="{x}" cy="{y}" r="11" fill="url(#glowCool)"/>
<circle cx="{x}" cy="{y}" r="2.1" fill="#f2f4ff"/>"""


def binary(rng):
    """Две чёрные дыры кружат вокруг общего центра и закручивают за собой пространство."""
    x, y = SPOT
    wake = "".join(
        f'<path d="{header.spiral(0.85, 15, 0.21, phase)}" stroke="{SAND}" stroke-width="{w}" stroke-opacity="{o}"/>'
        for phase in (0, math.pi)
        for w, o in ((6, 0.05), (2.4, 0.13), (0.9, 0.34))
    )
    holes = "".join(
        f'<circle cx="{cx}" r="{r + 7}" fill="url(#glowWarm)"/>'
        f'<circle cx="{cx}" r="{r}" fill="#000" stroke="{CREAM}" stroke-width="1.1"/>'
        for cx, r in ((-14, 7), (15, 5.2))
    )
    return f"""
<g transform="translate({x} {y})">
  <g style="animation:turn 16s linear infinite">
    <g transform="scale(1 -1)" fill="none" stroke-linecap="round">{wake}</g>
    {holes}
  </g>
</g>"""


def galaxy(rng):
    """Спиральная галактика, вид под углом. Поворачивается целиком."""
    x, y = SPOT
    return f'<g transform="translate({x - 6} {y}) scale(1.55)">{header.galaxy(0, 0, seconds=150)}</g>'


def orbits(rng):
    """Звезда и три планеты, у каждой своя орбита и свой год."""
    x, y = SPOT
    squash = 0.38
    paths = "".join(
        f'<circle r="{r}" vector-effect="non-scaling-stroke"/>' for r in (19, 33, 49)
    )
    planets = ""
    for r, year, size, colour in ((19, 9, 1.7, CREAM), (33, 21, 2.3, SAND), (49, 44, 1.9, COOL)):
        delay = num(rng.uniform(0, year), 1)
        # встречное вращение держит планету круглой, хотя орбита сплющена
        planets += (
            f'<g style="animation:turn {year}s -{delay}s linear infinite"><g transform="translate({r} 0)">'
            f'<g style="animation:turn {year}s -{delay}s linear infinite reverse">'
            f'<ellipse rx="{size}" ry="{num(size / squash)}" fill="{colour}"/></g></g></g>'
        )
    return f"""
<g transform="translate({x} {y}) rotate(-16) scale(1 {squash})">
  <g fill="none" stroke="{INK}" stroke-opacity=".17" stroke-width=".8">{paths}</g>
  {planets}
</g>
<circle cx="{x}" cy="{y}" r="15" fill="url(#glowWarm)"/>
<circle cx="{x}" cy="{y}" r="3" fill="{CREAM}"/>"""


def constellation(rng):
    """Созвездие-дерево: звёзды соединены, как родня в древе."""
    x, y = SPOT
    points = [(2, -44), (-17, -21), (20, -18), (-33, 5), (-7, 6), (33, 9), (2, 36), (43, -37), (-44, 31)]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (4, 6), (2, 7), (3, 8)]
    lines = "".join(
        f'<path d="M{points[a][0]} {points[a][1]}L{points[b][0]} {points[b][1]}"/>' for a, b in edges
    )
    stars = ""
    for i, (px, py) in enumerate(points):
        r = (2.3, 1.7, 1.9, 1.4, 1.6, 1.5, 1.8, 1.2, 1.2)[i]
        tint = (CREAM, INK, COOL)[i % 3]
        blink = f"animation:blink {num(rng.uniform(3.5, 8), 1)}s -{num(rng.uniform(0, 8), 1)}s ease-in-out infinite"
        stars += (
            f'<circle cx="{px}" cy="{py}" r="{num(r * 3.4)}" fill="url(#glowCool)" opacity=".7"/>'
            f'<circle cx="{px}" cy="{py}" r="{r}" fill="{tint}" style="{blink}"/>'
        )
    return f"""
<g transform="translate({x} {y})">
  <g style="animation:sway 46s ease-in-out infinite">
    <g fill="none" stroke="{INK}" stroke-opacity=".24" stroke-width=".7">{lines}</g>
    {stars}
  </g>
</g>"""


def black_hole(rng):
    """Та же чёрная дыра, что в шапке, только маленькая."""
    x, y = SPOT
    k = 0.28
    cx, cy = header.BH
    hole = header.black_hole(rng, disk_lanes=18, ring_lanes=11)
    return f'<g transform="translate({num(x - k * cx)} {num(y - k * cy)}) scale({k})">{hole}</g>'


def comet(rng):
    """Комета идёт по дуге, за ней тянется хвост; вокруг вспыхивают искры."""
    x, y = SPOT
    tail = "".join(
        f'<path d="M0 0Q-34 14 -70 34" stroke="{c}" stroke-width="{w}" stroke-opacity="{o}" stroke-linecap="round"/>'
        for c, w, o in ((SAND, 9, 0.05), (SAND, 4, 0.12), (CREAM, 1.2, 0.45))
    )
    sparks = "".join(
        f'<circle cx="{num(rng.uniform(-46, 40))}" cy="{num(rng.uniform(-40, 40))}" r="{num(rng.uniform(0.8, 1.6))}" fill="{CREAM}"'
        f' style="animation:blink {num(rng.uniform(2.5, 6), 1)}s -{num(rng.uniform(0, 6), 1)}s ease-in-out infinite"/>'
        for _ in range(9)
    )
    return f"""
<g transform="translate({x} {y})">
  {sparks}
  <g style="animation:sway 9s ease-in-out infinite">
    <g fill="none">{tail}</g>
    <circle r="12" fill="url(#glowWarm)"/>
    <circle r="2.6" fill="#fff6ea"/>
  </g>
</g>"""


def defs(tint):
    x, y = SPOT
    return f"""
<clipPath id="card"><rect x="{GAP}" y="{GAP}" width="{W - 2 * GAP}" height="{H - 2 * GAP}" rx="14"/></clipPath>
<radialGradient id="tint" gradientUnits="userSpaceOnUse" cx="{x}" cy="{y}" r="150">
  <stop offset="0" stop-color="{tint}" stop-opacity=".2"/>
  <stop offset="1" stop-color="{tint}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="veil" x1="0" x2="1" y1="0" y2="0">
  <stop offset="0" stop-color="{BG}" stop-opacity=".7"/>
  <stop offset=".5" stop-color="{BG}" stop-opacity=".55"/>
  <stop offset=".74" stop-color="{BG}" stop-opacity="0"/>
</linearGradient>
<radialGradient id="glowCool">
  <stop offset="0" stop-color="{COOL}" stop-opacity=".5"/>
  <stop offset="1" stop-color="{COOL}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glowWarm">
  <stop offset="0" stop-color="{SAND}" stop-opacity=".5"/>
  <stop offset="1" stop-color="{SAND}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="ray" gradientUnits="userSpaceOnUse" x1="-58" x2="58" y1="0" y2="0">
  <stop offset="0" stop-color="{COOL}" stop-opacity="0"/>
  <stop offset=".5" stop-color="#eef1ff" stop-opacity=".7"/>
  <stop offset="1" stop-color="{COOL}" stop-opacity="0"/>
</linearGradient>"""


def build(head, text, title, about, note, body, tint, seed, accent=False):
    """Одна карточка: title — заголовок, about — описание, note — нижняя строка, body — функция объекта."""
    rng = random.Random(seed)
    head.fresh()
    text.fresh()
    stars = "".join(
        header.star(rng, rng.uniform(GAP, W - GAP), rng.uniform(GAP, H - GAP), (0.3, 1.0), (0.25, 0.8), blink=0.12)
        for _ in range(46)
    )
    extra = header.hole_defs() if body is black_hole else header.sky_defs() if body is galaxy else ""
    scene = body(rng)
    lines = wrap(text, about, 14.3, COLUMN)
    copy = head.line(title, 26, 40, 20, INK, tracking=-0.02)
    for i, line in enumerate(lines):
        copy += text.line(line, 26, 66 + i * 20, 14.3, BODY)
    copy += text.line(note, 26, H - GAP - 19, 12.8, SAND if accent else MUTED)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="name">
<title id="name">{title}. {about}</title>
<style>{STYLE}</style>
<defs>{defs(tint)}{extra}{head.defs()}{text.defs()}</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#tint)"/>
{stars}
{scene}
<rect width="{W}" height="{H}" fill="url(#veil)"/>
{copy}
</g>
<rect x="{GAP + .5}" y="{GAP + .5}" width="{W - 2 * GAP - 1}" height="{H - 2 * GAP - 1}" rx="13.5" fill="none" stroke="{INK}" stroke-opacity=".1"/>
</svg>
"""
