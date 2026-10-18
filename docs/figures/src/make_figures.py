"""Rebuild the README figures from the published E11 summary.

    python docs/figures/src/make_figures.py            # writes HTML pages to docs/figures/src/build/
    node docs/figures/src/render.mjs                   # renders them to PNG in docs/figures/

Every number on the two charts and the stats strip is read from
results/E11-8k-returns/summary.json, so they can be checked without an API key
or price data. The worked examples (Alexion, Boeing) use per-filing returns,
which are not published; their values are written here and in the README.
The social preview is uploaded in the repository settings and is not
committed; render.mjs leaves it in build/. Rendering needs Node and
Playwright; the pages load IBM Plex from Google Fonts.
"""

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUMMARY = ROOT / "results" / "E11-8k-returns" / "summary.json"
OUT = Path(__file__).resolve().parent / "build"

# Every README image is drawn on one canvas width and rendered at 2x, so
# README text is never smaller than 16 px here (32 px in the PNG).
WIDTH = 1200

FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">'
)

THEMES = {
    "dark": {
        "bg": "#0D1117",
        "panel": "#161B22",
        "panel2": "#0F1520",
        "border": "#30363D",
        "ink": "#E6EDF3",
        "ink2": "#9DA7B3",
        "body": "#C9D1D9",
        "accent": "#5EEAD4",
        "grid": "#21262D",
        "zero": "#6E7681",
        "bad": "#F0883E",
        "good": "#58A6FF",
        "base": "#8B949E",
        "ret": "#F0A070",
        "bars": ["#C2410C", "#E8894A", "#8B949E", "#7DB8FF", "#1F6FEB"],
    },
    "light": {
        "bg": "#FFFFFF",
        "panel": "#F6F8FA",
        "panel2": "#F6F8FA",
        "border": "#D1D9E0",
        "ink": "#1F2328",
        "ink2": "#59636E",
        "body": "#1F2328",
        "accent": "#0F766E",
        "grid": "#E6E8EB",
        "zero": "#9AA1A9",
        "bad": "#C2410C",
        "good": "#1F6FEB",
        "base": "#A8B0B8",
        "ret": "#C2410C",
        "bars": ["#C2410C", "#E8894A", "#8C959F", "#5A9BE6", "#1F6FEB"],
    },
}

SCALE = [
    ("Very bad", "#C2410C", "#FFFFFF"),
    ("Bad", "#E8894A", "#0D1117"),
    ("Neutral", "#C9D1D9", "#0D1117"),
    ("Good", "#7DB8FF", "#0D1117"),
    ("Very good", "#1F6FEB", "#FFFFFF"),
]
ANSWERS = ["very_bad", "bad", "neutral", "good", "very_good"]

TITLE = "Decision-model ratings of 8-K filings and short-term stock returns"


def r3(v):
    """Round half up, as the README does (0.0545 -> 0.055, not float 0.054)."""
    q = Decimal(repr(abs(v))).quantize(Decimal("0.001"), ROUND_HALF_UP)
    return ("+" if v >= 0 else "−") + str(q)


def pct(v, places=2):
    q = Decimal(repr(abs(v))).quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)
    return ("+" if v >= 0 else "−") + f"{q}%"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def page(name, body, bg, width=WIDTH):
    OUT.mkdir(parents=True, exist_ok=True)
    (
        OUT / f"{name}.html"
    ).write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">{FONTS}
<style>
html,body{{margin:0;background:{bg}}}
*{{box-sizing:border-box}}
#art{{width:{width}px;background:{bg};font-family:'IBM Plex Sans',sans-serif}}
.mono{{font-family:'IBM Plex Mono',monospace}}
</style></head><body><div id="art">{body}</div></body></html>""")


def text(x, y, s, size, fill, anchor="start", weight=400, mono=False):
    fam = "IBM Plex Mono" if mono else "IBM Plex Sans"
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'
    )


def svg(w, h, t, parts):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>{"".join(parts)}</svg>'
    )


def scale_bar(height, font):
    cells = "".join(
        f'<div class="mono" style="height:{height}px;display:flex;align-items:center;padding:0 14px;'
        f'border-radius:6px;background:{bg};color:{fg};font-size:{font}px">{label}</div>'
        for label, bg, fg in SCALE
    )
    return f'<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:4px">{cells}</div>'


def banner(t):
    return f"""<div style="border-radius:14px;background:{t["panel2"]};border:1px solid {t["border"]};
 padding:40px 44px 34px;display:flex;flex-direction:column;gap:30px;color:{t["ink"]}">
 <div style="display:flex;flex-direction:column;gap:14px">
  <div class="mono" style="font-size:17px;letter-spacing:.08em;color:{t["accent"]}">SEC FORM 8-K · S&amp;P 500 · 2013–2026</div>
  <div style="font-size:46px;font-weight:700;line-height:1.08;letter-spacing:-.01em;max-width:1040px">Decision-model ratings of 8-K filings<br>and short-term stock returns</div>
  <div style="font-size:20px;line-height:1.45;color:{t["ink2"]};max-width:1000px">A decision model, which returns a probability for each answer option and writes no text, rates each company filing from very bad to very good for shareholders. The ratings are tested against stock returns.</div>
 </div>
 {scale_bar(36, 17)}
</div>"""


def stats_strip(t, S):
    m = S["main"]["rating_score"]
    years = S["by_year"]
    pos = sum(v > 0 for v in years.values())
    tiles = [
        (
            r3(m[0]),
            "rank correlation with the 2-day return",
            f"95% interval {r3(m[1])} to {r3(m[2])}",
        ),
        (
            f"{pos} of {len(years)}",
            "years with a positive correlation",
            f"{min(years)} to {max(years)}, the same test each year",
        ),
        (
            f"${S_COST['dollars']:.2f}",
            "of model time to rate the filings",
            f"{S['n_events']:,} filings, {S_COST['tokens_m']} million input tokens",
        ),
    ]
    cells = "".join(
        f"""<div style="padding:24px 28px;display:flex;flex-direction:column;gap:6px;{"border-left:1px solid " + t["border"] + ";" if i else ""}">
 <div class="mono" style="font-size:42px;font-weight:600;color:{t["accent"]};line-height:1.1">{big}</div>
 <div style="font-size:19px;color:{t["ink"]}">{label}</div>
 <div style="font-size:16px;color:{t["ink2"]}">{sub}</div></div>"""
        for i, (big, label, sub) in enumerate(tiles)
    )
    return (
        f'<div style="background:{t["panel"]};border:1px solid {t["border"]};border-radius:14px;'
        f'display:grid;grid-template-columns:repeat(3,minmax(0,1fr))">{cells}</div>'
    )


# The cost is not in summary.json; it comes from the scoring run's metadata
# (results/E11-8k-returns/scores.meta.json) and the public price.
S_COST = {"dollars": 2.32, "tokens_m": 55}


def return_by_rating(t, S):
    data = S["mean_2d_pct_by_jev_answer"]
    W, H = WIDTH, 640
    L, R, top, bot = 96, 40, 150, 520
    lo, hi = -1.5, 0.75
    y = lambda v: top + (hi - max(lo, min(hi, v))) / (hi - lo) * (bot - top)
    slot = (W - L - R) / 5
    p = [
        text(24, 46, "Lower ratings, lower 2-day returns", 30, t["ink"], weight=600),
        text(
            24,
            84,
            "Average market-adjusted return over 2 days, by the model’s answer. 26,962 S&P 500 8-Ks, 2013–2026.",
            18,
            t["ink2"],
        ),
        text(24, 112, "Whiskers: 95% intervals from resampling calendar months.", 18, t["ink2"]),
    ]
    for v in (0.5, 0, -0.5, -1.0, -1.5):
        Y = y(v)
        p.append(
            f'<line x1="{L}" x2="{W - R}" y1="{Y:.1f}" y2="{Y:.1f}" stroke="{t["zero"] if v == 0 else t["grid"]}" stroke-width="{1.5 if v == 0 else 1}"/>'
        )
        p.append(
            text(L - 12, Y + 6, "0%" if v == 0 else pct(v, 1), 17, t["ink2"], "end", mono=True)
        )
    for i, k in enumerate(ANSWERS):
        mean, ci_lo, ci_hi, n = data[k]
        cx = L + slot * (i + 0.5)
        bw = slot * 0.46
        y0, y1 = y(0), y(mean)
        p.append(
            f'<rect x="{cx - bw / 2:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(abs(y1 - y0), 2):.1f}" rx="3" fill="{t["bars"][i]}"/>'
        )
        clipped = ci_lo < lo
        p.append(
            f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{y(ci_lo):.1f}" y2="{y(ci_hi):.1f}" stroke="{t["ink"]}" stroke-width="2"/>'
        )
        p.append(
            f'<line x1="{cx - 8:.1f}" x2="{cx + 8:.1f}" y1="{y(ci_hi):.1f}" y2="{y(ci_hi):.1f}" stroke="{t["ink"]}" stroke-width="2"/>'
        )
        if clipped:
            yb = y(lo)
            p.append(
                f'<path d="M{cx - 8:.1f},{yb - 10:.1f} L{cx:.1f},{yb + 2:.1f} L{cx + 8:.1f},{yb - 10:.1f}" fill="none" stroke="{t["ink"]}" stroke-width="2"/>'
            )
        else:
            p.append(
                f'<line x1="{cx - 8:.1f}" x2="{cx + 8:.1f}" y1="{y(ci_lo):.1f}" y2="{y(ci_lo):.1f}" stroke="{t["ink"]}" stroke-width="2"/>'
            )
        lx = cx + bw / 2 + 10
        label_y = y(mean) + (24 if mean < 0 else -10)
        if clipped:
            label_y = y(mean) - 64
        p.append(text(lx, label_y, pct(mean), 18, t["ink"], weight=600, mono=True))
        if clipped:
            p.append(text(lx, label_y + 24, "interval", 16, t["ink2"], mono=True))
            p.append(
                text(lx, label_y + 46, f"{pct(ci_lo)} to {pct(ci_hi)}", 16, t["ink2"], mono=True)
            )
        p.append(text(cx, bot + 40, SCALE[i][0], 18, t["ink"], "middle", weight=600))
        p.append(text(cx, bot + 64, f"{n:,} filings", 16, t["ink2"], "middle", mono=True))
    p.append(
        text(
            24,
            H - 12,
            "Means pooled across item groups and years; the test itself compares filings within the same item group and year.",
            16,
            t["ink2"],
        )
    )
    return svg(W, H, t, p)


def correlation_by_window(t, S):
    W, H = WIDTH, 660
    cats = [
        ("window_d0", "Day 0"),
        ("window_d0_1", "2 days (main)"),
        ("window_d0_4", "5 days"),
        ("window_d0_9", "10 days"),
        ("window_drift_5", "Close to +5"),
        ("window_drift_10", "Close to +10"),
    ]
    xs = [190, 360, 530, 700, 930, 1100]
    y0, y1, lo, hi = 540, 200, -0.03, 0.05
    sy = lambda v: y0 - (v - lo) / (hi - lo) * (y0 - y1)
    p = [
        text(
            24,
            46,
            "Strongest on the filing day, gone after the first close",
            30,
            t["ink"],
            weight=600,
        ),
        text(
            24,
            84,
            "Rank correlation with the market-adjusted return, within item group and year. Bars: 95% intervals.",
            18,
            t["ink2"],
        ),
        f'<circle cx="34" cy="122" r="8" fill="{t["good"]}"/>',
        text(50, 128, "Model rating", 18, t["ink"]),
        f'<circle cx="200" cy="122" r="8" fill="{t["base"]}"/>',
        text(
            216, 128, "Word-tone score, positive minus negative words (free method)", 18, t["ink"]
        ),
        text(110, 176, "From the last close before the filing", 17, t["ink2"]),
        text(842, 176, "From the first close after it", 17, t["ink2"]),
    ]
    for v in (-0.02, 0.0, 0.02, 0.04):
        Y = sy(v)
        p.append(
            f'<line x1="100" x2="{W - 24}" y1="{Y:.1f}" y2="{Y:.1f}" stroke="{t["zero"] if v == 0 else t["grid"]}" stroke-width="{1.5 if v == 0 else 1}"/>'
        )
        p.append(
            text(90, Y + 6, "0.00" if v == 0 else f"{v:+.2f}", 17, t["ink2"], "end", mono=True)
        )
    p.append(
        f'<line x1="830" x2="830" y1="156" y2="580" stroke="{t["zero"]}" stroke-width="1.5" stroke-dasharray="5 5"/>'
    )
    for (key, label), X in zip(cats, xs):
        r = S[key]
        for series, dx, col in (("base_good", -16, t["base"]), ("rating_score", 16, t["good"])):
            m, l, h = r[series]
            p.append(
                f'<line x1="{X + dx}" x2="{X + dx}" y1="{sy(l):.1f}" y2="{sy(h):.1f}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'
            )
            p.append(
                f'<circle cx="{X + dx}" cy="{sy(m):.1f}" r="9" fill="{col}" stroke="{t["bg"]}" stroke-width="2"/>'
            )
        if key in ("window_d0_1", "window_d0_9"):
            m = r["rating_score"][0]
            p.append(text(X + 32, sy(m) + 6, r3(m), 17, t["ink"], mono=True))
        p.append(
            text(X, 572, label, 17, t["ink"], "middle", weight=600 if key == "window_d0_1" else 400)
        )
    p.append(
        text(
            24,
            H - 40,
            "Above zero: filings rated or worded more positively were followed by better returns.",
            16,
            t["ink2"],
        )
    )
    p.append(
        text(
            24,
            H - 14,
            "The word-tone score sits below zero: more upbeat wording was followed by slightly worse returns.",
            16,
            t["ink2"],
        )
    )
    return svg(W, H, t, p)


EXAMPLES = [
    {
        "when": "12 Dec 2016, before the open",
        "company": "Alexion Pharmaceuticals",
        "item": "Item 5.02",
        "what": 'The CEO resigns immediately "for personal reasons" and the CFO leaves.',
        "answer": 0,
        "note": "98% probability of bad or very bad.",
        "ret": "−17.3%",
        "ret_note": "2 days, against the market; −3.9% by day 10.",
        "why": "Picked after grading as an illustration: the third-largest 2-day fall among the 79 filings rated very bad.",
    },
    {
        "when": "23 Dec 2019, after the close",
        "company": "Boeing",
        "item": "Item 5.02",
        "what": "The CEO resigns effective immediately and an interim CEO is named. The company had announced it that morning.",
        "answer": 1,
        "note": "95% probability of bad or very bad.",
        "ret": "−2.80%",
        "ret_note": "2 days, against the market; −2.84% by day 10.",
        "why": "Chosen as the example when the test was designed, before any return was computed.",
    },
]


def rating_examples(t):
    card = (
        f"background:{t['panel']};border:1px solid {t['border']};border-radius:14px;padding:22px 24px;"
        f"display:flex;flex-direction:column;gap:10px;color:{t['ink']}"
    )
    step = f'class="mono" style="font-size:16px;letter-spacing:.07em;color:{t["ink2"]}"'
    note = f'style="font-size:17px;line-height:1.45;color:{t["body"]}"'
    rows = []
    for e in EXAMPLES:
        label, bg, fg = SCALE[e["answer"]]
        rows.append(f"""<div style="display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:16px">
 <div style="{card}"><div {step}>THE FILING</div>
  <div class="mono" style="font-size:16px;line-height:1.55">{e["item"]} · {e["company"]}<br>{e["when"]}</div>
  <div {note}>{esc(e["what"])}</div></div>
 <div style="{card}"><div {step}>THE RATING</div>
  <div><span class="mono" style="display:inline-block;padding:7px 14px;border-radius:8px;background:{bg};color:{fg};font-size:17px">{label}</span></div>
  <div {note}>{esc(e["note"])}</div></div>
 <div style="{card}"><div {step}>THE RETURN</div>
  <div class="mono" style="font-size:38px;font-weight:600;color:{t["ret"]};line-height:1.1">{e["ret"]}</div>
  <div {note}>{esc(e["ret_note"])}</div></div>
</div>
<div style="font-size:16px;color:{t["ink2"]};margin:-4px 4px 4px">{esc(e["why"])}</div>""")
    return f'<div style="display:flex;flex-direction:column;gap:14px">{"".join(rows)}</div>'


def social():
    return """<div style="width:1280px;height:640px;padding:76px 84px;background:#0D1117;color:#E6EDF3;
 display:flex;flex-direction:column;justify-content:center;gap:30px">
 <div class="mono" style="font-size:26px;letter-spacing:.06em;color:#5EEAD4">SEC FORM 8-K · S&amp;P 500</div>
 <div style="width:96px;height:3px;background:#5EEAD4"></div>
 <div style="font-size:58px;font-weight:700;line-height:1.08;letter-spacing:-.015em">Decision-model ratings of 8-K filings<br>and short-term stock returns</div>
 <div style="font-size:48px;line-height:1.22;color:#F0F3F6;max-width:1100px">Fourteen years of 8-K filings, rated for $2.32 and checked against the market.</div>
</div>"""


def main():
    S = json.loads(SUMMARY.read_text())
    for theme, t in THEMES.items():
        page(f"banner-{theme}", banner(t), t["bg"])
        page(f"stats-{theme}", stats_strip(t, S), t["bg"])
        page(f"return-by-rating-{theme}", return_by_rating(t, S), t["bg"])
        page(f"correlation-by-window-{theme}", correlation_by_window(t, S), t["bg"])
        page(f"rating-example-{theme}", rating_examples(t), t["bg"])
    page("social-preview", social(), "#0D1117", width=1280)
    print("\n".join(sorted(p.name for p in OUT.glob("*.html"))))


if __name__ == "__main__":
    main()
