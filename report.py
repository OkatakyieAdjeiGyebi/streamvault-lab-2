
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# ============================================================
# STREAMVAULT - INITIAL DATASET PROFILING
# Purpose: Understand extracted TMDb data before cleaning
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "streamvault_profile_report.txt"

FILES = {
    "Movies": "movies.csv",
    "Cast": "cast.csv",
    "Crew": "crew.csv",
    "Extraction Log": "extraction_log.csv"
}

report = []


def add(text=""):
    """Add text to the report and print it."""
    report.append(str(text))
    print(text)


def section(title):
    add("\n" + "=" * 75)
    add(title.upper())
    add("=" * 75)


def find_file(filename):
    """Find a CSV anywhere inside the project folder."""
    matches = list(BASE_DIR.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Could not find {filename} inside {BASE_DIR}"
        )

    # Select the most recently modified matching file
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if len(matches) > 1:
        add(
            f"WARNING: Found {len(matches)} copies of {filename}. "
            f"Using the most recently modified: {matches[0]}"
        )

    return matches[0]


def load_csv(name, filename):
    """Load a dataset while preserving identifier columns as strings."""
    path = find_file(filename)

    # Read column names first to determine available ID columns
    columns = pd.read_csv(path, nrows=0).columns.tolist()

    id_columns = [
        col for col in columns
        if col.lower() in [
            "tmdb_id", "movie_id", "input_id",
            "person_id", "actor_id", "id"
        ]
    ]

    dtype_mapping = {col: "string" for col in id_columns}

    df = pd.read_csv(
        path,
        dtype=dtype_mapping,
        low_memory=False
    )

    add(f"{name} loaded from: {path.relative_to(BASE_DIR)}")
    return df


# ============================================================
# 1. LOAD ALL DATASETS
# ============================================================

section("1. Loading datasets")

datasets = {}

for name, filename in FILES.items():
    datasets[name] = load_csv(name, filename)

movies = datasets["Movies"]
cast = datasets["Cast"]
crew = datasets["Crew"]
log = datasets["Extraction Log"]

add("\nAll four datasets loaded successfully.")


# ============================================================
# 2. DATASET DIMENSIONS AND COLUMNS
# ============================================================

section("2. Dataset dimensions and columns")

for name, df in datasets.items():
    add(f"\n{name}")
    add("-" * 40)
    add(f"Rows: {df.shape[0]:,}")
    add(f"Columns: {df.shape[1]:,}")
    add(f"Column names: {df.columns.tolist()}")


# ============================================================
# 3. DATA TYPES AND SAMPLE RECORDS
# ============================================================

section("3. Data types and sample records")

for name, df in datasets.items():
    add(f"\n{name} - Data types")
    add(df.dtypes.to_string())

    add(f"\n{name} - First 5 records")
    add(df.head(5).to_string(index=False))


# ============================================================
# 4. UNIQUE VALUES AND FREQUENCIES
# ============================================================

section("4. Unique values and frequencies")

MAX_UNIQUE_TO_DISPLAY = 30

for name, df in datasets.items():
    add(f"\n{name}")

    for col in df.columns:
        unique_count = df[col].nunique(dropna=False)

        add(f"\nColumn: {col}")
        add(f"Unique values including missing: {unique_count:,}")

        if unique_count <= MAX_UNIQUE_TO_DISPLAY:
            add(df[col].value_counts(dropna=False).to_string())
        else:
            add("Top 15 most frequent values:")
            add(
                df[col]
                .value_counts(dropna=False)
                .head(15)
                .to_string()
            )

            add("Sample distinct non-missing values:")
            add(
                str(
                    df[col]
                    .dropna()
                    .drop_duplicates()
                    .head(10)
                    .tolist()
                )
            )


# ============================================================
# 5. MISSING VALUE ANALYSIS
# ============================================================

section("5. Missing value analysis")

for name, df in datasets.items():
    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percentage": (
            df.isna().mean() * 100
        ).round(2),
        "data_type": df.dtypes.astype(str)
    })

    missing = missing.sort_values(
        "missing_percentage",
        ascending=False
    )

    add(f"\n{name} - Missing values")
    add(missing.to_string())


# ============================================================
# 6. DUPLICATE ANALYSIS
# ============================================================

section("6. Duplicate analysis")

for name, df in datasets.items():
    add(f"\n{name}")
    add(f"Duplicate complete rows: {df.duplicated().sum():,}")

    possible_id_columns = [
        col for col in df.columns
        if col.lower() in ["tmdb_id", "input_id"]
    ]

    for col in possible_id_columns:
        add(
            f"Duplicate values in {col}: "
            f"{df[col].duplicated().sum():,}"
        )

        repeated = df[
            df[col].duplicated(keep=False)
        ]

        if not repeated.empty:
            add(f"Repeated {col} records:")
            add(repeated.head(30).to_string(index=False))


# ============================================================
# 7. NUMERICAL SUMMARY
# ============================================================

section("7. Numerical summary")

for name, df in datasets.items():
    numeric = df.select_dtypes(include="number")

    add(f"\n{name}")

    if numeric.empty:
        add("No numeric columns found.")
    else:
        add(numeric.describe().T.to_string())


# ============================================================
# 8. ZERO AND NEGATIVE VALUE CHECKS
# ============================================================

section("8. Zero and negative value checks")

for name, df in datasets.items():
    numeric = df.select_dtypes(include="number")

    add(f"\n{name}")

    if numeric.empty:
        add("No numeric columns found.")
        continue

    for col in numeric.columns:
        zero_count = (numeric[col] == 0).sum()
        negative_count = (numeric[col] < 0).sum()

        add(
            f"{col}: "
            f"Zeros = {zero_count:,}, "
            f"Negative values = {negative_count:,}"
        )


# ============================================================
# 9. EXTRACTION LOG ANALYSIS
# ============================================================

section("9. Extraction log analysis")

add(f"Total extraction log records: {len(log):,}")

for col in log.columns:
    if any(
        word in col.lower()
        for word in ["status", "error", "success"]
    ):
        add(f"\n{col} frequency:")
        add(log[col].value_counts(dropna=False).to_string())

add("\nFirst 20 extraction log records:")
add(log.head(20).to_string(index=False))


# ============================================================
# 10. IMPORTANT MOVIE FIELDS
# ============================================================

section("10. Important movie information")

important_columns = [
    "tmdb_id",
    "id",
    "title",
    "original_title",
    "release_date",
    "budget",
    "revenue",
    "runtime",
    "vote_average",
    "vote_count",
    "popularity",
    "original_language",
    "status",
    "belongs_to_collection"
]

available_columns = [
    col for col in important_columns
    if col in movies.columns
]

if available_columns:
    add(
        movies[available_columns]
        .head(30)
        .to_string(index=False)
    )
else:
    add("None of the expected movie fields were found.")


# ============================================================
# 11. COLLECTION ANALYSIS
# ============================================================

section("11. Collection information")

collection_col = "belongs_to_collection"

if collection_col in movies.columns:

    collection_values = movies[collection_col].dropna()

    add(
        f"Movies with collection information: "
        f"{len(collection_values):,}"
    )

    add(
        f"Movies without collection information: "
        f"{movies[collection_col].isna().sum():,}"
    )

    add("\nCollection examples:")

    add(
        movies.loc[
            movies[collection_col].notna(),
            ["title", collection_col]
            if "title" in movies.columns
            else [collection_col]
        ].head(30).to_string(index=False)
    )

else:
    add("Collection column not found.")


# ============================================================
# 12. CAST AND CREW OVERVIEW
# ============================================================

section("12. Cast and crew overview")

add(f"Total cast records: {len(cast):,}")
add(f"Total crew records: {len(crew):,}")

for name, df in [("Cast", cast), ("Crew", crew)]:
    add(f"\n{name} columns: {df.columns.tolist()}")

    for col in ["department", "job", "known_for_department"]:
        if col in df.columns:
            add(f"\n{name} - {col} frequencies:")
            add(df[col].value_counts(dropna=False).head(30).to_string())


# ============================================================
# 13. SAVE REPORT
# ============================================================

section("13. Report completion")

add(f"Report generated: {datetime.now()}")
add("No records were deleted or modified during this profiling exercise.")
add("This report is for initial diagnosis, not final data cleaning.")

OUTPUT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("\n" + "=" * 75)
print("PROFILING COMPLETE")
print("=" * 75)
print(f"Report saved to: {OUTPUT_FILE}")

