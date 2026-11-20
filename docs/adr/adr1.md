# ADR-001: Preserve source submissions and deduplicate using canonical TMDb movie IDs

**Status:** Accepted  
**Date:** 20 November 2026  
**Deciders:** Project team

## Context

StreamVault's candidate list was assembled over approximately four years from three sources:

- Adjoa's evaluation tracker.
- A spreadsheet inherited from Kwame's predecessor.
- A batch of titles supplied by a studio licensing desk.

The project brief identified 127 candidate submissions.

The extraction process produced the following results:

| Stage | Records |
|---|---:|
| Original candidate submissions | 127 |
| Successfully retrieved movie records | 119 |
| Unsuccessful or skipped submissions | 8 |
| Distinct TMDb movie IDs | 112 |
| Additional occurrences beyond unique films | 7 |

The 119 retrieved records therefore represent 112 distinct films.

Some titles were submitted more than once. The Dark Knight, for example, appeared three times. Pulp Fiction, The Matrix and Fight Club also appeared more than once.

The notebook retains separate datasets for:

- `movies`: successfully retrieved movie records.
- `unique_movies`: deduplicated movie records.
- `duplicate_movies`: records belonging to duplicated movie groups.
- `dark_knight_records`: a specific example of repeated submissions.
- `unresolved_summary`: a summary of unresolved candidate identifiers.

The duplicate dataset contains 13 rows. This represents records belonging to duplicated groups, not 13 additional films. The difference between the 119 retrieved records and 112 unique films is seven additional occurrences.

The extraction also produced eight unsuccessful or skipped submissions. A blank input and invalid or unresolved identifiers are among the issues requiring separate tracking.

Removing duplicate submissions without preserving their original records would make it difficult to establish where candidates originated and how frequently they were submitted.

## Decision

Use `api_movie_id` as the canonical identifier for movie-level analysis.

Preserve all successfully retrieved records in the original extraction dataset, but construct a separate analytical dataset containing one record per distinct movie ID.

Maintain the following identifiers:

| Field | Purpose |
|---|---|
| `source_row` | Original candidate position |
| `input_tmdb_id` | Identifier supplied in the candidate list |
| `api_movie_id` | Canonical movie identifier returned by TMDb |

Deduplication must occur before:

- Financial calculations.
- Franchise classification.
- Acquisition-unit construction.
- Movie-level rankings.
- Cast and crew analysis.

The earliest candidate occurrence should be retained when duplicate records are otherwise identical.

However, duplicate records must first be checked for conflicting API values. If two records for the same movie contain different information, the discrepancy must be logged rather than silently discarded.

The original records should remain available for auditing.

## Alternatives considered

**Delete duplicate records during extraction**

Rejected because it would destroy the original submission history and make source reconciliation difficult.

**Count every submission independently**

Rejected because repeated submissions would artificially increase movie counts, franchise sizes and financial performance.

**Deduplicate using movie titles**

Rejected because different films can share titles and international or alternative titles may differ.

**Use only the input TMDb identifier**

Not adopted as the sole analytical identifier because the API-returned movie ID provides the canonical identity used in subsequent movie, cast and crew relationships.

## Consequences

- Financial calculations use 112 distinct film identities rather than 119 retrieved records.
- Original submission occurrences remain available for auditing.
- Repeated submissions cannot artificially inflate acquisition performance.
- Cast and crew records can be associated with their canonical movie identities.
- Conflicting duplicate API records must be investigated rather than automatically resolved.

The eight unsuccessful submissions remain outside the financial analysis until their identities or API records can be resolved.

Their absence creates a potential opportunity cost: any of those titles could have been commercially attractive candidates.

We cannot establish their potential contribution without successfully retrieving and validating them.

## What survives the next rerun?

The deduplication process remains reusable when Adjoa processes 500 titles.

The pipeline should automatically:

1. Read the original candidate list.
2. Preserve each submission and its source row.
3. Retrieve the relevant movie details.
4. Record successful and unsuccessful API requests.
5. Identify duplicate movie IDs.
6. Check duplicate records for conflicting values.
7. Generate the unique analytical movie dataset.

No manual duplicate removal should be required.

## Revisit when

- TMDb identifiers are no longer sufficient to establish movie identity.
- Duplicate API records contain conflicting financial or metadata values.
- New candidate sources introduce additional identifier systems.
- Remakes, alternative releases or international editions require more advanced identity resolution.

---