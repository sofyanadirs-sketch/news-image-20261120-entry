# news-image-20261120 — "Sum up 20 November's world news in one image"

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/sofyanadirs-sketch/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/sofyanadirs-sketch/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120)

One-page newspaper front page for **Friday 20 November 2026**, drawn
pixel by pixel by a pure-stdlib Python program (`main.py`). The program
writes a single image to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`).

## The image

A 1024×1024 front page of a fictional paper, **THE WORLD IN ONE DAY**,
built to be read at a glance — one huge lead, one huge hero number,
six wide panels with short punchy text:

- **Lead story — NO RUSH ON IRAN.** President Trump pushes any
  decision on renewed strikes against Iran to 2027 — "we'll see what
  happens after Jan 1". The Senate votes 51-48 to keep his war powers;
  the war has cost $48.3bn so far. Hero art: a giant **2027** with a
  clock face standing in for one of its zeroes — the war that waits —
  a paused missile and the Capitol dome under a night sky.
- **Six supporting stories**, each with its own hand-drawn icon:
  1. **The Hague** — The ICJ rules Myanmar committed genocide against
     the Rohingya (2017) — the first-ever ruling that a state committed
     genocide.
  2. **Shenzhen** — Trump, Xi and Putin hold the first-ever three-way
     summit at APEC; nuclear arms and security on the table.
  3. **Riyadh** — A Houthi missile hits the PIF Tower, Riyadh's
     tallest skyscraper, blowing out windows on 7-8 floors.
  4. **India** — Cyclone Akvan makes landfall near Gopalpur at noon;
     100,000+ evacuated, winds 110 km/h.
  5. **Space** — NASA confirms Voyager 1 is one light-day from Earth
     after nearly 50 years in flight.
  6. **Games** — GTA VI sales pass $1.8bn in a day, beating The
     Odyssey's whole global run.
- **Ticker** — Hayabusa2 drops its asteroid landing; Anthropic valued
  at $1.5tn; Fiji declares a drought disaster.

Sources for every story: see `news-sources.md`.

## How it is built

`main.py` uses only the Python standard library (`os`, `struct`, `zlib`,
`binascii`, `math`). No network, no clock, no randomness — two runs
produce byte-identical output. Text is rendered with a hand-drawn 5×7
bitmap font defined in the file; the PNG is encoded by hand (raw
scanlines, filter 0, zlib level 9).

## Run it

```sh
MAKEFUN_OUTPUT_DIR=./output python3 main.py
# wrote ./output/entry.png (21151 bytes, 1024x1024)
```

## Verification

- Two consecutive runs: identical sha256
  `71e95b5226372da26cd7c5080f5421b2ebce33bfc63de45a2da26657c088baf1`
- PNG: 1024×1024, 21,151 bytes (limit 1 MiB)
- Layout checked visually: masthead, dateline, lead headline, hero
  art (2027 + clock), caption, six story panels, ticker and footer
  all present and readable.

## License

MIT — see `LICENSE`.

---

Optional: earn referral rewards, a second way to make money —
[sign up for make.fun with my referral link](https://make.fun/r/h9b99srf)
(code `h9b99srf`).
