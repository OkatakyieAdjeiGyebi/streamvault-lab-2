
# Document 1 — Data Diagnosis

## 1.1 Executive Summary

The analysis began with 127 candidate submissions. The extraction process successfully retrieved 119 movie records, alongside their cast and crew credits.

The initial data audit revealed that the main problem was not simply missing information. It was a combination of invalid identifiers, repeated submissions, incomplete franchise information, and inconsistencies between the original candidate list and the API responses.

The following datasets were created:

| Dataset | Records | Columns |
|---|---:|---:|
| Movies | 119 | 17 |
| Cast | 8,407 | 7 |
| Crew | 25,957 | 7 |
| Extraction log | 127 | 8 |

## 1.2 Problems Discovered, Ranked by Risk

| Risk | Problem | Detection | Business Impact |
|---|---|---|---|
| Critical | Invalid or missing candidate IDs | Extraction log and HTTP responses | Eight candidates did not produce usable movie records. |
| High | Repeated movie submissions | Duplicate ID and title checks | Could inflate franchise counts and distort profitability comparisons. |
| High | Incomplete collection metadata | Missing-value analysis | Could cause legitimate standalone titles to be misclassified or excluded. |
| High | Incorrect identifier format | Comparison of input IDs against API IDs | Can break joins between movies, cast, and crew. |
| Medium | Missing extraction-log information | Log validation | Makes it harder to distinguish an API failure from an invalid input. |
| Medium | Unverified franchise membership | Collection ID and distinct movie ID grouping | Could result in incorrect bundle classifications. |
| Medium | Historical financial comparability | Release-year segmentation | Could make older films appear more profitable without accounting for inflation. |

## 1.3 Detailed Findings

### Problem 1: Failed API Retrievals

The extraction log recorded:

- 119 successful detail requests.
- 119 successful credits requests.
- Seven HTTP 404 responses.
- One additional record skipped because its TMDb ID was missing.

The failed records were associated with source rows 17, 29, 34, 72, 92, and 98, while rows 68 and 110 contained missing IDs.

An important discovery was that the original candidate file had 126 rows, despite the project brief describing 127 titles. Rows 68 and 110 were missing identifiers in the original file.

This discrepancy needs to be resolved against the original source submissions.

**Business impact:** Eight candidate submissions could not be evaluated using the extracted records. Their exclusion means the final shortlist may not contain every potentially attractive licensing opportunity.

### Problem 2: Repeated Movie Submissions

The Movies dataset contained 119 records but only 112 distinct TMDb movie IDs.

There were no exact duplicate rows, but seven additional records represented repeated movie IDs.

Examples included:

- The Dark Knight appeared three times.
- Pulp Fiction appeared twice.
- The Matrix appeared twice.
- The Shawshank Redemption appeared twice.
- Fight Club appeared twice.
- The Empire Strikes Back appeared twice.

We retained the original extraction records for auditing but used distinct movie IDs for movie-level calculations.

**Business impact:** Counting repeated submissions as separate films could artificially increase the size and performance of acquisition opportunities.

### Problem 3: Missing Collection Metadata

Nineteen movie records had no collection ID or collection name.

This represents approximately 16% of the retrieved movie records.

However, we did not automatically classify these records as bad data. A standalone film may legitimately have no franchise collection.

The decision was to preserve these titles and treat them as standalone acquisition opportunities unless other evidence established their membership in a multi-film bundle.

**Business impact:** Automatically deleting these films would remove potential licensing opportunities.

### Problem 4: Identifier Inconsistency

The cast dataset contained `tt0468569` as an input identifier.

This resembles an IMDb-style identifier rather than a numeric TMDb movie ID.

The investigation also revealed a mismatch between the input identifiers and API movie identifiers in some records.

We therefore preserved separate fields for:

- `source_row`: Original candidate position.
- `input_tmdb_id`: Identifier supplied to the extraction process.
- `api_movie_id`: Identifier returned by TMDb.

This distinction is essential when joining datasets.

**Business impact:** Incorrect joins could associate talent with the wrong film or cause valid credits to disappear from the analysis.

### Problem 5: Profiling Inconsistency

An earlier profiling report indicated that the collection column could not be found, despite the Movies dataset containing both `collection_id` and `collection_name`.

We treated this as a profiling-code problem rather than a missing-data problem and used the actual dataset columns for subsequent analysis.

## 1.4 Candidate-List Reconciliation

The following figures summarize the extraction and deduplication process:

| Metric | Count |
|---|---:|
| Original candidate submissions described in the brief | 127 |
| Successfully retrieved records | 119 |
| Failed or skipped submissions | 8 |
| Unique retrieved movie IDs | 112 |
| Repeated records beyond unique IDs | 7 |

The analysis also produced a later shortlist of 27 films:

- 15 franchise films.
- 12 standalone films.

These are different stages of the analysis and should not be confused.

**Important reconciliation issue:** The final acquisition-unit tables also report 48 units, comprising 23 franchise units and 25 standalone units. We need to preserve the exact grouping and filtering rules behind these 48 units before presenting them as the same population as the 27-film shortlist.

## 1.5 What the Data Limitations Cost Kwame

The missing eight submissions represent potentially lost opportunities. We cannot determine whether any of them would have ranked among the strongest acquisition targets.

The repeated submissions could have overstated performance if not deduplicated.

Missing collection information could have caused incorrect bundle decisions.

Finally, historical box-office figures are not equivalent to current licensing value. They provide useful evidence of commercial performance, but not a reliable estimate of the amount StreamVault should pay today.

The recommendation should therefore be treated as a negotiation framework, not a guaranteed financial return.
