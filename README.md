
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

Our results show that Nvidia's earnings announcements are associated with different stock-market reactions across firms and countries. The relationship is stronger for certain technology-related businesses but it is far from uniform.

**H1 — Firm-level sensitivity**

Of the 100 firms considered, 95 have enough observations to estimate sensitivity to Nvidia. Only 34.7% have a positive coefficient and the median sensitivity is -0.025. Some semiconductor and AI infrastructure companies stand out, including Synopsys, Monolithic Power Systems, and AMD.

**H2 — Explaining sensitivity**

The cross-sectional regression includes 57 firms and explains 29.2% of the variation in estimated Nvidia sensitivity. Technology-sector membership is positively and statistically significantly associated with sensitivity (coefficient = 0.0749, p = 0.002). However, R&D intensity and the semiconductor indicator are not individually statistically significant once the other variables are included.

**H3 — Changes after ChatGPT**

We do not find a general increase in sensitivity after November 2022. The median change is -0.020, and only 38.4% of firms show an increase. Nevertheless, several companies involved in AI hardware and semiconductor production became more sensitive to Nvidia during the later period.

**H4 — International differences**

Taiwan has the highest estimated sensitivity among the 29 country ETFs, followed by the Netherlands. These results are interesting given both countries' roles in semiconductor manufacturing. However, our analysis does not directly test whether supply-chain exposure explains these differences.

Overall, the findings suggest that being associated with artificial intelligence does not automatically mean that a company's stock price moves closely with Nvidia. Sector classification appears informative, but the relationship between observable AI exposure and financial-market sensitivity is more complex than we initially expected.

The full calculations, tables, visualizations, and interpretations are available in `notebook1.ipynb`.


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

### Step 2 — Create a Python Environment and Install Dependencies

Python 3.11 is recommended.

On Windows, run the following commands from the project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 3 — Check the input data

The repository already contains the CSV datasets used in our analysis, stored in the `data/raw/` folder. This allows the notebook to run using the same data snapshots without requiring a new download.

Before running the notebook, make sure the folder contains the required files including:

- `us_prices.csv`
- `country_etf_prices.csv`
- `nasdaq100_constituents.csv`
- `firm_labels.csv`

Additional datasets, such as the World Bank GDP data, are also included in the repository.

If you want to collect updated market data, you can run:

```powershell
.\.venv\Scripts\python.exe -m src.collect
```

Company financial information from SEC EDGAR can be collected separately using `src.firm_data`, provided a valid `SEC_USER_AGENT` contact header is configured.

**Note:** Re-collecting the data is optional. Since external financial databases can be updated, downloading new data may produce results that differ from those reported in the notebook. For reproducing our findings, we recommend using the included CSV snapshots.


### Step 4 — Run the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The automated tests verify selected functions used in the data analysis.

### Step 5 — Open the Notebook

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

The repository includes the data snapshots used in our analysis, along with the Python scripts needed to collect and process the data. This makes it possible to reproduce our reported results without downloading everything again.

We have also kept the data collection scripts so that the analysis can be updated in the future. However, running these scripts again may lead to slightly different results, as historical prices can be revised, company coverage may change, and external data providers may update their information.

For this reason, we recommend using the included datasets when reproducing our findings. The results presented in the notebook are based on these saved observations rather than continuously updated market data.

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

**Market benchmark overlap**

Both SPY and QQQ include Nvidia, so changing the market benchmark does not completely remove Nvidia's contribution to index returns. This should be considered when interpreting the sensitivity estimates.

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

