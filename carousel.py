"""LinkedIn carousel (PDF) of the 'How the #1 hit changed' dashboard. All numbers read from out/*.csv."""
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

O = "out"
dec = pd.read_csv(f"{O}/number_ones_by_decade.csv")
yr = pd.read_csv(f"{O}/hot100_by_year.csv")
t10 = pd.read_csv(f"{O}/hot100_top10_by_decade.csv")
art = pd.read_csv(f"{O}/artists_most_number_ones.csv")
wk = pd.read_csv(f"{O}/artists_most_weeks_at_1.csv")
intl = pd.read_csv(f"{O}/international_by_decade.csv")
ctry = pd.read_csv(f"{O}/countries_number_ones.csv")
rec = pd.read_csv(f"{O}/records.csv").fillna("")
sa = pd.read_csv(f"{O}/south_asian_roots.csv")
ind = pd.read_csv(f"{O}/india_on_number_ones.csv")
H = json.load(open(f"{O}/headlines.json"))

W, HH = 1080, 1350
BG, FG, MU, GRID = (250, 246, 240), (38, 34, 30), (112, 104, 96), (226, 218, 208)
C = dict(c1=(217, 102, 63), c2=(212, 154, 18), c3=(42, 157, 143), c4=(139, 95, 191), c5=(63, 124, 196),
         c6=(212, 92, 134), c7=(94, 158, 79), c8=(224, 123, 46), c9=(46, 139, 87))
IF = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
F = lambda w, s: ImageFont.truetype(IF.format(w), s)
TOTAL = 13
mmss = lambda s: f"{int(s)//60}:{int(round(s))%60:02d}"
pct = lambda v: f"{v:.0%}"
tint = lambda col, a=0.12: tuple(int(BG[i] * (1 - a) + col[i] * a) for i in range(3))
fade = lambda col, a: tuple(int(BG[i] * (1 - a) + col[i] * a) for i in range(3))


def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def slide(n, col, kicker, title, body=None):
    im = Image.new("RGB", (W, HH), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=col)
    d.ellipse([70, 70, 130, 130], fill=col)
    d.text((100, 100), str(n), font=F("Bold", 30), fill=(255, 255, 255), anchor="mm")
    d.text((150, 100), kicker.upper(), font=F("SemiBold", 24), fill=col, anchor="lm")
    y = 165
    for ln in wrap(d, title, F("Bold", 60), W - 140):
        d.text((70, y), ln, font=F("Bold", 60), fill=FG); y += 72
    if body:
        y += 14
        for ln in wrap(d, body, F("Regular", 31), W - 140):
            d.text((70, y), ln, font=F("Regular", 31), fill=MU); y += 44
    # footer
    d.line([70, HH - 95, W - 70, HH - 95], fill=GRID, width=2)
    d.text((70, HH - 58), "Mohit Saini  ·  How the #1 hit changed", font=F("Medium", 24), fill=MU, anchor="lm")
    d.text((W - 70, HH - 58), f"{n} / {TOTAL}" + ("   swipe →" if n < TOTAL else ""), font=F("SemiBold", 24), fill=col, anchor="rm")
    return im, d, y + 30


def bars(d, box, labels, vals, fmt, col, hl=None):
    x0, y0, x1, y1 = box
    vmax = max(vals) * 1.18
    n = len(vals); step = (x1 - x0) / n; bw = min(80, step * 0.62)
    base = y1 - 50
    d.line([x0, base, x1, base], fill=GRID, width=2)
    for i, (l, v) in enumerate(zip(labels, vals)):
        cx = x0 + step * (i + 0.5)
        top = base - (base - y0) * v / vmax
        strong = (i == n - 1) if hl is None else hl(i)
        c = col if strong else fade(col, 0.45)
        d.rounded_rectangle([cx - bw / 2, top, cx + bw / 2, base], 10, fill=c)
        d.rectangle([cx - bw / 2, base - 10, cx + bw / 2, base], fill=c)
        d.text((cx, top - 12), fmt(v), font=F("Bold", 27), fill=col if strong else MU, anchor="ms")
        d.text((cx, base + 16), l, font=F("Medium", 22), fill=MU, anchor="mt")


def hbars(d, box, labels, vals, cols, fmt, rowh=56):
    x0, y0, x1, y1 = box
    lw = max(d.textlength(l, font=F("Medium", 28)) for l in labels) + 24
    vmax = max(vals)
    for i, (l, v, c) in enumerate(zip(labels, vals, cols)):
        y = y0 + i * rowh
        d.text((x0 + lw - 24, y + rowh / 2 - 4), l, font=F("Medium", 28), fill=FG, anchor="rm")
        w = (x1 - x0 - lw - 110) * v / vmax
        d.rounded_rectangle([x0 + lw, y + 10, x0 + lw + max(w, 8), y + rowh - 18], 8, fill=c)
        d.text((x0 + lw + w + 12, y + rowh / 2 - 4), fmt(v), font=F("Bold", 28), fill=c, anchor="lm")


def line(d, box, xs, ys, col, fmt, ymax, events=(), yt=None):
    x0, y0, x1, y1 = box
    base = y1 - 44
    X = lambda x: x0 + 70 + (x1 - x0 - 150) * (x - xs[0]) / (xs[-1] - xs[0])
    Y = lambda v: base - (base - y0 - 60) * v / ymax
    for t in (yt or [ymax * k / 4 for k in range(5)]):
        d.line([x0 + 70, Y(t), x1 - 80, Y(t)], fill=GRID, width=1)
        d.text((x0 + 58, Y(t)), fmt(t), font=F("Medium", 20), fill=MU, anchor="rm")
    for k, (ex, lab) in enumerate(events):
        d.line([X(ex), y0 + 10 + (k % 2) * 30, X(ex), base], fill=(196, 188, 178), width=2)
        d.text((X(ex) + 6, y0 + 22 + (k % 2) * 30), lab, font=F("Medium", 20), fill=MU, anchor="lm")
    pts = [(X(x), Y(v)) for x, v in zip(xs, ys)]
    poly = pts + [(pts[-1][0], base), (pts[0][0], base)]
    ov = Image.new("RGBA", (W, HH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.polygon(poly, fill=col + (40,))
    return pts, ov, base, X


def paste_line(im, d, pts, ov, col, lab):
    im.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(im)
    d.line(pts, fill=col, width=6, joint="curve")
    d.ellipse([pts[-1][0] - 9, pts[-1][1] - 9, pts[-1][0] + 9, pts[-1][1] + 9], fill=col)
    d.text((pts[-1][0] + 14, pts[-1][1]), lab, font=F("Bold", 28), fill=col, anchor="lm")
    return d


def xticks(d, X, base, years):
    for t in years:
        d.text((X(t), base + 14), str(t), font=F("Medium", 21), fill=MU, anchor="mt")


def callout(d, y, col, big, small):
    d.rounded_rectangle([70, y, W - 70, y + 150], 22, fill=tint(col))
    d.rounded_rectangle([70, y, 84, y + 150], 7, fill=col)
    d.text((112, y + 20), big, font=F("Bold", 58), fill=col)
    for k, ln in enumerate(wrap(d, small, F("Medium", 26), W - 220)[:2]):
        d.text((114, y + 92 + k * 32), ln, font=F("Medium", 26), fill=FG)


slides = []
D = dec.set_index("decade")
labs = dec["decade_label"].str.replace("1958–59", "'58–59").str.replace("2020–25", "2020–25").tolist()
short = [l.replace("19", "'", 1) if l.startswith("19") and l.endswith("s") else l for l in labs]

# 1 cover
im = Image.new("RGB", (W, HH), BG); d = ImageDraw.Draw(im)
cx, cy = 900, 230
for k in range(300, 70, -13): d.ellipse([cx - k, cy - k, cx + k, cy + k], outline=GRID, width=2)
d.ellipse([cx - 85, cy - 85, cx + 85, cy + 85], fill=C["c1"]); d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=C["c2"])
d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=BG)
x = 70
for c in ["c1", "c2", "c7", "c3", "c5", "c4", "c6"]: d.rectangle([x, 120, x + 46, 132], fill=C[c]); x += 46
d.text((70, 170), "BILLBOARD 1958–2025 · DATA STORY", font=F("SemiBold", 26), fill=MU)
d.text((70, 220), "How the", font=F("Bold", 120), fill=FG)
d.text((70, 360), "#1 hit", font=F("Bold", 120), fill=FG)
d.text((70, 500), "changed", font=F("Bold", 120), fill=C["c1"])
yy = 700
for ln in wrap(d, f"67 years. {H['n_number_ones']:,} #1 hits. {H['n_hot100_songs']:,} songs on the Hot 100. "
                  "What the data says about song length, songwriting, chart runs, the biggest artists — and India's place on America's chart.",
               F("Regular", 36), W - 140):
    d.text((70, yy), ln, font=F("Regular", 36), fill=FG); yy += 52
chips = [("Shorter songs", "c1"), ("Bigger writing teams", "c4"), ("Week-one hits", "c5"), ("Top artists", "c6"), ("India", "c8")]
x, yy = 70, yy + 40
for t, c in chips:
    tw = d.textlength(t, font=F("SemiBold", 26)) + 44
    if x + tw > W - 70: x, yy = 70, yy + 68
    d.rounded_rectangle([x, yy, x + tw, yy + 52], 26, fill=tint(C[c], 0.16)); d.text((x + 22, yy + 26), t, font=F("SemiBold", 26), fill=C[c], anchor="lm"); x += tw + 14
d.text((70, HH - 120), "Analysis by Mohit Saini · Data Analyst", font=F("SemiBold", 30), fill=FG)
d.text((W - 70, HH - 120), "swipe →", font=F("Bold", 30), fill=C["c1"], anchor="ra")
slides.append(im)

# 2 length
im, d, y = slide(2, C["c1"], "Songs got shorter", "The typical #1 lost 50 seconds since the 1990s",
                 "Median length of #1 hits by decade. Songs grew until the 90s, then reversed in the streaming era.")
bars(d, (70, y + 40, W - 70, y + 620), short, dec.median_length_sec.tolist(), mmss, C["c1"])
callout(d, HH - 290, C["c1"], f"{mmss(D.loc[1990,'median_length_sec'])} → {mmss(D.loc[2020,'median_length_sec'])}", "Median #1 length, 1990s vs 2020–25")
slides.append(im)

# 3 intro + fade
im, d, y = slide(3, C["c3"], "Get to the hook", "Intros were cut in half, and the fade-out disappeared",
                 "Median seconds before the lead vocal starts, by decade.")
bars(d, (70, y + 40, W - 70, y + 560), short, dec.median_intro_sec.tolist(), lambda v: f"{v:g}s", C["c3"])
callout(d, HH - 290, C["c3"], f"{pct(D.loc[1980,'share_fade_out'])} → {pct(D.loc[2020,'share_fade_out'])}", "#1 hits that end with a fade-out, 1980s vs 2020–25")
slides.append(im)

# 4 writers
im, d, y = slide(4, C["c4"], "A #1 takes a team", "Songwriting credits more than doubled",
                 "Average credited songwriters per #1 hit (sample and interpolation credits excluded).")
bars(d, (70, y + 40, W - 70, y + 560), short, dec.avg_songwriters.tolist(), lambda v: f"{v:.1f}", C["c4"])
callout(d, HH - 290, C["c4"], f"{pct(D.loc[1980,'share_solo_writer'])} → {pct(D.loc[2020,'share_solo_writer'])}", "#1 hits written by a single person, 1980s vs 2020–25")
slides.append(im)

# 5 debuts
im, d, y = slide(5, C["c5"], "Hits arrive, they don't climb", "Most big hits now debut at full strength",
                 "Share of each year's top-10 hits that entered the Hot 100 already in the top 10. Dashed lines: Billboard rule changes.")
xs, ys = yr.year.tolist(), yr.top10_debuting_in_top10.tolist()
pts, ov, base, X = line(d, (70, y + 20, W - 70, y + 560), xs, ys, C["c5"], pct, 0.8,
                        events=[(1991.9, "Sales data"), (2005.1, "Downloads"), (2013.1, "YouTube")])
d = paste_line(im, d, pts, ov, C["c5"], pct(ys[-1]))
xticks(d, X, base, [1960, 1970, 1980, 1990, 2000, 2010, 2020])
callout(d, HH - 290, C["c5"], f"{pct(H['top10_debut_1980s'])} → {pct(H['top10_debut_2020'])}", "Top-10 hits that debuted in the top 10, 1980s vs 2020")
slides.append(im)

# 6 churn
im, d, y = slide(6, C["c3"], "More songs, shorter lives", "Streaming flooded the chart with new entries",
                 "Different songs entering the Hot 100 each year.")
xs, ys = yr.year.tolist(), yr.new_songs.tolist()
pts, ov, base, X = line(d, (70, y + 20, W - 70, y + 590), xs, ys, C["c3"], lambda v: f"{int(v)}", 800)
d = paste_line(im, d, pts, ov, C["c3"], f"{ys[-1]}")
xticks(d, X, base, [1960, 1970, 1980, 1990, 2000, 2010, 2020])
Y = yr.set_index("year")
callout(d, HH - 290, C["c3"], f"{int(Y.loc[2001,'new_songs'])} → {int(Y.loc[2020,'new_songs'])}",
        f"New chart entries, 2001 low vs 2020 — while the typical entry in 2019 lasted just {Y.loc[2019,'median_weeks_on_chart']:.0f} weeks")
slides.append(im)

# 7 artists
im, d, y = slide(7, C["c6"], "Who owns the top spot", "The Beatles have the most #1s. Mariah has the most weeks.",
                 "#1 hits credited as lead or featured artist.")
top = art.head(10)
cols = [C["c6"] if o != "United States" else C["c5"] for o in top.origin]
hbars(d, (70, y + 20, W - 70, y + 700), top.artist.tolist(), top.number_ones.tolist(), cols, lambda v: str(int(v)), rowh=52)
ly = y + 20 + 52 * 10 + 14
d.rounded_rectangle([70, ly, 92, ly + 22], 5, fill=C["c6"]); d.text((102, ly + 11), "outside the US", font=F("Medium", 24), fill=MU, anchor="lm")
d.rounded_rectangle([320, ly, 342, ly + 22], 5, fill=C["c5"]); d.text((352, ly + 11), "US", font=F("Medium", 24), fill=MU, anchor="lm")
m = wk.set_index("artist")
callout(d, HH - 290, C["c6"], f"{int(m.loc['Mariah Carey','weeks_at_1'])} weeks", "Mariah Carey's total time at #1 — more than any other act")
slides.append(im)

# 8 world
im, d, y = slide(8, C["c7"], "The world on America's chart", "Non-US acts peaked in the 1980s, then came the Canadian wave",
                 "Share of #1 hits by acts from outside the US, by decade.")
il = intl.decade_label.tolist(); il = [l.replace("19", "'", 1) if l.startswith("19") and l.endswith("s") else l for l in il]
bars(d, (70, y + 30, W - 70, y + 350), il, intl.share_non_us.tolist(), pct, C["c7"], hl=lambda i: il[i] == "'80s")
c6 = ctry.head(6)
hbars(d, (70, y + 390, W - 70, y + 720), c6.country.tolist(), c6.number_ones.tolist(),
      [fade(C["c7"], 1 - i * 0.1) for i in range(6)], lambda v: f"{int(v)} #1s", rowh=50)
slides.append(im)

# 9 records
im, d, y = slide(9, C["c5"], "Record breakers", "Six chart records worth knowing")
R = rec.set_index("record")
cards = [("Longest run at #1", "c1", lambda r: f"{r.value} weeks", lambda r: f"{r.song} ({r.artist}, {r.year}), tied with Old Town Road (2019)"),
         ("Biggest leap to #1", "c5", lambda r: f"#{r.value} → #1", lambda r: f"{r.song} — {r.artist} ({r.year}), in one week"),
         ("Longest Hot 100 run (to May 2021)", "c3", lambda r: f"{r.value} weeks", lambda r: f"{r.song} — {r.artist}"),
         ("Youngest lead singer at #1", "c2", lambda r: f"{r.value} years old", lambda r: f"{r.note} ({r.artist})"),
         ("Oldest lead singer at #1", "c4", lambda r: f"{r.value} years old", lambda r: f"{r.artist}, {r.song} — {r.note}"),
         ("Longest span between first and latest #1", "c6", lambda r: f"{r.value} years", lambda r: f"{r.artist}: {r.note}")]
cy = y
for name, c, big, small in cards:
    r = R.loc[name]
    d.rounded_rectangle([70, cy, W - 70, cy + 136], 20, fill=tint(C[c]))
    d.rounded_rectangle([70, cy, 82, cy + 136], 6, fill=C[c])
    d.text((106, cy + 14), name.upper(), font=F("SemiBold", 20), fill=C[c])
    d.text((106, cy + 40), big(r), font=F("Bold", 42), fill=C[c])
    d.text((108, cy + 96), wrap(d, small(r), F("Medium", 22), W - 220)[0], font=F("Medium", 22), fill=FG)
    cy += 146
slides.append(im)

# 10 India
im, d, y = slide(10, C["c8"], "India on America's chart", "South Asian roots have reached #1 — and India's sound got there first",
                 None)
S = sa.set_index("song")
hits = sa[sa.song.isin(["Down", "Pillowtalk", "Franchise", "Paper Planes"]) | sa.song.str.startswith("Jai Ho")]
for _, r in hits.iterrows():
    col = C["c8"] if r.peak == 1 else C["c9"]
    d.rounded_rectangle([70, y, W - 70, y + 92], 18, fill=tint(col))
    d.text((106, y + 46), f"#{int(r.peak)}", font=F("Bold", 42), fill=col, anchor="lm")
    d.text((240, y + 16), f"{r.song[:38]}", font=F("SemiBold", 27), fill=FG)
    d.text((240, y + 54), f"{r.act} · {r.year} · {r.roots}"[:64], font=F("Regular", 22), fill=MU)
    y += 102
n_sitar = int((ind.link == "Features a sitar").sum())
cal = ind[ind.song == "Calcutta"].iloc[0]
callout(d, y + 14, C["c9"], f"{n_sitar} #1 hits", "feature a sitar — from Paint It Black (1966) to Baby Boy (2003)")
callout(d, y + 176, C["c8"], f"{cal.year}: Calcutta", f"An instrumental named after Kolkata went to #1 ({cal.artist})")
slides.append(im)

# 11 labels
im, d, y = slide(11, C["c2"], "Fewer owners", "Three companies now release most #1 hits",
                 "Share of #1 hits from the top three parent companies in each decade.")
bars(d, (70, y + 40, W - 70, y + 600), short, dec.top3_parent_share.tolist(), pct, C["c2"], hl=lambda i: short[i] == "2010s")
callout(d, HH - 290, C["c2"], f"{pct(D.loc[1960,'top3_parent_share'])} → {pct(D.loc[2010,'top3_parent_share'])}", "Top-3 parent companies' share of #1s, 1960s vs 2010s")
slides.append(im)

# 12 implications
im, d, y = slide(12, C["c4"], "So what?", "What this means for the music business")
items = [("A&R and production", "c6", "The opening seconds carry the song. Short intros and no fade-out are the norm among recent #1s."),
         ("Publishing", "c4", "More writers per hit means smaller shares and complex splits — accurate metadata matters more."),
         ("Marketing", "c5", "When hits peak in week one, the pre-release campaign decides the chart run."),
         ("Data & catalogue teams", "c7", "High churn means many songs get a brief moment. Spotting which keep streaming is where analytics adds value.")]
for t, c, txt in items:
    d.rounded_rectangle([70, y, W - 70, y + 190], 20, fill=tint(C[c]))
    d.rounded_rectangle([70, y, W - 70, y + 10], 5, fill=C[c])
    d.text((104, y + 34), t, font=F("Bold", 34), fill=C[c])
    for k, ln in enumerate(wrap(d, txt, F("Regular", 28), W - 210)[:3]):
        d.text((104, y + 84 + k * 36), ln, font=F("Regular", 28), fill=FG)
    y += 208
slides.append(im)

# 13 CTA
im = Image.new("RGB", (W, HH), BG); d = ImageDraw.Draw(im)
x = 70
for c in ["c1", "c2", "c7", "c3", "c5", "c4", "c6"]: d.rectangle([x, 120, x + 46, 132], fill=C[c]); x += 46
d.text((70, 200), "Want the full", font=F("Bold", 96), fill=FG)
d.text((70, 320), "interactive version?", font=F("Bold", 96), fill=C["c1"])
yy = 500
for ln in wrap(d, "Every chart, leaderboard and number — with its source — is in the interactive dashboard. "
                  "The code and data are on GitHub so you can check or extend the analysis.", F("Regular", 36), W - 140):
    d.text((70, yy), ln, font=F("Regular", 36), fill=FG); yy += 52
d.rounded_rectangle([70, yy + 40, W - 70, yy + 150], 55, fill=C["c1"])
d.text((W / 2, yy + 95), "Links in the post ↑", font=F("Bold", 44), fill=(255, 255, 255), anchor="mm")
d.text((70, yy + 230), "Data: Billboard Hot 100 & #1 hits via TidyTuesday (Chris Dalla Riva; Sean Miller).", font=F("Regular", 24), fill=MU)
d.text((70, HH - 210), "Mohit Saini", font=F("Bold", 54), fill=FG)
d.text((70, HH - 140), "Data Analyst · open to music & media analytics roles", font=F("Medium", 30), fill=MU)
d.text((70, HH - 95), "linkedin.com/in/mohitsaini02  ·  github.com/msaini888", font=F("Medium", 26), fill=C["c5"])
slides.append(im)

assert len(slides) == TOTAL, len(slides)
slides[0].save("hit_song_carousel.pdf", save_all=True, append_images=slides[1:], resolution=150)
for i, s in enumerate(slides): s.resize((360, 450)).save(f"/tmp/claude-0/sl{i+1:02d}.png")
print("ok")
