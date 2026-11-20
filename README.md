# THE WORLD IN ONE DAY — Friday 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/sofyanadirs-sketch/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/sofyanadirs-sketch/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120)

One image that sums up the world's news of Friday 20 November 2026, drawn
as a one-page newspaper front page: one dominant lead story, four
supporting stories, and a wire ticker with the rest of the day.

## What the entry does

`main.py` (Python 3.13, standard library only, no network) draws the front
page pixel by pixel — masthead, headline, lead art panel, story grid,
ticker, sources — and writes it to `/output/entry.png` (1024x1024 PNG,
about 20 KB). The program is fully deterministic: two runs write
byte-identical files.

The day's news, as the page tells it:

- **Lead — Shenzhen:** Trump, Xi and Putin hold the first-ever three-way
  summit and issue a four-point "Declaration toward Peace" — UN reform,
  fuel for all, state immunity, nuclear-risk talks — with no word on
  Ukraine or Iran.
- **The Hague:** the ICJ rules Myanmar committed genocide against the
  Rohingya — the first ruling ever that a state committed genocide.
- **India:** Cyclone Akvan makes landfall near Gopalpur at noon; 300,000+
  evacuated, winds gusting to 110 km/h.
- **Washington:** the Senate rejects the Iran war-powers resolution 51-48;
  the Pentagon puts the war's cost at $48.3 billion.
- **Markets:** Anthropic's $81 billion IPO, the biggest listing ever;
  shares jump 34% on debut, valuing the company at about $1.5 trillion.
- **Ticker:** Haiti offensive, Venezuela-US military deal, Ukraine hits the
  Crimea bridge, Fiji drought disaster, Seoul clears ex-PM Han.

Sources are listed in `news-sources.md`.

## Run

```sh
python3 main.py
# writes /output/entry.png
# or: ENTRY_OUT=entry.png python3 main.py
```

## Files

- `main.py` — the entry program (the only file the run needs)
- `news-sources.md` — the reporting behind every story on the page
- `BUILD-NOTES.md` — how this entry was built and verified

## License

MIT — see `LICENSE`.

---

Optional: earn referral rewards, a second way to make money —
[make.fun](https://make.fun/r/h9b99srf) (referral code `h9b99srf`).
