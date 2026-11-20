



# ADR-004: Rank acquisition opportunities using transparent percentile-based scoring and analyse talent by credited role

**Status:** Accepted, with talent conclusions limited to the analysed sample  
**Date:** 20 November 2026  
**Deciders:** Project team

## Context

Kwame requires a shortlist of three strong franchise opportunities and five strong standalone opportunities.

A single undifferentiated ranking could favour one acquisition structure because franchises contain multiple films while standalones contain one.

Financial performance alone also does not capture audience reception or the level of audience participation behind a rating.

Profit and revenue-budget multiples have highly skewed distributions. A few unusually successful titles could dominate a ranking if raw financial values were combined without normalisation.

The project also requires an assessment of directors and lead actors who repeatedly appear across commercially successful candidate films.

TMDb provides:

- Cast order.
- Actor identifiers.
- Actor names.
- Crew departments.
- Crew job titles.
- Person identifiers.

These fields make it possible to distinguish leading cast members and credited directors from other personnel.

The notebook contains:

| Dataset | Records | Columns |
|---|---:|---:|
| Movies | 119 | 17 |
| Cast | 8,407 | 7 |
| Crew | 25,957 | 7 |
| Unique movies | 112 | 17 |

The talent analysis must use distinct movie identities and must not confuse repeated cast or crew records with additional films.

## Decision

Use percentile-based scoring to rank acquisition opportunities.

Calculate five component scores:

1. **Profit score:** Percentile ranking of total estimated profit.
2. **Financial efficiency score:** Percentile ranking of revenue-budget multiple.
3. **Rating score:** Percentile ranking of average audience rating.
4. **Popularity score:** Percentile ranking of total audience votes.
5. **Content breadth score:** Percentile ranking of distinct film count within an acquisition unit.

### Core score

Use the following weighting:

| Component | Weight |
|---|---:|
| Profit score | 30% |
| Financial efficiency score | 30% |
| Rating score | 20% |
| Popularity score | 20% |
| **Total** | **100%** |

The core score excludes movie count so that larger franchises do not automatically receive higher underlying attractiveness scores.

### Portfolio score

Calculate a separate portfolio score:

`Portfolio Score = (0.90 × Core Score) + (0.10 × Content Breadth Score)`

The portfolio score recognises the additional content breadth of a franchise without allowing size to dominate the core assessment.

Rank franchise and standalone opportunities separately.

The notebook should retain the following fields in its final ranking:

- `collection_name`
- `acquisition_type`
- `movie_count`
- `total_profit`
- `roi_pct`
- `average_rating`
- `core_score`
- `portfolio_score`
- `type_rank`

The precise percentile calculation, ranking population, tie handling and treatment of missing values must remain documented in the implementation. The same method must be applied consistently in quarterly reruns.

### Shortlist selection

For the modern acquisition recommendation, select:

- The three highest-ranked franchise opportunities.
- The five highest-ranked standalone opportunities.

The reported modern franchise shortlist is:

| Rank | Opportunity | Movies | Profit | ROI | Core score |
|---:|---|---:|---:|---:|---:|
| 1 | The Lord of the Rings Collection | 3 | $2.651B | 996.45% | 91.72 |
| 2 | The Avengers Collection | 4 | $6.808B | 612.81% | 89.31 |
| 3 | Harry Potter Collection | 8 | $6.480B | 506.23% | 83.79 |

The reported modern standalone shortlist is:

| Rank | Film | Profit | ROI | Rating | Core score |
|---:|---|---:|---:|---:|---:|
| 1 | Inception | $679.0M | 424.39% | 8.37 | 65.86 |
| 2 | Interstellar | $581.6M | 352.49% | 8.50 | 62.76 |
| 3 | Spirited Away | $255.9M | 1,346.97% | 8.54 | 61.03 |
| 4 | The Incredibles | $539.4M | 586.35% | 7.73 | 54.14 |
| 5 | Monsters, Inc. | $520.0M | 400.00% | 7.86 | 46.90 |

These rankings are the reported outputs of the modern scoring analysis and must be regenerated after the modern cohort reconciliation described in ADR-003.

The all-years rankings must remain available as a separate analysis. They must not be substituted for the modern shortlist without clearly identifying the change in historical window.

## Talent analysis

Talent analysis is an additional supporting assessment, not a replacement for the acquisition scoring model.

The objective is to identify people whose repeated involvement in commercially successful and well-rated films may provide useful negotiation signals.

### Lead actors

Use cast order as a consistent proxy for leading roles.

Apply the following procedure:

1. Sort cast credits by `cast_order`.
2. Select the first five credited actors for each selected film.
3. Identify actors using `actor_id`, rather than names alone.
4. Count distinct films associated with each actor.
5. Count distinct acquisition units associated with each actor.
6. Examine the financial performance and audience reception of their associated films.

The first five credited actors are a practical proxy for leading cast members. They are not guaranteed to be the actual principal performers in every film.

### Directors

Identify directors through the crew records.

Use:

- `department = Directing`
- `job = Director`

Identify individuals using `person_id`.

Do not classify every crew member in the Directing department as a director. The actual job must also match.

Calculate:

- Distinct films directed.
- Distinct acquisition units represented.
- Associated film profit.
- Associated film ROI.
- Associated audience ratings.

### Interpreting talent frequency

Frequency alone is insufficient.

An individual appearing in several films is not automatically a reliable signal of licensing value.

Talent rankings should therefore consider:

- Number of distinct films.
- Number of acquisition units.
- Associated commercial performance.
- Associated audience reception.

Repeated appearances within the same franchise must not be treated as evidence of success across multiple independent acquisition deals.

For example, appearing in three films from one franchise is not equivalent to appearing in three unrelated standalone acquisitions.

### Sample limitation

The project has reported a separate talent-analysis population of 27 films, comprising 15 franchise films and 12 standalone films.

This population must be distinguished from:

- The 112 unique movies in the complete analytical dataset.
- The 48 all-years acquisition units.
- The eight selected modern acquisition opportunities.

The exact 27-film selection must be retained in the notebook so that the talent findings can be reproduced.

The available results support Christopher Nolan as a promising director signal: Inception, Interstellar, Memento and The Prestige are four separate films associated with him, all with ratings above 8.1.

However, the evidence comes from a small selected population.

No actor should be described as a proven reliable acquisition signal simply because they appear repeatedly in the analysed sample.

The final actor and director tables must show actual distinct-film counts and associated performance measures. Names and rankings should not be inferred from frequency alone.

## Alternatives considered

**Rank opportunities using total profit alone**

Rejected because it ignores financial efficiency, audience reception and audience participation.

**Rank opportunities using ROI alone**

Rejected because unusually low production budgets can produce exceptional percentage returns without necessarily representing the strongest overall acquisition opportunity.

**Use a simple average of raw financial and audience measures**

Rejected because the variables have different scales and highly skewed distributions.

**Give movie count equal importance to profit and financial efficiency**

Rejected because this would structurally favour larger bundles.

**Combine all franchises and standalones into one shortlist**

Rejected because the acquisition structures have different commercial characteristics.

**Count every cast member and crew appearance**

Rejected because supporting performers and technical personnel would distort the identification of commercially relevant lead actors and directors.

**Rank talent by raw frequency alone**

Rejected because frequent appearances do not necessarily indicate commercial reliability or audience demand.

## Consequences

- The scoring system combines financial performance, efficiency and audience evidence.
- Percentile ranks reduce the influence of extreme numerical values.
- Separate rankings make franchise and standalone comparisons clearer.
- The portfolio score recognises content breadth without allowing movie count to dominate.
- The shortlist can be regenerated automatically.
- The talent analysis focuses on leading cast credits and correctly identified directors.
- Talent frequency is treated as a supporting negotiation signal, not proof of causation.
- Percentile scores depend on the ranking population.
- The selected weights represent analytical judgement, not experimentally proven predictors of licensing returns.
- The modern shortlist remains subject to the population reconciliation in ADR-003.

## What survives the next rerun?

The scoring and talent-analysis processes should remain reusable for the expected 500-title candidate list.

Adjoa should be able to regenerate:

1. Five component scores.
2. Core scores.
3. Portfolio scores.
4. Franchise rankings.
5. Standalone rankings.
6. Three leading franchise candidates.
7. Five leading standalone candidates.
8. First-five-cast-member selections.
9. Director records based on actual crew jobs.
10. Distinct-film and acquisition-unit talent counts.
11. Talent performance summaries.

The following must remain fixed and documented unless formally revised:

- Scoring weights.
- Percentile methodology.
- Ranking population.
- Missing-value treatment.
- Cast-order selection rule.
- Director job filter.
- Distinct-film counting method.
- Shortlist selection rules.

Every quarterly report should identify the ranking population because adding or removing candidates can change percentile scores and rankings.

## Revisit when

- StreamVault obtains actual licensing outcomes that allow the scoring weights to be tested.
- Streaming performance data becomes available.
- The business changes its acquisition priorities.
- A more reliable measure of expected streaming demand becomes available.
- The talent-analysis population becomes substantially larger.
- Evidence establishes that other cast positions provide better predictive value than the first-five-cast-order proxy.

---

# Overall ADR summary

| ADR | Decision | Main reason |
|---|---|---|
| ADR-001 | Deduplicate by canonical TMDb movie ID | Prevent repeated submissions from distorting the analysis |
| ADR-002 | Require at least two distinct collection films for franchise classification | Create consistent analytical acquisition units |
| ADR-003 | Compare historical performance across all years and 2000 onward | Address Finance's concerns while preserving historical evidence |
| ADR-004 | Use percentile-based scoring and role-specific talent analysis | Produce transparent and repeatable acquisition rankings |

## Long-term operating principle

The extraction, data validation, deduplication, acquisition classification, financial calculations, scoring and talent analysis must be reproducible without manual intervention.

Adjoa should be able to rerun the workflow against approximately 500 titles on her own laptop.

The next rerun should preserve the original analytical rules while generating a new candidate population, new financial results, new acquisition rankings and updated talent summaries.

The methodology should only change when there is a documented reason to do so.

**Important outstanding validation:** Before the ADRs and client recommendation are treated as final, reconcile the modern movie population and acquisition-unit counts, verify the precise scoring implementation, and ensure the talent tables contain the actual ranked results rather than inferred names.
