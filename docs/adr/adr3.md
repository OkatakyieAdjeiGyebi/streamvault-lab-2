# ADR-003: Evaluate historical financial performance using two time windows and multiple financial measures

**Status:** Accepted, subject to modern-cohort reconciliation  
**Date:** 20 November 2026  
**Deciders:** Project team

## Context

Kwame needs evidence to decide whether StreamVault should prioritise franchise bundles or standalone films.

TMDb provides historical movie information, including:

- Production budgets.
- Worldwide box-office revenue.
- Audience ratings.
- Audience vote counts.
- Release dates.

However, the analysis does not have access to actual StreamVault licensing prices, streaming revenue or contractual acquisition costs.

Yaw in Finance has also raised concerns about pre-2000 films because of inflation, currency reporting and historical box-office reporting differences.

Using all available historical data without a separate modern comparison could leave the recommendation vulnerable to Finance's objections.

Using only modern films would remove useful historical evidence and reduce the available sample.

## Decision

Use historical production budgets and worldwide box-office revenue as comparative indicators of historical commercial performance.

Calculate the following measures:

| Measure | Calculation |
|---|---|
| Estimated profit | Revenue − Budget |
| ROI | (Profit / Budget) × 100 |
| Revenue-budget multiple | Revenue / Budget |
| Average rating | Mean TMDb vote average |
| Total votes | Sum of TMDb vote counts |

For franchise acquisition units, aggregate the budgets and revenues of their distinct candidate films before calculating financial indicators.

For standalone acquisitions, calculate the same measures using the individual film.

Present two historical windows:

1. **All years:** All eligible films with available financial information.
2. **2000 onward:** Films released in 2000 or later.

The 2000 cutoff is a practical analytical boundary chosen to address Finance's concerns. It is not proof that financial reporting became completely consistent after that date.

### Cohort construction rule

The modern comparison must use a consistent movie-level cohort.

The correct process is:

1. Filter distinct movies to release years of 2000 or later.
2. Rebuild franchise and standalone acquisition units using that filtered population.
3. Calculate the financial measures for those units.
4. Compare the resulting franchise and standalone populations.

A mixed-period franchise must not silently contribute pre-2000 financial results to the modern comparison.

This distinction is particularly important because a franchise can contain films released both before and after 2000.

### Comparison results currently reported

**All-years comparison**

| Measure | Franchise | Standalone |
|---|---:|---:|
| Acquisition units | 23 | 25 |
| Movies | 87 | 25 |
| Average profit per unit | $2.092B | $275.6M |
| Median profit per unit | $1.817B | $253.7M |
| Average ROI | 497.46% | 947.99% |
| Median ROI | 455.11% | 400.00% |
| Average revenue-budget multiple | 5.97x | 10.48x |
| Median revenue-budget multiple | 5.55x | 5.00x |
| Average rating | 7.45 | 8.10 |

**2000-onward comparison — previously reported results**

| Measure | Franchise | Standalone |
|---|---:|---:|
| Acquisition units | 12 | 12 |
| Movies | 44 | 12 |
| Average profit per unit | $2.598B | $325.4M |
| Median profit per unit | $2.035B | $298.6M |
| Average ROI | 471.51% | 389.36% |
| Median ROI | 408.13% | 348.80% |
| Average revenue-budget multiple | 5.72x | 4.89x |
| Median revenue-budget multiple | 5.08x | 4.49x |
| Average rating | 7.52 | 7.92 |

These figures are retained as the reported comparison results, but the modern population requires a final reconciliation before the results can be treated as fully validated.

### Important reconciliation issue

The notebook also reports:

- `modern_movies`: 71 records.
- Modern acquisition-unit counts in one analysis: 17 franchises and 12 standalones.
- Another modern comparison: 12 franchises and 12 standalones, representing 44 franchise films and 12 standalone films.

These outputs do not describe an obviously identical population.

The difference must be investigated by checking:

- The exact movie-level filtering applied.
- Whether missing financial values were excluded.
- Whether acquisition units were rebuilt after filtering.
- Whether mixed-period franchises were included.
- Whether different intermediate datasets were used.

Until this is resolved, the 12-franchise/12-standalone comparison should be identified as a reported result rather than silently presented as a fully reconciled final population.

The all-years comparison remains separately reported.

## Alternatives considered

**Use only all-years financial results**

Rejected because it would not adequately address Finance's concerns about historical financial reporting.

**Use only films released from 2000 onward**

Rejected because it would discard historical evidence that helps explain overall acquisition performance.

**Adjust historical figures for inflation**

Not adopted because a verified inflation-adjustment methodology and consistent financial data were not established within the current analysis.

**Use ROI as the only financial measure**

Rejected because percentage returns can favour low-budget films without representing their absolute financial contribution.

**Use audience ratings as the primary acquisition measure**

Rejected because audience reception does not directly establish commercial profitability.

**Use historical revenue instead of profit**

Rejected because revenue alone does not account for production expenditure.

## Consequences

The results reveal an important difference between the two historical windows.

### Across all years

- Standalone films have higher average ROI: 947.99% against 497.46%.
- Standalone films have higher average revenue-budget multiples: 10.48x against 5.97x.
- Standalone films receive higher average audience ratings: 8.10 against 7.45.
- Franchises generate substantially higher average profit per acquisition unit.

### From 2000 onward

Under the previously reported comparison:

- Franchises generate approximately $2.598 billion in average profit per unit, compared with $325.4 million for standalones.
- Franchise ROI is 471.51%, compared with 389.36%.
- Franchise revenue-budget multiples are also higher.
- Standalone films retain the higher average audience rating.

The recommendation is therefore sensitive to the historical window.

The evidence supports prioritising strong modern franchise opportunities while retaining exceptional standalone titles as selective acquisitions.

However, this is a historical performance comparison, not a direct estimate of StreamVault's expected financial return.

### Limitations

- Historical profit is not equivalent to StreamVault's expected streaming profit.
- Historical figures are not adjusted for inflation.
- Budget and revenue reporting may contain inconsistencies.
- The 2000 cutoff is an analytical boundary, not a guarantee of financial comparability.
- Acquisition units differ in size.
- Franchise profitability may be driven by a small number of exceptional films.
- The absence of actual licensing costs prevents a definitive assessment of acquisition affordability.

## What survives the next rerun?

The financial calculations and two-window comparison are reusable for the expected 500-title candidate list.

Adjoa should be able to regenerate:

- Movie-level financial indicators.
- Franchise-level aggregate indicators.
- Standalone financial indicators.
- Average and median performance measures.
- All-years comparisons.
- 2000-onward comparisons.
- Audience ratings and vote-count comparisons.

The cutoff year and financial calculations must remain documented and configurable.

The original API financial data should be retained so that future inflation adjustments or alternative financial calculations can be performed without repeating the entire extraction.

## Revisit when

- Finance provides an agreed inflation-adjustment methodology.
- More reliable financial information becomes available.
- Actual StreamVault licensing fees are collected.
- Streaming performance data becomes available.
- The modern cohort reconciliation is completed.
- The business requires a direct comparison of expected streaming returns rather than historical theatrical performance.

---