# ADR-002: Define franchise acquisition units using distinct TMDb collection membership

**Status:** Accepted  
**Date:** 20 November 2026  
**Deciders:** Project team

## Context

StreamVault acquires films through two commercial arrangements:

1. Franchise bundles, where multiple films are acquired together.
2. Standalone acquisitions, where individual films are licensed separately.

The original candidate list does not explicitly identify which titles belong to the same acquisition bundle.

TMDb provides collection metadata through the movie details endpoint, including:

- `collection_id`
- `collection_name`

However, not every film with collection metadata represents a franchise acquisition opportunity within the submitted candidate list.

Some collections contain only one candidate film because the remaining entries were not included in the submission.

The notebook identified 19 retrieved movie records with missing collection information.

Missing collection information does not necessarily indicate a data error. Some films are genuinely standalone titles.

The analysis therefore needs a consistent classification rule that avoids incorrectly treating every collection-associated film as a franchise.

## Decision

Use TMDb collection membership to construct analytical acquisition units.

Apply the following classification:

**Franchise**

Two or more distinct candidate movie IDs belong to the same TMDb collection.

**Standalone**

A candidate movie does not belong to a collection containing at least two distinct candidate films.

The classification must use:

- `api_movie_id` to identify distinct films.
- `collection_id` to group films.
- `collection_name` for reporting and interpretation.

Repeated submissions must not increase the number of films in a collection.

Financial calculations for franchise acquisition units must aggregate the budgets and revenues of their distinct candidate films.

Each standalone film represents an individual acquisition unit.

### Important commercial qualification

TMDb collection membership is an analytical classification, not confirmation of a studio's contractual bundle structure.

A collection identified as a franchise may not be available as one complete licensing package.

Similarly, a film classified as standalone may belong to a wider commercial franchise that was not fully represented in the candidate list.

The analysis must therefore distinguish between:

- TMDb collection membership.
- Candidate films represented in the dataset.
- Actual studio licensing arrangements.

Only studio licensing information can confirm the last of these.

## Alternatives considered

**Treat every movie with collection metadata as a franchise**

Rejected because some collections contain only one represented candidate film.

**Discard films without collection metadata**

Rejected because missing collection information does not establish that a film is unsuitable for acquisition.

**Manually assign franchise membership using film titles**

Rejected because this introduces subjective classifications and makes quarterly reruns difficult to reproduce.

**Use external franchise databases to reconstruct missing collections**

Not adopted for the initial analysis because the classification was designed around the supplied TMDb data. External verification can be introduced as a future improvement.

## Consequences

The deduplicated acquisition analysis produced:

| Acquisition type | Acquisition units | Movies |
|---|---:|---:|
| Franchise | 23 | 87 |
| Standalone | 25 | 25 |
| **Total** | **48** | **112** |

These figures describe the all-years acquisition-unit analysis.

The classification provides a consistent framework for comparing bundles and individual films.

However:

- Some genuine franchise opportunities may be classified as standalone.
- Some collections may contain additional films outside the candidate list.
- A TMDb collection does not prove that a studio will sell its films together.
- Acquisition-unit counts must not be confused with movie counts.

The analysis cannot establish whether StreamVault can acquire all films in a particular collection under one agreement.

## What survives the next rerun?

The collection-grouping process is reusable for 500 or more candidate titles.

Adjoa should be able to regenerate:

- Franchise collections with two or more distinct candidate films.
- Single-candidate collections.
- Films without collection metadata.
- Distinct movie counts per collection.
- Aggregate financial performance per acquisition unit.

The workflow should preserve a separate classification audit containing the collection ID, collection name, distinct movie count and classification reason.

No manual franchise assignments should be required during ordinary reruns.

## Revisit when

- Studio licensing information provides authoritative bundle definitions.
- TMDb collection information is incomplete or inconsistent.
- StreamVault begins considering partial franchise bundles.
- Additional verified franchise metadata becomes available.

---
