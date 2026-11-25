"""Текст в кривых.

GitHub показывает картинки из README через <img>, веб-шрифты там не грузятся.
Поэтому надписи набираются здесь: HarfBuzz расставляет глифы с кернингом,
fontTools отдаёт контуры, в SVG попадают <path> и <use>.
"""
from io import BytesIO

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def num(value, digits=2):
    """Число для SVG: без хвостовых нулей и без «-0»."""
    text = f"{value:.{digits}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


class Face:
    """Одно начертание вариативного шрифта."""

    def __init__(self, path, weight, prefix):
        font = instantiateVariableFont(TTFont(path), {"wght": weight})
        data = BytesIO()
        font.save(data)
        self.prefix = prefix
        self.upm = font["head"].unitsPerEm
        self.order = font.getGlyphOrder()
        self.outlines = font.getGlyphSet()
        self.shaper = hb.Font(hb.Face(data.getvalue()))
        self.used = {}
        self.paths = {}

    def fresh(self):
        """Начать новый файл: набор использованных глифов у каждого SVG свой."""
        self.used = {}

    def shape(self, text):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.shaper, buffer)
        return [
            (self.order[info.codepoint], pos.x_advance)
            for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions)
        ]

    def width(self, text, size, tracking=0.0):
        """Ширина строки в пикселях; tracking задаётся в долях кегля."""
        glyphs = self.shape(text)
        units = sum(advance for _, advance in glyphs) + tracking * self.upm * max(len(glyphs) - 1, 0)
        return units * size / self.upm

    def line(self, text, x, y, size, fill, tracking=0.0, anchor="start", opacity=None):
        """Строка с базовой линией в (x, y). Возвращает <g> со ссылками на глифы."""
        if anchor == "end":
            x -= self.width(text, size, tracking)
        elif anchor == "middle":
            x -= self.width(text, size, tracking) / 2
        scale = size / self.upm
        pen_x = 0.0
        uses = []
        for name, advance in self.shape(text):
            if self.contour(name):
                ref = self.used.setdefault(name, f"{self.prefix}{len(self.used)}")
                uses.append(f'<use href="#{ref}" x="{num(pen_x, 0)}"/>')
            pen_x += advance + tracking * self.upm
        alpha = f' fill-opacity="{num(opacity)}"' if opacity is not None else ""
        return (
            f'<g transform="translate({num(x)} {num(y)}) scale({num(scale, 4)} {num(-scale, 4)})" '
            f'fill="{fill}"{alpha}>{"".join(uses)}</g>'
        )

    def contour(self, name):
        """Контур глифа в единицах шрифта. У пробела он пустой."""
        if name not in self.paths:
            pen = SVGPathPen(self.outlines, ntos=lambda v: num(v, 0))
            self.outlines[name].draw(pen)
            self.paths[name] = pen.getCommands()
        return self.paths[name]

    def defs(self):
        """Контуры всех глифов, которые понадобились строкам."""
        return "".join(f'<path id="{ref}" d="{self.contour(name)}"/>' for name, ref in self.used.items())
