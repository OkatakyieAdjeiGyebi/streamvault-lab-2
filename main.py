
import os
import json
import requests
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

if not API_KEY:
    raise ValueError("TMDB_API_KEY is missing")

INPUT_FILE = "data/raw/id_list.csv"

RAW_DIR = Path("data/raw/api_responses")
PROCESSED_DIR = Path("data/processed")

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. API SESSION
# ==========================================

session = requests.Session()

retry = Retry(
    total=4,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def fetch_tmdb(endpoint):

    url = f"{BASE_URL}/{endpoint}"

    response = session.get(
        url,
        params={"api_key": API_KEY},
        timeout=30
    )

    try:
        payload = response.json()
    except ValueError:
        payload = {"raw_response": response.text}

    return response.status_code, payload


# ==========================================
# 3. LOAD ORIGINAL CANDIDATE LIST
# ==========================================

# Preserve every original ID exactly as supplied.
df = pd.read_csv(
    INPUT_FILE,
    dtype={"tmdb_id": "string"},
    keep_default_na=False,
    skip_blank_lines=False
)

df["source_row"] = range(1, len(df) + 1)

df["tmdb_id"] = df["tmdb_id"].str.strip()

print("Original candidate rows:", len(df))
print("Unique supplied IDs:", df["tmdb_id"].nunique())

# ==========================================
# 4. EXTRACT ALL CANDIDATES
# ==========================================

movie_records = []
cast_records = []
crew_records = []
extraction_logs = []

for _, row in df.iterrows():

    movie_id = row["tmdb_id"]
    source_row = row["source_row"]


    # Skip intentionally blank IDs
    if pd.isna(movie_id) or movie_id.strip() in ["", "MISSING_ID"]:
        extraction_logs.append({
            "source_row": source_row,
            "input_tmdb_id": None,
            "details_http_status": None,
            "credits_http_status": None,
            "details_retrieved": False,
            "credits_retrieved": False,
            "details_error": "Skipped: missing TMDb ID",
            "credits_error": "Skipped: missing TMDb ID"
        })

        print(f"Skipping row {source_row}: Missing TMDb ID")
        continue


    print(
        f"\nProcessing row {source_row}/{len(df)}: "
        f"TMDb ID = {movie_id}"
    )

    details = None
    credits = None

    details_status = None
    credits_status = None

    details_error = None
    credits_error = None

    # --------------------------------------
    # Fetch movie details
    # --------------------------------------

    try:

        details_status, details = fetch_tmdb(
            f"movie/{movie_id}"
        )

    except requests.RequestException as e:
        details_error = str(e)

    # Save response, including error responses
    with open(
        RAW_DIR / f"row_{source_row}_details.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump({
            "source_row": int(source_row),
            "input_id": movie_id,
            "http_status": details_status,
            "response": details,
            "error": details_error
        }, file, indent=4, ensure_ascii=False)

    # --------------------------------------
    # Fetch movie credits independently
    # --------------------------------------

    try:

        credits_status, credits = fetch_tmdb(
            f"movie/{movie_id}/credits"
        )

    except requests.RequestException as e:
        credits_error = str(e)

    # Save credits response
    with open(
        RAW_DIR / f"row_{source_row}_credits.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump({
            "source_row": int(source_row),
            "input_id": movie_id,
            "http_status": credits_status,
            "response": credits,
            "error": credits_error
        }, file, indent=4, ensure_ascii=False)

    # --------------------------------------
    # Extract movie details if available
    # --------------------------------------

    if (
        details_status == 200
        and isinstance(details, dict)
        and details.get("id") is not None
    ):

        movie_records.append({

            "source_row": source_row,
            "input_tmdb_id": movie_id,

            "api_movie_id": details.get("id"),
            "title": details.get("title"),
            "original_title": details.get("original_title"),
            "release_date": details.get("release_date"),

            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "runtime": details.get("runtime"),

            "vote_average": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
            "popularity": details.get("popularity"),

            "original_language": details.get(
                "original_language"
            ),

            "status": details.get("status"),

            "genres": ", ".join(
                g["name"]
                for g in details.get("genres", [])
            ),

            "collection_id": (
                details.get("belongs_to_collection") or {}
            ).get("id"),

            "collection_name": (
                details.get("belongs_to_collection") or {}
            ).get("name")
        })

    # --------------------------------------
    # Extract cast if available
    # --------------------------------------

    if (
        credits_status == 200
        and isinstance(credits, dict)
    ):

        for actor in credits.get("cast", []):

            cast_records.append({

                "source_row": source_row,
                "input_tmdb_id": movie_id,

                "movie_id": actor.get("id")
                if False else (
                    details.get("id")
                    if isinstance(details, dict)
                    else None
                ),

                "actor_id": actor.get("id"),
                "actor_name": actor.get("name"),
                "character": actor.get("character"),
                "cast_order": actor.get("order")
            })

        # ----------------------------------
        # Extract crew
        # ----------------------------------

        for person in credits.get("crew", []):

            crew_records.append({

                "source_row": source_row,
                "input_tmdb_id": movie_id,

                "movie_id": (
                    details.get("id")
                    if isinstance(details, dict)
                    else None
                ),

                "person_id": person.get("id"),
                "person_name": person.get("name"),
                "department": person.get("department"),
                "job": person.get("job")
            })

    # --------------------------------------
    # Record extraction outcome
    # --------------------------------------

    extraction_logs.append({

        "source_row": source_row,
        "input_tmdb_id": movie_id,

        "details_http_status": details_status,
        "credits_http_status": credits_status,

        "details_retrieved": (
            details_status == 200
            and isinstance(details, dict)
            and details.get("id") is not None
        ),

        "credits_retrieved": (
            credits_status == 200
            and isinstance(credits, dict)
        ),

        "details_error": details_error,
        "credits_error": credits_error
    })


# ==========================================
# 5. CREATE DATAFRAMES
# ==========================================

movies_df = pd.DataFrame(movie_records)
cast_df = pd.DataFrame(cast_records)
crew_df = pd.DataFrame(crew_records)
logs_df = pd.DataFrame(extraction_logs)


# ==========================================
# 6. EXPLICIT DATA TYPES
# ==========================================

def convert_integer_columns(data, columns):

    for column in columns:

        if column in data.columns:

            data[column] = pd.array(
                data[column],
                dtype="Int64"
            )


def convert_float_columns(data, columns):

    for column in columns:

        if column in data.columns:

            data[column] = pd.array(
                data[column],
                dtype="Float64"
            )


# Movie dataset
convert_integer_columns(
    movies_df,
    [
        "source_row",
        "api_movie_id",
        "budget",
        "revenue",
        "runtime",
        "vote_count",
        "collection_id"
    ]
)

convert_float_columns(
    movies_df,
    [
        "vote_average",
        "popularity"
    ]
)

# Cast dataset
convert_integer_columns(
    cast_df,
    [
        "source_row",
        "movie_id",
        "cast_order"
    ]
)

# Keep identifiers as strings
for column in ["input_tmdb_id", "actor_id"]:
    if column in cast_df.columns:
        cast_df[column] = cast_df[column].astype("string")

# Crew dataset
convert_integer_columns(
    crew_df,
    [
        "source_row",
        "movie_id"
    ]
)

for column in ["input_tmdb_id", "person_id"]:
    if column in crew_df.columns:
        crew_df[column] = crew_df[column].astype("string")


# ==========================================
# 7. SAVE DATASETS
# ==========================================

movies_df.to_csv(
    PROCESSED_DIR / "movies.csv",
    index=False
)

cast_df.to_csv(
    PROCESSED_DIR / "cast.csv",
    index=False
)

crew_df.to_csv(
    PROCESSED_DIR / "crew.csv",
    index=False
)

logs_df.to_csv(
    PROCESSED_DIR / "extraction_log.csv",
    index=False
)


# ==========================================
# 8. EXTRACTION SUMMARY
# ==========================================

print("\n========== EXTRACTION SUMMARY ==========")

print("Original rows:", len(df))
print("Movie records retrieved:", len(movies_df))
print("Cast records:", len(cast_df))
print("Crew records:", len(crew_df))

print(
    "Details successful:",
    logs_df["details_retrieved"].sum()
)



print(
    "Credits successful:",
    logs_df["credits_retrieved"].sum()
)

print(
    "Details unsuccessful:",
    (~logs_df["details_retrieved"]).sum()
)

print(
    "Credits unsuccessful:",
    (~logs_df["credits_retrieved"]).sum()
)

print("\nMOVIE DATA TYPES:")
print(movies_df.dtypes)




print("Input rows:", len(df))
print("Blank ID rows:", (df["tmdb_id"].str.strip() == "").sum())

print(
    df[df["tmdb_id"].str.strip() == ""]
    [["tmdb_id", "source_row"]]
)




print("\nEXTRACTION COMPLETE")
