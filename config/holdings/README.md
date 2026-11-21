# ETF holdings snapshots

Save issuer holdings here as dated CSV snapshots. Use the naming convention:
`BOTZ_2026-11-20.csv`, `SOXX_2026-11-20.csv`, `ARTY_2026-11-20.csv`.
The script reads a column named `Ticker`, `Symbol`, or `Ticker Symbol` (case-insensitive).
The files must contain **actual issuer data**, never a hand-guessed membership list.
If no issuer file is supplied, ETF membership remains **missing** (NaN), not zero.

Official holdings pages:
- https://www.globalxetfs.com/funds/botz/
- https://www.ishares.com/us/products/239705/ishares-semiconductor-etf-soxx
- https://www.ishares.com/us/products/297905/ishares-future-ai-tech-etf-arty

Important: a November 2026 holdings snapshot is NOT historical membership in 2018.
The analysis calls this a **current-label association** and never a causal or ex-ante test.
