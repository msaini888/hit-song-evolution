"""How the #1 hit changed, 1958-2025.
Reproducible analysis of two public datasets (TidyTuesday):
  - Billboard #1 hits 1958-2025 with song attributes (TidyTuesday 2025-08-26, from Chris Dalla Riva)
  - Billboard Hot 100 weekly charts 1958-2021 (TidyTuesday 2021-09-14, from Data.World / Sean Miller)
Run: python analysis.py   -> writes out/*.csv and out/headlines.json
"""
import json, os
import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "raw")
OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

# ---------- 1. #1 hits ----------
n1 = pd.read_csv(f"{RAW}/2025-08-26_billboard.csv")
n1["year"] = pd.to_datetime(n1["date"]).dt.year
n1["decade"] = (n1["year"] // 10 * 10).astype(int)
count = lambda s: len([x for x in str(s).split(";") if x.strip()]) if pd.notna(s) else 0
# songwriters excluding credits that come only from samples/interpolations
n1["n_writers"] = n1["songwriters_w_o_interpolation_sample_credits"].apply(count)
n1["n_producers"] = n1["producers"].apply(count)
n1["has_feature"] = n1["featured_artists"].notna().astype(int)
# same corporate parent recorded under two names in the source
alias = {"Vivendi": "Universal", "TimeWarner": "Warner Bros."}
n1["parent_group"] = n1["parent_label"].replace(alias)

dec = n1.groupby("decade").agg(
    songs=("song", "size"),
    median_length_sec=("length_sec", "median"),
    median_intro_sec=("intro_length_sec", "median"),
    share_intro_le_5s=("intro_length_sec", lambda s: (s <= 5).mean()),
    avg_songwriters=("n_writers", "mean"),
    share_solo_writer=("n_writers", lambda s: (s == 1).mean()),
    avg_producers=("n_producers", "mean"),
    share_featured_artist=("has_feature", "mean"),
    share_fade_out=("fade_out", "mean"),
    share_explicit=("explicit", "mean"),
    share_artist_cowrote=("artist_is_a_songwriter", "mean"),
    avg_weeks_at_1=("weeks_at_number_one", "mean"),
).reset_index()


def top3(g):
    v = g["parent_group"].value_counts(normalize=True)
    return pd.Series({"top3_parent_share": v.head(3).sum(),
                      "top3_parents": " / ".join(v.head(3).index),
                      "distinct_parents": g["parent_group"].nunique()})


lab = n1.groupby("decade").apply(top3, include_groups=False).reset_index()
dec = dec.merge(lab, on="decade")
dec["decade_label"] = dec["decade"].astype(str) + "s"
dec.loc[dec.decade == 1950, "decade_label"] = "1958–59"
dec.loc[dec.decade == 2020, "decade_label"] = "2020–25"
dec.round(4).to_csv(f"{OUT}/number_ones_by_decade.csv", index=False)

# ---------- 2. Hot 100 chart dynamics ----------
h = pd.read_csv(f"{RAW}/2021-09-14_billboard.csv")
h["wk"] = pd.to_datetime(h["week_id"], format="%m/%d/%Y")
h = h.sort_values("wk")
g = h.groupby("song_id")
songs = pd.DataFrame({
    "debut_wk": g["wk"].min(),
    "debut_pos": g["week_position"].first(),
    "peak": g["week_position"].min(),
    "weeks_on_chart": g.size(),
})
peak_wk = h.loc[g["week_position"].idxmin()].set_index("song_id")["wk"]
songs["weeks_to_peak"] = ((peak_wk - songs["debut_wk"]).dt.days / 7).round()
songs["year"] = songs["debut_wk"].dt.year
# 1958 is a partial year; 2021 debuts are cut off by the end of the data
songs = songs[(songs.year >= 1959) & (songs.year <= 2020)]

yr = songs.groupby("year").agg(new_songs=("peak", "size")).reset_index()
t10 = songs[songs.peak <= 10]
yr = yr.merge(t10.groupby("year").agg(
    top10_hits=("peak", "size"),
    top10_debuting_in_top10=("debut_pos", lambda s: (s <= 10).mean()),
    top10_median_weeks_to_peak=("weeks_to_peak", "median"),
).reset_index(), on="year")
# weeks on chart is truncated for songs debuting near the end of the data
full = songs[songs.year <= 2019]
yr = yr.merge(full.groupby("year").agg(median_weeks_on_chart=("weeks_on_chart", "median")).reset_index(),
              on="year", how="left")
yr.round(4).to_csv(f"{OUT}/hot100_by_year.csv", index=False)

t10dec = t10.assign(decade=t10.year // 10 * 10).groupby("decade").agg(
    top10_hits=("peak", "size"),
    share_debut_in_top10=("debut_pos", lambda s: (s <= 10).mean()),
    median_weeks_to_peak=("weeks_to_peak", "median"),
).reset_index()
t10dec.round(4).to_csv(f"{OUT}/hot100_top10_by_decade.csv", index=False)

# ---------- headlines ----------
D = dec.set_index("decade")
Y = yr.set_index("year")
H = {
    "n_number_ones": int(len(n1)),
    "n_hot100_songs": int(len(songs)),
    "n_hot100_rows": int(len(h)),
    "length_1990s_sec": float(D.loc[1990, "median_length_sec"]),
    "length_2020s_sec": float(D.loc[2020, "median_length_sec"]),
    "intro_1990s_sec": float(D.loc[1990, "median_intro_sec"]),
    "intro_2020s_sec": float(D.loc[2020, "median_intro_sec"]),
    "intro_le5_1980s": float(D.loc[1980, "share_intro_le_5s"]),
    "intro_le5_2020s": float(D.loc[2020, "share_intro_le_5s"]),
    "writers_1980s": float(D.loc[1980, "avg_songwriters"]),
    "writers_2020s": float(D.loc[2020, "avg_songwriters"]),
    "solo_1980s": float(D.loc[1980, "share_solo_writer"]),
    "solo_2020s": float(D.loc[2020, "share_solo_writer"]),
    "fade_1980s": float(D.loc[1980, "share_fade_out"]),
    "fade_2020s": float(D.loc[2020, "share_fade_out"]),
    "explicit_1980s": float(D.loc[1980, "share_explicit"]),
    "explicit_2020s": float(D.loc[2020, "share_explicit"]),
    "top3_1960s": float(D.loc[1960, "top3_parent_share"]),
    "top3_2010s": float(D.loc[2010, "top3_parent_share"]),
    "top10_debut_1980s": float(t10dec.set_index("decade").loc[1980, "share_debut_in_top10"]),
    "top10_debut_2010s": float(t10dec.set_index("decade").loc[2010, "share_debut_in_top10"]),
    "top10_debut_2020": float(Y.loc[2020, "top10_debuting_in_top10"]),
    "top10_hits_2020": int(Y.loc[2020, "top10_hits"]),
    "weeks_to_peak_1980s": float(t10dec.set_index("decade").loc[1980, "median_weeks_to_peak"]),
    "weeks_to_peak_2020": float(Y.loc[2020, "top10_median_weeks_to_peak"]),
    "new_songs_min_year": int(yr.loc[yr.new_songs.idxmin(), "year"]),
    "new_songs_min": int(yr.new_songs.min()),
    "new_songs_2020": int(Y.loc[2020, "new_songs"]),
    "new_songs_1966": int(Y.loc[1966, "new_songs"]),
}
json.dump(H, open(f"{OUT}/headlines.json", "w"), indent=1)
print(json.dumps(H, indent=1))
