"""Part 2: artist leaderboards, international reach, records, South Asian connections."""
import re, json, os
import pandas as pd
RAW, OUT = "raw", "out"

n1 = pd.read_csv(f"{RAW}/2025-08-26_billboard.csv")
n1["year"] = n1["date"].str[:4].astype(int)
n1["decade"] = n1["year"] // 10 * 10


def split_credit(artist):
    parts = re.split(r" ft\. ", artist)
    lead, feat = parts[0], (parts[1] if len(parts) > 1 else "")
    feats = [x.strip() for x in re.split(r", | & ", feat) if x.strip()]
    return lead.strip(), feats


leads = n1["artist"].apply(lambda a: split_credit(a)[0])
known = set(leads) | {f for a in n1["artist"] for f in split_credit(a)[1]}


def credits(artist):
    lead, feats = split_credit(artist)
    pieces = [p.strip() for p in lead.split(" & ")]
    # split a joint lead credit only when every piece is an act in its own right elsewhere
    lead_names = pieces if len(pieces) > 1 and all(p in known for p in pieces) else [lead]
    return lead_names, feats


rows = []
for _, r in n1.iterrows():
    L, F = credits(r["artist"])
    origin = str(r["artist_place_of_origin"]).split(";")
    for name in L:
        rows.append(dict(artist=name, role="lead", weeks=r["weeks_at_number_one"], year=r["year"]))
    for name in F:
        rows.append(dict(artist=name, role="featured", weeks=r["weeks_at_number_one"], year=r["year"]))
cr = pd.DataFrame(rows)
board = cr.groupby("artist").agg(number_ones=("role", "size"),
                                 as_lead=("role", lambda s: (s == "lead").sum()),
                                 weeks_at_1=("weeks", "sum"),
                                 first_year=("year", "min"), last_year=("year", "max")).reset_index()

# origin for solo-lead acts, from rows where they are the only lead
orig = {}
for _, r in n1.iterrows():
    L, _ = credits(r["artist"])
    if len(L) == 1 and pd.notna(r["artist_place_of_origin"]) and ";" not in r["artist_place_of_origin"]:
        orig.setdefault(L[0], r["artist_place_of_origin"])
board["origin"] = board["artist"].map(orig)
board = board.sort_values(["number_ones", "weeks_at_1"], ascending=False)
board["span_years"] = board["last_year"] - board["first_year"]
top = board.head(15).copy()
top["rank"] = range(1, len(top) + 1)
top.to_csv(f"{OUT}/artists_most_number_ones.csv", index=False)
wk = board.sort_values(["weeks_at_1", "number_ones"], ascending=False).head(10).copy()
wk["rank"] = range(1, len(wk) + 1)
wk.to_csv(f"{OUT}/artists_most_weeks_at_1.csv", index=False)

# international: #1 hits by artists from outside the US (origin field has no "United States")
n1["non_us"] = ~n1["artist_place_of_origin"].fillna("").str.contains("United States")
intl_dec = n1.groupby("decade").agg(number_ones=("song", "size"), non_us=("non_us", "sum")).reset_index()
intl_dec["share_non_us"] = intl_dec["non_us"] / intl_dec["number_ones"]
lab = {1950: "1958–59", 2020: "2020–25"}
intl_dec["decade_label"] = intl_dec["decade"].map(lambda d: lab.get(d, f"{d}s"))
intl_dec.round(4).to_csv(f"{OUT}/international_by_decade.csv", index=False)

c = n1[n1.non_us].assign(country=n1["artist_place_of_origin"].str.split(";")).explode("country")
countries = c.groupby("country").size().reset_index(name="number_ones").sort_values("number_ones", ascending=False)
countries.head(12).to_csv(f"{OUT}/countries_number_ones.csv", index=False)

intl_board = board[board["origin"].notna() & (board["origin"] != "United States")].head(10).copy()
intl_board["rank"] = range(1, len(intl_board) + 1)
intl_board.to_csv(f"{OUT}/artists_international.csv", index=False)
us_board = board[board["origin"] == "United States"].head(10).copy()
us_board["rank"] = range(1, len(us_board) + 1)
us_board.to_csv(f"{OUT}/artists_us.csv", index=False)

# records
h = pd.read_csv(f"{RAW}/2021-09-14_billboard.csv")
h["wk"] = pd.to_datetime(h["week_id"], format="%m/%d/%Y")
rec = []
t = n1.sort_values(["weeks_at_number_one", "year"], ascending=[False, False]).iloc[0]
ties = n1[(n1.weeks_at_number_one == t.weeks_at_number_one) & (n1.song != t.song)]
rec.append(dict(record="Longest run at #1", song=t.song, artist=t.artist, year=int(t.year),
                value=int(t.weeks_at_number_one), unit="weeks",
                note="; ".join(f"tied with {r.song} ({r.artist}, {r.year})" for r in ties.itertuples())))
j = h[h.week_position == 1].copy()
j["jump"] = j["previous_week_position"] - 1
t = j.sort_values("jump", ascending=False).iloc[0]
rec.append(dict(record="Biggest leap to #1", song=t.song, artist=t.performer, year=int(t.wk.year),
                value=int(t.previous_week_position), unit="from position"))
w = h.groupby(["song", "performer"]).agg(weeks=("wk", "size"), y=("wk", "min")).reset_index().sort_values("weeks").iloc[-1]
rec.append(dict(record="Longest Hot 100 run (to May 2021)", song=w.song, artist=w.performer, year=int(w.y.year),
                value=int(w.weeks), unit="weeks"))
a = n1.dropna(subset=["front_person_age"])
t = a.sort_values("front_person_age").iloc[0]
rec.append(dict(record="Youngest lead singer at #1", song=t.song, artist=t.artist, year=int(t.year),
                value=int(t.front_person_age), unit="years old", note="Michael Jackson, on three 1970 #1s"))
t = a.sort_values("front_person_age").iloc[-1]
rec.append(dict(record="Oldest lead singer at #1", song=t.song, artist=t.artist, year=int(t.year),
                value=int(t.front_person_age), unit="years old", note="a 1958 recording that first reached #1 in 2023"))
lng = board.sort_values("span_years", ascending=False).iloc[0]
rec.append(dict(record="Longest span between first and latest #1", song="", artist=lng.artist,
                year=int(lng.last_year), value=int(lng.span_years), unit="years",
                note=f"first #1 in {int(lng.first_year)}, latest in {int(lng.last_year)}"))
pd.DataFrame(rec).to_csv(f"{OUT}/records.csv", index=False)

# South Asian connections: curated list of acts with South Asian roots, chart facts from the data
ROOTS = {
    "Jay Sean": "British singer of Indian Punjabi heritage",
    "A R Rahman": "Indian composer (Slumdog Millionaire)",
    "Panjabi MC": "British bhangra producer of Indian Punjabi heritage",
    "M.I.A.": "British rapper of Sri Lankan Tamil heritage",
    "Norah Jones": "American singer, daughter of Ravi Shankar",
    "Zayn": "British singer of Pakistani heritage",
}
rows = []
for key, note in ROOTS.items():
    m = h[h.performer.str.contains(re.escape(key), regex=True)]
    for (song, perf), g in m.groupby(["song", "performer"]):
        rows.append(dict(act=key, song=song, performer=perf, peak=int(g.peak_position.min()),
                         weeks=int(len(g)), year=int(g.wk.min().year), roots=note))
sa = pd.DataFrame(rows).sort_values(["peak", "weeks"], ascending=[True, False])
sa = sa[sa.peak <= 40].reset_index(drop=True)
sa.to_csv(f"{OUT}/south_asian_roots.csv", index=False)
# Indian sounds and places on #1 hits
ind = pd.concat([
    n1[n1.sitar == 1][["song", "artist", "year"]].assign(link="Features a sitar"),
    n1[n1.song.str.contains("Calcutta", na=False)][["song", "artist", "year"]].assign(link="Named after Calcutta (Kolkata)"),
]).sort_values("year")
ind.to_csv(f"{OUT}/india_on_number_ones.csv", index=False)

print(top[["rank", "artist", "number_ones", "as_lead", "weeks_at_1", "origin", "first_year", "last_year"]].to_string(index=False))
print(wk[["artist", "weeks_at_1", "number_ones"]].to_string(index=False))
print(intl_dec.to_string(index=False)); print(countries.head(10).to_string(index=False))
print(intl_board[["artist", "number_ones", "origin"]].to_string(index=False))
print(us_board[["artist", "number_ones"]].to_string(index=False))
print(pd.DataFrame(rec).to_string(index=False)); print(sa.to_string(index=False)); print(ind.to_string(index=False))
