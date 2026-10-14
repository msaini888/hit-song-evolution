# How the #1 Hit Changed, 1958–2025

An analysis of 67 years of Billboard data: how hit songs, the people who write them, and the way they move up the chart have changed, and what that means for labels, publishers and A&R.

**Key findings**

| Measure | Then | Now |
|---|---|---|
| Median length of a #1 hit | 4:10 (1990s) | 3:20 (2020–25) |
| Median intro before the vocal | 20s (1990s) | 10.5s (2020–25) |
| Songwriters per #1 (excl. sample credits) | 2.0 (1980s) | 4.8 (2020–25) |
| #1s written by one person | 42% (1980s) | 5% (2020–25) |
| #1s that end with a fade-out | 71% (1980s) | 16% (2020–25) |
| Top-10 hits that debuted in the top 10 | 0% (1980s) | 68% (2020) |
| #1s from the three largest parent companies | 28% (1960s) | 87% (2010s) |

**Artists and records**

- Most #1 hits: The Beatles (20), Mariah Carey (19), Rihanna (14), Drake (13), then Michael Jackson, Taylor Swift, Madonna and The Supremes (12 each)
- Most weeks at #1: Mariah Carey (87)
- Acts from outside the US took 36% of #1s in the 1980s; the UK has produced 179 #1 hits, Canada 48
- Longest-running #1: 19 weeks, shared by *Old Town Road* (2019) and *A Bar Song (Tipsy)* (2024)
- South Asian roots at #1: Jay Sean's *Down* (2009), Zayn's *Pillowtalk* (2016), and M.I.A. featured on *Franchise* (2020)

## Data

Both datasets are public, from the [TidyTuesday](https://github.com/rfordatascience/tidytuesday) project:

- **Billboard #1 hits, 1958–2025** (TidyTuesday 2025-08-26): 1,177 songs with 100+ coded attributes (length, intro length, songwriters, producers, labels, instrumentation), compiled by Chris Dalla Riva.
- **Billboard Hot 100 weekly charts, 1958–2021** (TidyTuesday 2021-09-14): 327,895 chart rows covering 28,802 songs that debuted 1959–2020.

## How to run

```bash
pip install -r requirements.txt
mkdir raw
curl -L -o raw/2025-08-26_billboard.csv https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-08-26/billboard.csv
curl -L -o raw/2021-09-14_billboard.csv https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-09-14/billboard.csv
python analysis.py
python artists_part.py
```

Outputs go to `out/`:

- `number_ones_by_decade.csv`: song attributes of #1 hits by decade
- `hot100_by_year.csv`: chart entries, debut strength, time to peak, time on chart by year of debut
- `hot100_top10_by_decade.csv`: top-10 hits by decade
- `headlines.json`: every headline figure above

## Method notes

- Decades are by the date a song first reached #1. "2020–25" runs to the latest #1 in the data.
- Songwriter counts exclude credits that come only from samples or interpolations.
- Parent companies are as recorded in the source, with two names for the same company merged (Vivendi into Universal, TimeWarner into Warner Bros.).
- Chart dynamics use each song's first week on the Hot 100 and its best position. Songs debuting in 2020 are one year of data; time-on-chart excludes 2020 because the data ends in May 2021.
- Billboard changed its methodology several times (point-of-sale data in 1991, album cuts eligible from December 1998, downloads in 2005, on-demand streaming in 2007, YouTube in 2013). Some trends reflect those changes as much as listener behaviour. The analysis describes what changed, not why.

## Author

Mohit Saini, data analyst · [LinkedIn](https://linkedin.com/in/mohitsaini02) · [GitHub](https://github.com/msaini888)
