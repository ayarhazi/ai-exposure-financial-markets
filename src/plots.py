"""Functions for plotting and comparing the results of our Nvidia analysis"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

def plot_nvda_reactions(event_results: pd.DataFrame, output: Path) -> None:
    nvidia = event_results.loc[event_results.ticker.eq("NVDA")].sort_values("announcement_date")
    fig, ax = plt.subplots(figsize=(11, 4))
    colors = ["#21867a" if v >= 0 else "#bb5960" for v in nvidia.abnormal_return]
    ax.bar(nvidia.announcement_date.dt.strftime("%Y-%m"), 100 * nvidia.abnormal_return, color=colors)
    ax.axhline(0, lw=0.8, color="black")
    ax.set_ylabel("Nvidia abnormal return (%)")
    ax.set_xlabel("Earnings announcement month")
    ax.set_title("Nvidia's next-session abnormal returns after earnings")
    ax.tick_params(axis="x", rotation=80, labelsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_sensitivity_distribution(sensitivity: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(sensitivity.sensitivity, bins=20, edgecolor="white", alpha=0.85)
    ax.axvline(0, color="black", lw=1, ls="--")
    ax.set(xlabel="Sensitivity to Nvidia (slope of event abnormal returns)",
           ylabel="Number of stocks", title="How unevenly do stocks follow Nvidia?")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_pre_post(slopes: pd.DataFrame, output: Path) -> None:
    pivot = slopes.pivot(index="ticker", columns="period", values="sensitivity").dropna()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(pivot["Pre"], pivot["Post"], s=25, alpha=0.7)
    lo = min(pivot.min().min(), 0)
    hi = max(pivot.max().max(), 0)
    ax.plot([lo, hi], [lo, hi], color="black", ls="--", lw=1, label="No change")
    ax.set(xlabel="Before 30 Nov 2022", ylabel="After 30 Nov 2022",
           title="Did firm sensitivity change after ChatGPT?")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_pca(pca: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(pca.year, 100 * pca.pc1_variance_share, marker="o")
    ax.set(xlabel="Calendar year", ylabel="Variance explained by PC1 (%)",
           title="Common movement across Nasdaq-100 stocks")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_country_map(country_slopes: pd.DataFrame, countries: pd.DataFrame, output: Path) -> None:
    data = country_slopes.merge(countries, left_on="ticker", right_on="etf", validate="many_to_one")
    fig = px.choropleth(data, locations="iso3", color="sensitivity", hover_name="country",
                        hover_data={"n_events": True, "ticker": True},
                        color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
                        projection="natural earth",
                        title="US-listed country ETFs: sensitivity to Nvidia earnings")
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    # Self-contained HTML: an internet connection is not required to view it.
    fig.write_html(str(output), include_plotlyjs=True, full_html=True)


def plot_country_two_periods(country_period_slopes: pd.DataFrame, countries: pd.DataFrame,
                            output: Path) -> None:
    data = country_period_slopes.merge(countries, left_on="ticker", right_on="etf", validate="many_to_one")
    if data.empty:
        return
    maximum = max(0.1, float(data.sensitivity.abs().max()))
    fig = px.choropleth(data, locations="iso3", color="sensitivity", hover_name="country",
                        animation_frame="period", category_orders={"period": ["Pre", "Post"]},
                        color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
                        range_color=[-maximum, maximum],
                        title="Country ETF exposure before and after 30 November 2022",
                        projection="natural earth")
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    fig.write_html(str(output), include_plotlyjs=True, full_html=True)

def show_figure(fig, path):
    """Save a Plotly figure as PNG, or display it if export is unavailable."""
    from IPython.display import Image, display

    try:
        fig.write_image(str(path), scale=2)
        display(Image(filename=str(path)))
    except Exception as error:
        print(f"PNG export unavailable: {type(error).__name__}")
        display(fig)
