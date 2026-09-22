from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from database import (
        detect_plastic_dataset,
        load_plastic_table_data,
        log_ingestion,
    )
except Exception as exc:
    print(f"ERROR: Could not import database.py: {exc}")
    sys.exit(1)


def transform_dim_products(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw dim_products.csv into the PostgreSQL structure."""

    required = {
        "product_name",
        "product_id",
        "category",
        "price_INR",
        "price_USD",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"dim_products is missing required columns: {sorted(missing)}"
        )

    out = pd.DataFrame()

    out["product_id"] = df["product_id"].astype(str).str.strip()
    out["product_name"] = df["product_name"].astype(str).str.strip()

    out["product_category"] = (
        df["category"].astype(str).str.strip()
    )

    # Fields not present in the raw CSV
    out["product_type"] = "Finished Product"
    out["specification"] = out["product_name"]
    out["unit"] = "kg"
    out["is_active"] = True

    # PostgreSQL selling_price uses INR
    out["selling_price"] = pd.to_numeric(
        df["price_INR"],
        errors="coerce",
    )

    return out


def transform_fact_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw fact_orders.csv into the PostgreSQL structure."""

    required = {
        "order_id",
        "customer_id",
        "order_date",
        "requested_delivery_date",
        "order_status",
        "total_amount",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"fact_orders is missing required columns: {sorted(missing)}"
        )

    out = pd.DataFrame()

    out["order_id"] = (
        df["order_id"].astype(str).str.strip()
    )

    out["customer_id"] = (
        df["customer_id"].astype(str).str.strip()
    )

    out["order_date"] = df["order_date"]

    out["requested_delivery_date"] = (
        df["requested_delivery_date"]
    )

    status_map = {
        "Confirmed": "Confirmed",
        "In Production": "In Production",
        "Ready to Dispatch": "Ready to Dispatch",
        "Partially Fulfilled": "Partially Delivered",
        "Delivered": "Delivered",
        "Fulfilled": "Delivered",
        "Cancelled": "Cancelled",
        "Pending": "Confirmed",
    }

    original_status = (
        df["order_status"]
        .astype(str)
        .str.strip()
    )

    out["order_status"] = (
        original_status
        .map(status_map)
        .fillna(original_status)
    )

    out["total_order_value"] = pd.to_numeric(
        df["total_amount"],
        errors="coerce",
    )

    out["currency"] = "INR"

    return out


def ingest_csv(csv_path: str) -> dict:
    """Read, transform, validate and load one CSV file."""

    path = Path(csv_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Expected a CSV file, received: {path.name}"
        )

    print("=" * 70)
    print("SUPPLYSYNC AUTOMATED INGESTION")
    print("=" * 70)
    print(f"File: {path}")

    # Read everything as text initially.
    # This prevents IDs from being converted to integers.
    df = pd.read_csv(
        path,
        dtype=str,
    )

    print(f"Rows received: {len(df):,}")
    print(f"Columns received: {len(df.columns):,}")

    # ---------------------------------------------------------
    # RAW DATASET TRANSFORMATIONS
    # ---------------------------------------------------------

    # Raw dim_products.csv
    if (
        "price_INR" in df.columns
        and "price_USD" in df.columns
    ):
        print(
            "Raw dim_products format detected - transforming..."
        )

        df = transform_dim_products(df)

    # Raw fact_orders.csv
    elif (
        "total_amount" in df.columns
        and "requested_delivery_date" in df.columns
        and "order_status" in df.columns
    ):
        print(
            "Raw fact_orders format detected - transforming..."
        )

        df = transform_fact_orders(df)

    # ---------------------------------------------------------
    # DATASET DETECTION
    # ---------------------------------------------------------

    dataset = detect_plastic_dataset(df.columns)

    if not dataset:
        raise ValueError(
            "Could not identify the CSV as one of the supported "
            "SupplySync plastic datasets. Check the column names."
        )

    print(f"Detected dataset: plastic.{dataset}")
    print("Loading into PostgreSQL...")

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    result = load_plastic_table_data(
        dataset,
        df,
    )

    # ---------------------------------------------------------
    # INGESTION LOG
    # ---------------------------------------------------------

    try:
        log_ingestion(
            dataset=result.get(
                "dataset",
                dataset,
            ),
            received_rows=result.get(
                "received",
                0,
            ),
            validated_rows=result.get(
                "validated",
                0,
            ),
            inserted_rows=result.get(
                "inserted",
                0,
            ),
            updated_rows=result.get(
                "updated",
                0,
            ),
            skipped_rows=result.get(
                "skipped",
                0,
            ),
            status="SUCCESS",
        )

    except Exception as audit_exc:
        print(
            "WARNING: Data loaded, but audit logging failed: "
            f"{audit_exc}"
        )

    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    print()
    print("SUCCESS")

    print(
        f"Dataset:    "
        f"{result.get('dataset', dataset)}"
    )

    print(
        f"Received:   "
        f"{result.get('received', 0):,}"
    )

    print(
        f"Validated:  "
        f"{result.get('validated', 0):,}"
    )

    print(
        f"Inserted:   "
        f"{result.get('inserted', 0):,}"
    )

    print(
        f"Updated:    "
        f"{result.get('updated', 0):,}"
    )

    print(
        f"Skipped:    "
        f"{result.get('skipped', 0):,}"
    )

    print(
        f"Duplicates: "
        f"{result.get('duplicate_rows_in_file', 0):,}"
    )

    print("=" * 70)

    return result


def main() -> int:

    if len(sys.argv) != 2:

        print(
            'Usage: python sync_csv_to_postgres.py '
            '"C:\\Path\\file.csv"'
        )

        return 2

    try:

        ingest_csv(sys.argv[1])

        return 0

    except Exception as exc:

        print()
        print("FAILED")
        print(f"Reason: {exc}")
        print("=" * 70)

        return 1


if __name__ == "__main__":
    raise SystemExit(main())