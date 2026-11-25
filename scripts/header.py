"""Шапка профиля: чёрная дыра с диском, звёзды в три слоя, далёкая галактика и пульсар."""
import math
import random

from typeset import num

W, H = 800, 360
BG = "#050507"
INK = "#dedbe3"
MUTED = "#8f8b99"
SAND = "#c6a17c"
CREAM = "#f6ecdd"
EMBER = "#6a4b37"

BH = (594, 182)   # центр чёрной дыры
PHOTON = 45       # фотонное кольцо
SHADOW = 51       # край тени
TILT = -7         # наклон диска, градусы
FLAT = 0.14       # сплющенность диска: мы смотрим почти с ребра


def mix(a, b, t):
    """Цвет между a и b, t от 0 до 1."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def heat(t):
    """Цвет вещества: у дыры почти белое, дальше песочное, по краю тлеет."""
    return mix(CREAM, SAND, t / 0.45) if t < 0.45 else mix(SAND, EMBER, (t - 0.45) / 0.55)


def orbit(cx, cy, rx, ry):
    """Замкнутая орбита одним путём. Идёт по часовой стрелке, начиная справа."""
    return (
        f"M{num(cx + rx)} {num(cy)}A{num(rx)} {num(ry)} 0 1 1 {num(cx - rx)} {num(cy)}"
        f"A{num(rx)} {num(ry)} 0 1 1 {num(cx + rx)} {num(cy)}Z"
    )


def dashes(rng, pieces):
    """Сгустки и просветы вдоль орбиты. Длина пути принята за 100."""
    raw = []
    for _ in range(pieces):
        raw += [rng.uniform(5, 24), rng.uniform(1.5, 8)]
    k = 100 / sum(raw)
    return " ".join(num(v * k, 1) for v in raw)


def stream(rng, d, colour, width, opacity, period):
    """Одна струя вещества: штрихи едут по орбите за period секунд."""
    delay = rng.uniform(0, period)
    return (
        f'<path d="{d}" pathLength="100" stroke="{colour}" stroke-width="{num(width)}" '
        f'stroke-opacity="{num(opacity)}" stroke-dasharray="{dashes(rng, rng.choice((3, 4, 5)))}" '
        f'style="animation:flow {num(period, 0)}s -{num(delay, 0)}s linear infinite"/>'
    )


def disk(rng, count):
    """Аккреционный диск. Внутренние орбиты быстрее внешних, как у Кеплера."""
    cx, cy = BH
    lanes = []
    radii = [58 + 176 * (i / (count - 1)) ** 1.15 for i in range(count)]
    for rx in radii:
        t = (rx - 58) / 176
        opacity = (0.74 - 0.64 * t) * rng.uniform(0.6, 1)
        width = 1.25 - 0.45 * t
        period = 46 * (rx / 58) ** 1.5 * rng.uniform(0.92, 1.08)
        lanes.append(stream(rng, orbit(cx, cy, rx, rx * FLAT), heat(t), width, opacity, period))
    return "".join(lanes)


def lensed_ring(rng, count):
    """Дальняя сторона диска, которую гравитация выгнула дугой над тенью."""
    cx, cy = BH
    lanes = []
    for i in range(count):
        t = i / (count - 1)
        r = SHADOW + 1.5 + 36.8 * t
        opacity = (0.74 - 0.52 * t) * rng.uniform(0.6, 1)
        period = 40 * (r / SHADOW) ** 1.5 * rng.uniform(0.92, 1.08)
        lanes.append(stream(rng, orbit(cx, cy, r, r), heat(t * 0.9), 1.5 - 0.4 * t, opacity, period))
    return "".join(lanes)


def black_hole(rng, disk_lanes=42, ring_lanes=24):
    cx, cy = BH
    lanes = disk(rng, disk_lanes)
    return f"""
<circle cx="{cx}" cy="{cy}" r="160" fill="url(#halo)"/>
<g transform="rotate({TILT} {cx} {cy})" fill="none" stroke-linecap="round">
  <g clip-path="url(#far)" mask="url(#doppler)">
    <ellipse cx="{cx}" cy="{cy}" rx="240" ry="33" fill="url(#diskGlow)"/>
    <g filter="url(#streak)">{lanes}</g>
  </g>
</g>
<circle cx="{cx}" cy="{cy}" r="104" fill="url(#ringGlow)" mask="url(#arc)"/>
<g fill="none" stroke-linecap="round" mask="url(#arc)" filter="url(#soft)">{lensed_ring(rng, ring_lanes)}</g>
<circle cx="{cx}" cy="{cy}" r="{SHADOW + 4}" fill="url(#shadow)"/>
<path d="{orbit(cx, cy, PHOTON, PHOTON)}" pathLength="100" fill="none" stroke="{CREAM}" stroke-width=".9"
  stroke-opacity=".85" stroke-dasharray=".42 .38" style="animation:flow 240s linear infinite"/>
<g transform="rotate({TILT} {cx} {cy})" fill="none" stroke-linecap="round">
  <g clip-path="url(#near)" mask="url(#doppler)">
    <ellipse cx="{cx}" cy="{cy}" rx="240" ry="33" fill="url(#diskGlow)"/>
    <g filter="url(#streak)">{lanes}
    <path d="{orbit(cx, cy, 57, 57 * FLAT)}" stroke="{CREAM}" stroke-width="1.8" stroke-opacity=".9"/></g>
  </g>
</g>"""


def star(rng, x, y, radius, alpha, blink=0.07):
    lo, hi = radius
    r = lo + (hi - lo) * rng.random() ** 2.2
    tint = rng.choices((INK, "#f0dcc4", "#cdd5f0"), weights=(6, 2, 2))[0]
    twinkle = ""
    if rng.random() < blink:
        twinkle = f' style="animation:blink {num(rng.uniform(3, 7), 1)}s -{num(rng.uniform(0, 7), 1)}s ease-in-out infinite"'
    return f'<circle cx="{num(x, 1)}" cy="{num(y, 1)}" r="{num(r)}" fill="{tint}" opacity="{num(rng.uniform(*alpha))}"{twinkle}/>'


def star_layer(rng, name, count, radius, alpha, seconds):
    """Слой звёзд шириной 800. Копия справа закрывает шов, пока слой едет влево."""
    dots = [star(rng, rng.uniform(0, W), rng.uniform(0, H), radius, alpha) for _ in range(count)]
    return (
        f'<g class="stars" style="animation:drift {seconds}s linear infinite">'
        f'<g id="{name}">{"".join(dots)}</g><use href="#{name}" x="{W}"/></g>'
    )


def spiral(turns, a, b, phase, steps=44):
    """Рукав галактики: логарифмическая спираль."""
    points = []
    for i in range(steps + 1):
        theta = turns * 2 * math.pi * i / steps
        r = a * math.exp(b * theta)
        points.append(f"{num(r * math.cos(theta + phase), 1)} {num(r * math.sin(theta + phase), 1)}")
    return "M" + "L".join(points)


def galaxy(x, y, seconds=420):
    arms = "".join(
        f'<path d="{spiral(1.05, 3.2, 0.36, phase)}" stroke="#cfd4ea" stroke-width="{w}" stroke-opacity="{o}"/>'
        for phase in (0, math.pi)
        for w, o in ((7, 0.07), (3.2, 0.16), (1.2, 0.34))
    )
    return f"""
<g transform="translate({x} {y}) rotate(-26) scale(1 .44)">
  <circle r="40" fill="url(#galaxy)"/>
  <g fill="none" stroke-linecap="round" style="animation:turn {seconds}s linear infinite">{arms}</g>
  <circle r="3.2" fill="{CREAM}" opacity=".9"/>
</g>"""


def pulsar(x, y):
    """Нейтронная звезда: два луча вращаются, сама звезда мигает в такт."""
    return f"""
<g transform="translate({x} {y}) rotate(18) scale(1 .5)">
  <g style="animation:turn 5s linear infinite">
    <path d="M0 0L19 -1.5 19 1.5ZM0 0L-19 -1.5 -19 1.5Z" fill="url(#beam)"/>
  </g>
</g>
<circle cx="{x}" cy="{y}" r="5" fill="#cdd5f0" opacity=".12" style="animation:pulse 2.5s ease-in-out infinite"/>
<circle cx="{x}" cy="{y}" r="1.3" fill="#eef1ff"/>"""


STYLE = """
@keyframes flow{to{stroke-dashoffset:100}}
@keyframes drift{to{transform:translateX(-800px)}}
@keyframes turn{to{transform:rotate(360deg)}}
@keyframes blink{50%{opacity:.15}}
@keyframes pulse{50%{opacity:.45;r:7px}}
.narrow{display:none}
@media (max-width:520px){
  .wide{display:none}.narrow{display:inline}
  .hole{transform:translate(34px,4px)}
  .stars{stroke:#dedbe3;stroke-width:.9px;stroke-opacity:.55}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def hole_defs():
    """Градиенты, маски и фильтры чёрной дыры."""
    cx, cy = BH
    inner = SHADOW / 104
    return f"""
<clipPath id="far"><rect x="{cx - 300}" y="{cy - 80}" width="600" height="80"/></clipPath>
<clipPath id="near"><rect x="{cx - 300}" y="{cy}" width="600" height="80"/></clipPath>
<radialGradient id="halo">
  <stop offset=".3" stop-color="{SAND}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{SAND}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="ringGlow">
  <stop offset="{num(inner - .03)}" stop-color="{CREAM}" stop-opacity="0"/>
  <stop offset="{num(inner + .04)}" stop-color="{CREAM}" stop-opacity=".62"/>
  <stop offset="{num(inner + .22)}" stop-color="{SAND}" stop-opacity=".3"/>
  <stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="diskGlow">
  <stop offset=".22" stop-color="{CREAM}" stop-opacity="0"/>
  <stop offset=".3" stop-color="{CREAM}" stop-opacity=".55"/>
  <stop offset=".55" stop-color="{SAND}" stop-opacity=".2"/>
  <stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="shadow">
  <stop offset=".88" stop-color="#000"/>
  <stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>
<filter id="soft" filterUnits="userSpaceOnUse" x="{cx - 100}" y="{cy - 100}" width="200" height="200">
  <feGaussianBlur stdDeviation=".9"/>
</filter>
<filter id="streak" filterUnits="userSpaceOnUse" x="{cx - 250}" y="{cy - 60}" width="500" height="120">
  <feGaussianBlur stdDeviation="2.2 .4"/>
</filter>
<linearGradient id="dopplerRamp" gradientUnits="userSpaceOnUse" x1="{cx - 220}" x2="{cx + 220}" y1="0" y2="0">
  <stop offset="0" stop-color="#fff"/>
  <stop offset="1" stop-color="#fff" stop-opacity=".5"/>
</linearGradient>
<mask id="doppler" maskUnits="userSpaceOnUse" x="{cx - 300}" y="{cy - 80}" width="600" height="160">
  <rect x="{cx - 300}" y="{cy - 80}" width="600" height="160" fill="url(#dopplerRamp)"/>
</mask>
<radialGradient id="arcRamp" gradientUnits="userSpaceOnUse" cx="{cx + 3}" cy="{cy - 11}" r="90">
  <stop offset=".72" stop-color="#fff"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<mask id="arc" maskUnits="userSpaceOnUse" x="{cx - 110}" y="{cy - 110}" width="220" height="220">
  <rect x="{cx - 110}" y="{cy - 110}" width="220" height="220" fill="url(#arcRamp)"/>
</mask>"""


def sky_defs():
    """Галактика и луч пульсара."""
    return f"""
<radialGradient id="galaxy">
  <stop offset="0" stop-color="{CREAM}" stop-opacity=".75"/>
  <stop offset=".16" stop-color="#d9cfe0" stop-opacity=".3"/>
  <stop offset=".55" stop-color="#8f93c4" stop-opacity=".09"/>
  <stop offset="1" stop-color="#8f93c4" stop-opacity="0"/>
</radialGradient>
<linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="-19" x2="19" y1="0" y2="0">
  <stop offset="0" stop-color="#cdd5f0" stop-opacity="0"/>
  <stop offset=".5" stop-color="#eef1ff" stop-opacity=".8"/>
  <stop offset="1" stop-color="#cdd5f0" stop-opacity="0"/>
</linearGradient>"""


def frame_defs():
    return f"""
<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<radialGradient id="violet" gradientUnits="userSpaceOnUse" cx="146" cy="346" r="420">
  <stop offset="0" stop-color="#5a508c" stop-opacity=".26"/>
  <stop offset="1" stop-color="#5a508c" stop-opacity="0"/>
</radialGradient>
<linearGradient id="scrim" x1="0" x2="1" y1="0" y2="0">
  <stop offset="0" stop-color="{BG}" stop-opacity=".72"/>
  <stop offset=".3" stop-color="{BG}" stop-opacity=".5"/>
  <stop offset=".56" stop-color="{BG}" stop-opacity="0"/>
</linearGradient>"""


def build(head, text):
    """head — начертание для имени, text — для подписи."""
    rng = random.Random(1835)
    head.fresh()
    text.fresh()
    sky = (
        star_layer(rng, "s1", 170, (0.3, 0.75), (0.25, 0.7), 520)
        + star_layer(rng, "s2", 70, (0.5, 1.05), (0.45, 0.9), 360)
        + star_layer(rng, "s3", 20, (0.9, 1.5), (0.75, 1), 250)
    )
    hole = black_hole(rng)
    wide = (
        text.line("Backend engineer, Moscow", 44, 117, 16.5, MUTED)
        + head.line("Владислав", 42, 185, 64, INK, tracking=-0.04)
        + head.line("Фокин", 42, 248, 64, INK, tracking=-0.04)
    )
    narrow = (
        text.line("Backend engineer, Moscow", 36, 104, 29, "#a09cab")
        + head.line("Владислав", 34, 188, 76, INK, tracking=-0.04)
        + head.line("Фокин", 34, 262, 76, INK, tracking=-0.04)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="name">
<title id="name">Владислав Фокин, backend engineer, Moscow</title>
<style>{STYLE}</style>
<defs>{frame_defs()}{hole_defs()}{sky_defs()}{head.defs()}{text.defs()}</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#violet)"/>
{sky}
{galaxy(738, 60)}
{pulsar(448, 314)}
<g class="hole">{hole}</g>
<rect width="{W}" height="{H}" fill="url(#scrim)"/>
<g class="wide">{wide}</g>
<g class="narrow">{narrow}</g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="{INK}" stroke-opacity=".09"/>
</svg>
"""
