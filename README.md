
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

Our main research question is:

**Do companies identified as AI-exposed through their sector, R&D spending, or membership in AI-related ETFs also exhibit greater stock-price sensitivity to Nvidia's earnings announcements?**

We also investigate whether this relationship has changed since the launch of ChatGPT in November 2022 and whether international market reactions reflect differences in exposure to the AI supply chain.

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

These hypotheses are evaluated using quantitative methods. Results that do not support a hypothesis are considered informative rather than treated as unsuccessful outcomes.

## 4. Data Sources

Our analysis combines financial and economic data from several publicly accessible sources.

| Source | Data Collected |
|--------|----------------|
| Yahoo Finance (`yfinance`) | Historical stock prices for Nvidia, Nasdaq-100 firms, market benchmarks, and country ETFs |
| Nvidia Investor Relations | Quarterly earnings announcement dates |
| Nasdaq-100 constituent information | Company membership and sector classifications |
| SEC EDGAR | Company financial statements, R&D expenditure, and revenue |
| ETF issuers | AI and semiconductor ETF holdings |
| World Bank | Country-level economic indicators |
| UN Comtrade | International semiconductor trade information, where available |

The main research period covers 2018–2026. Earlier price observations are used when needed to estimate pre-announcement market relationships.

Financial data are collected using Python and stored locally to support reproducibility.

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

We assess the sensitivity of our findings to several methodological choices, including:

- Alternative estimation and event windows.
- Different market benchmarks.
- Placebo announcement dates.
- Alternative specifications and sample restrictions.

These checks help evaluate whether the observed relationships are robust to changes in the analysis.

## 6. Repository Structure

The repository is organized as follows:

```text
ai-exposure-financial-markets/
│
├── config/
│   └── Configuration files and event dates
│
├── src/
│   └── Python functions for collection and analysis
│
├── tests/
│   └── Automated tests
│
├── notebook1.ipynb
├── draft1.py
├── requirements.txt
├── .gitignore
└── README.md
```

The main notebook combines explanatory text, Python code, statistical outputs, graphs, and interpretation.

Reusable functions are organized in the `src/` directory to keep the notebook readable.

Downloaded datasets and automatically generated outputs are excluded from Git when appropriate.

## 7. How to Run the Project

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

Some additional financial information, including SEC data and historical ETF holdings, requires separate collection and validation.

### Step 5 — Run the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The automated tests verify selected functions used in the data analysis.

### Step 6 — Open the Notebook

Open `notebook1.ipynb` in Visual Studio Code.

Select the Python environment created earlier and execute the notebook cells in order.

The relevant datasets must be available before running the corresponding analysis.

## 8. Reproducibility

Reproducibility is an important objective of this project.

We aim to make the analytical process transparent by documenting:

- The sources used to collect data.
- The research period and sample definition.
- The transformations applied to the original datasets.
- The assumptions underlying the statistical methods.
- The code used to generate results and visualizations.

The raw financial datasets are not included directly in the Git repository. They can be collected using the provided scripts, subject to source availability.

For exact reproduction of the final results, the data collection date and archived data snapshots should also be documented.

## 9. Limitations

Several limitations must be considered when interpreting the results.

**Limited number of events**

The number of Nvidia quarterly earnings announcements is relatively small which limits statistical precision.

**Correlation versus causation**

Companies that move alongside Nvidia are not necessarily directly exposed to AI. Their reactions may also reflect broader technology-sector or market developments.

**Survivorship bias**

Using current Nasdaq-100 constituents to study historical returns may introduce survivorship bias.

**Imperfect AI exposure indicators**

R&D spending and thematic ETF membership are useful indicators but do not provide direct measures of AI-related activity.

**Historical data availability**

ETF holdings, company characteristics, and trade indicators may not be available consistently throughout the research period.

**International market proxies**

US-listed country ETFs do not perfectly represent local equity-market reactions because trading hours, exchange rates, and fund composition can affect returns.

These limitations are considered when discussing the statistical results.


## 10. References

The project relies on publicly available financial and economic
data, as well as established methods from the academic literature.

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
- UN Comtrade: https://comtradeplus.un.org/



