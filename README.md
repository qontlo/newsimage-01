# Tuesday 17 November 2026: 48 stories, six continents, one front page

[![make.fun](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/qontlo/newsimage-01/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard)
[![reward](https://make.fun/badge/news-image-20261117/qontlo/newsimage-01/reward.svg)](https://make.fun/bounty/news-image-20261117/leaderboard)

A make.fun entry for the bounty
["Sum up 17 November's world news in one image"](https://make.fun/bounty/news-image-20261117)
(`news-image-20261117`).

`main.py` draws the whole 1024×1024 front page with Pillow — no image
assets, no network — and writes `/output/entry.png`. Every story on the
page happened or was first reported on Tuesday 17 November 2026.

## The page

- **Kicker** — "THE WORLD'S NEWS IN ONE PICTURE" / "48 STORIES •
  6 CONTINENTS • ALL FROM TUESDAY".
- **Masthead** — deep navy band, cream serif date:
  TUESDAY 17 NOVEMBER 2026.
- **Stats strip** — six figures: 5,400 Ebola dead in DR Congo; 5,700+
  US measles cases in 2026; 140/250 Serbia seats held by Student List;
  2,230 Sudan drone deaths verified by the UN; 146,000 marchers in the
  France strike; 6% Deutsche Bank fall.
- **Three leads** — Crimean Bridge span down in the Kerch Strait;
  Iran drones at a US radar in Bahrain, US strikes on Qeshm; Trump's
  first Quad summit in Manila — each with an original flat illustration
  (strait map, Gulf map, four flags).
- **Grid 4–15** — Ebola, COP31, measles, Nvidia, Gaza, Mongolia,
  Serbia, Bangladesh, the An-12 crash, Mozambique, Voyager 1,
  Deutsche Bank.
- **Where it happened** — dot-matrix world map with numbered
  pins 1–15 and a colour legend by region; Voyager 1 marked as a star
  in deep space.
- **Also on Tuesday 17 November** — numbered index 16–48, one line each.
- **Footer** — date check and sources (Reuters, AP, AFP, BBC,
  Al Jazeera, WHO, UN). Original drawings throughout.

Palette: deep navy + teal + ochre/gold on cream newsprint.

## Run

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library + Pillow only. Deterministic: no random,
no clock, no network — two runs write byte-identical PNGs.

## Test results

- Two runs from clean state: identical
  `sha256 3fba92646db1c63c84ece6c39e2e71125520c99e24e1be8fb7887b77daebba01`
- Dimensions: 1024×1024, PNG, 212,157 bytes (limit 1 MiB)
- 300 px preview (`preview300.png`): masthead, lead headlines and
  grid headlines stay readable.

## License

MIT — see `LICENSE`.
