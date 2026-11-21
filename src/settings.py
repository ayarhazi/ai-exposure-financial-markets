"""One place for paths and research settings."""
from dataclasses import dataclass
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "outputs" / "figures"
CONFIG = ROOT / "config"

@dataclass(frozen=True)
class Settings:
    # 2017 is a burn-in: the first 2018 earnings need ~250 pre-event days.
    price_start: str = "2017-01-01"
    # Fixed historical cutoff, with the end date exclusive in yfinance.
    price_end: str = "2026-11-21"
    cutoff_chatgpt: str = "2022-11-30"
    estimation_start: int = -250
    estimation_end: int = -30
    min_estimation_days: int = 145
    min_events_per_slope: int = 8
    benchmark: str = "SPY"
    alternative_benchmark: str = "QQQ"
    seed: int = 42
