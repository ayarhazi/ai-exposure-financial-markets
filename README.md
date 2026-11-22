
# When Nvidia Moves, Who Follows?

### Is AI Exposure Visible on Paper or in Stock Prices?

**Python for Data Science — Final Project**

**Authors:** Estelle Aoun & Aya Rhazi  
**Academic Year:** 2026–2027  
**Research Period:** 2018–2026

---

## 1. Introduction

Artificial intelligence has become an increasingly important factor in financial markets particularly since the emergence of generative AI. Nvidia has played a central role in this development by supplying the computing infrastructure used to train and deploy AI models.

However, a company's association with artificial intelligence does not necessarily mean that its stock price reacts strongly to developments in the AI industry.

This project investigates whether firms identified as AI-exposed through observable characteristics are also those whose stock prices respond most strongly to Nvidia's quarterly earnings announcements.

We distinguish between two dimensions of AI exposure:

- **Observable exposure:** A firm's sector classification and research and development (R&D) expenditure relative to revenue. We also considered membership in thematic ETFs but suitable historical holdings data were not available for the final regression.

- **Revealed exposure:** The sensitivity of a firm's abnormal stock returns to Nvidia's abnormal returns following quarterly earnings announcements.

Our objective is to determine whether these two measures are consistent and whether similar patterns can be observed across international equity markets.

## 2. Research Question

**Do firms with stronger observable AI-related characteristics also show greater stock-price sensitivity to Nvidia's earnings announcements?**

We also ask whether these relationships changed after ChatGPT's launch on November 30, 2022, and whether the reactions of country ETFs differ in ways consistent with the geography of the AI supply chain.

## 3. Research Hypotheses

We investigate four hypotheses:

**H1 — Heterogeneous market reactions**

Stock-price reactions to Nvidia's earnings announcements differ substantially across firms with some companies displaying stronger sensitivity than others.

**H2 — AI labels and market sensitivity**

Companies with stronger observable AI-related characteristics tend to exhibit greater sensitivity to Nvidia's earnings announcements.

**H3 — The impact of ChatGPT**

The relationship between Nvidia's announcements and other companies' stock returns has become stronger since ChatGPT's public launch on November 30, 2022.

**H4 — International differences**

Countries with greater exposure to technology, semiconductors, or the AI supply chain tend to exhibit stronger equity-market reactions to Nvidia's earnings announcements.

These hypotheses are evaluated using quantitative methods. Results that do not support a hypothesis are considered equally informative.
Our analysis distinguishes statistical association from causation. The geographic evidence remains descriptive as we do not estimate a cross-country regression using verified technology weights or semiconductor trade links.

## 4. Data Sources

| Source | Role in the project |
|---|---|
| Yahoo Finance (`yfinance`) | Daily prices for Nvidia, Nasdaq-100 companies, `SPY`, `QQQ`, and 29 US-listed country ETFs |
| Nvidia Investor Relations and earnings records | Dates of Nvidia's quarterly earnings announcements, maintained in `config/earnings_nvda.csv` |
| Nasdaq-100 constituent information | Current-universe company identifiers and ICB sector labels |
| SEC EDGAR company facts | R&D expenditure and revenue used to construct the firm-level R&D ratio |
| World Bank | Economic indicators collected as contextual data; not used in a cross-country regression |

The analysis covers **36 Nvidia earnings announcements** during 2018–2026. Price histories include earlier dates where needed to estimate pre-event market relationships.

We considered thematic ETF holdings and UN Comtrade semiconductor trade data, but the final reported statistical tests do not use those variables because sufficiently verified and reproducible observations were not available.

## 5. Methodology

The analysis follows several stages.

### 5.1 Data Collection and Cleaning

We collect historical financial data and prepare the datasets for statistical analysis.

This involves:

- Checking missing and duplicated observations.
- Aligning stock prices across trading dates.
- Computing daily stock returns.
- Matching Nvidia earnings dates with the relevant trading sessions.
- Combining financial information from different sources.

Data quality checks are performed before the statistical analysis.

### 5.2 Descriptive Analysis

We explore the data using summary statistics and visualizations.

We examine the distribution of stock returns, differences across sectors, company characteristics, and initial reactions to Nvidia's earnings announcements.

### 5.3 Event Study

We conduct an event study to measure stock-market reactions around Nvidia's quarterly earnings announcements.

Expected returns are estimated using a market model based on observations preceding each announcement.

Abnormal returns are calculated as:

AR(i,t) = R(i,t) - [alpha(i) + beta(i) × R(m,t)]

Where:

- AR(i,t) is the abnormal return of stock i.
- R(i,t) is its observed return.
- R(m,t) is the market return.
- alpha(i) and beta(i) are estimated from pre-event data.

Since Nvidia generally reports earnings after the US market closes, the following trading session is treated as the main event day.

We then estimate individual firms' sensitivity to Nvidia's abnormal returns across earnings announcements.

### 5.4 Statistical Analysis

We use regression models to investigate whether differences in Nvidia sensitivity can be explained by AI-related company characteristics.

We also compare results before and after November 2022.

Principal component analysis (PCA) is used as a descriptive tool to examine patterns of co-movement in stock returns.

### 5.5 International Analysis

The international analysis examines market reactions using US-listed country ETFs as proxies for national equity markets.

We compare estimated sensitivities across countries and use geographic visualizations to identify potential differences.

Where suitable data are available, country characteristics are incorporated to explore the relationship between market sensitivity and participation in the semiconductor supply chain.


### 5.6 Robustness Checks

The notebook includes three robustness checks:
1. Re-estimating firm sensitivities using `QQQ` instead of `SPY` as the market benchmark.
2. Extending the event window from one trading day `[0]` to two trading days `[0, 1]`.
3. Comparing Nvidia's earnings-day abnormal returns with those observed on 200 randomly selected non-earnings dates.

These checks help evaluate whether the observed relationships are robust to changes in the analysis.

## 6. Main Findings

The following figures are those reported in the supplied executed notebook, they should be rechecked if the input datasets or code change.

- **H1:** Sensitivities vary considerably across firms. The notebook reports **95 estimable firms**, with a median sensitivity of **-0.025**.

- **H2:** In the regression sample of **57 firms**, the technology-sector indicator is positively associated with sensitivity, while R&D intensity is not individually statistically significant after controls. The reported model has **R² = 0.292**.

- **H3:** The median sensitivity did **not** increase across the whole firm sample after ChatGPT's release. Some AI hardware suppliers show stronger increases, but the overall change is mixed.

- **H4:** Taiwan's country ETF shows the strongest positive estimated sensitivity in the full-sample map. These patterns are descriptive and cannot establish trade-linked causality.

See `notebook1.ipynb` for the detailed outputs, visualizations, and interpretation of each hypothesis.


## 7. Repository Structure

The repository is organized as follows:

```text
ai-exposure-financial-markets/
│
├── config/
│   └── Configuration files and event dates
│
├── src/
│   └── Python functions for data collection, analysis and visualization
│
├── tests/
│   └── Automated tests
│
├── notebook1.ipynb
├── requirements.txt
├── .gitignore
└── README.md
```

The main notebook combines explanatory text, Python code, statistical outputs, graphs, and interpretation.

Reusable functions are organized in the `src/` directory to keep the notebook readable.

Downloaded datasets and automatically generated outputs are excluded from Git when appropriate.

## 8. How to Run the Project

The project is developed in Python using Visual Studio Code and Jupyter Notebook.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ayarhazi/ai-exposure-financial-markets.git
cd ai-exposure-financial-markets
```

### Step 2 — Create a Python Environment

Python 3.11 is recommended.

On Windows:

```powershell
py -3.11 -m venv .venv
```

### Step 3 — Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The project uses libraries including:

- NumPy
- Pandas
- Matplotlib
- SciPy
- Statsmodels
- Scikit-learn
- Plotly
- yfinance
- Requests

### Step 4 — Collect Market Data

```powershell
.\.venv\Scripts\python.exe -m src.collect
```

This command collects the initial historical price and economic datasets.

The downloaded files are saved locally under `data/raw/`.

Company financial information, including R&D expenditure and revenue from SEC filings, can be collected separately using `src.firm_data`.

### Step 5 — Run the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The automated tests verify selected functions used in the data analysis.

### Step 6 — Open the Notebook

Open `notebook1.ipynb` in Visual Studio Code.

Select the Python environment created earlier and execute the notebook cells in order.

The relevant datasets must be available before running the corresponding analysis.

## 9. Reproducibility

Reproducibility is an important objective of this project.

We aim to make the analytical process transparent by documenting:

- The sources used to collect data.
- The research period and sample definition.
- The transformations applied to the original datasets.
- The assumptions underlying the statistical methods.
- The code used to generate results and visualizations.

The raw financial datasets are not included directly in the Git repository. They can be collected using the provided scripts, subject to source availability.

For exact reproduction of the final results, the data collection date and archived data snapshots should also be documented.

## 10. Limitations

Several limitations must be considered when interpreting the results.

**Limited number of events**

The number of Nvidia quarterly earnings announcements is relatively small, which limits statistical precision.

**Correlation versus causation**

Companies that move alongside Nvidia are not necessarily directly exposed to AI. Their reactions may also reflect broader technology-sector or market developments.

**Survivorship bias**

Using current Nasdaq-100 constituents to study historical returns may introduce survivorship bias.

**Imperfect AI exposure indicators**

R&D spending and sector classification are useful indicators but do not provide direct measures of AI-related activity.

**Historical data availability**

Company financial characteristics and historical index composition may not be available consistently throughout the research period. Historical AI-themed ETF holdings were not included in the final regression.

**International market proxies**

US-listed country ETFs do not perfectly represent local equity-market reactions because trading hours, exchange rates, and fund composition can affect returns.

The geographic analysis is descriptive and does not establish a causal relationship between semiconductor trade links and stock-market sensitivity.

These limitations are considered when discussing the statistical results.

## 11. References

The project relies on publicly available financial and economic data, as well as established methods from the academic literature.

### Academic Literature

- MacKinlay, A. C. (1997). Event Studies in Economics and Finance.
  Journal of Economic Literature, 35(1), 13–39.
  https://www.jstor.org/stable/2729691

- Eisfeldt, A. L., Schubert, G., & Zhang, M. B. (2023).
  Generative AI and Firm Values.
  NBER Working Paper No. 31222.
  https://www.nber.org/papers/w31222

### Data Sources

- Nvidia Investor Relations: https://investor.nvidia.com/
- Yahoo Finance: https://finance.yahoo.com/
- SEC EDGAR: https://www.sec.gov/edgar
- World Bank Open Data: https://data.worldbank.org/

## 12. Authors

**Estelle Aoun & Aya Rhazi**

Python for Data Science — Final Project  
Academic Year 2026–2027

