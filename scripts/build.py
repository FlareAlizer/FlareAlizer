"""Собирает картинки для README.

    python scripts/build.py путь/к/шрифтам

В папке со шрифтами должны лежать вариативные Montserrat[wght].ttf и Onest[wght].ttf
(оба под лицензией OFL, есть на Google Fonts). Нужны пакеты fonttools и uharfbuzz.
"""
import sys
from pathlib import Path

import cards
import header
from typeset import Face

ASSETS = Path(__file__).resolve().parent.parent / "assets"
VIOLET, WARM = "#5a508c", "#8a6a4c"

# файл, заголовок, описание, нижняя строка, объект, оттенок фона
CARDS = [
    ("nexu", "nexu",
     "Платформа онлайн-школы: уроки с видео, задания с проверкой, тесты, опыт и ранги.",
     "TypeScript, Express, Prisma, React", cards.black_hole, VIOLET),
    ("ai-marketer-bot", "ai-marketer-bot",
     "Telegram-бот для ведения канала: контент-план и тексты постов через LLM, публикация по расписанию.",
     "Python, aiogram, PostgreSQL, Redis", cards.pulsar, WARM),
    ("logistics-optimizer", "logistics-optimizer",
     "Собирает заказы в сборные рейсы: группирует по городам, датам и вместимости машин.",
     "Python, PyQt6", cards.orbits, VIOLET),
    ("esg-quant-scanner", "esg-quant-scanner",
     "Оценивает акции по пяти факторам, собирает портфель по Марковицу и гоняет его через Монте-Карло.",
     "Python, NumPy, pandas, SciPy, LLM", cards.galaxy, WARM),
    ("teboil-marathon", "teboil-marathon",
     "Стенд Teboil на беговом марафоне: квиз с рулеткой, баллы от волонтёров, таблица лидеров.",
     "TypeScript, Next.js, PostgreSQL", cards.binary, VIOLET),
    ("alfa-hod", "alfa-hod",
     "Прототип с кейс-чемпионата: тест спроса для микробизнеса и рассрочка на закупку.",
     "TypeScript, React, Express, Gemini", cards.comet, WARM),
    ("grabtree", "grabtree",
     "Семейное древо, которое можно редактировать. Сервер на Node без зависимостей.",
     "JavaScript, Node.js", cards.constellation, VIOLET),
]


def find(folder, family):
    matches = sorted(Path(folder).glob(f"{family}*.ttf"))
    if not matches:
        sys.exit(f"В {folder} нет файла {family}*.ttf")
    return matches[0]


def save(name, svg):
    (ASSETS / name).write_text(svg, encoding="utf-8", newline="\n")
    print(f"{name:28} {len(svg.encode()) / 1024:5.1f} KB")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    head = Face(find(sys.argv[1], "Montserrat"), 600, "m")
    text = Face(find(sys.argv[1], "Onest"), 400, "o")
    ASSETS.mkdir(exist_ok=True)

    save("header.svg", header.build(head, text))
    for seed, (name, title, about, note, body, tint) in enumerate(CARDS):
        svg = cards.build(head, text, title, about, note, body, tint, seed=40 + seed)
        save(f"card-{name}.svg", svg)


if __name__ == "__main__":
    main()
