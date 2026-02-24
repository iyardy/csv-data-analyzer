import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CSV Data Analyzer: preview data and compute basic statistics."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="data.csv",
        help="Path to the CSV file (default: data.csv)",
    )
    parser.add_argument(
        "--head",
        type=int,
        default=5,
        help="Number of rows to preview (default: 5)",
    )
    parser.add_argument(
        "--column",
        type=str,
        default=None,
        help="Analyze a single column (must be numeric). If omitted, analyze all numeric columns.",
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter (default: ,)",
    )
    parser.add_argument(
    "--stats-only",
    action="store_true",
    help="Print only statistics (skip overview and preview)"
)
    parser.add_argument(
    "--export",
    type=str,
    default=None,
    help="Export computed statistics to a CSV file (e.g., stats.csv)"
)
    return parser.parse_args()


def load_csv(csv_path: Path, delimiter: str) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    # Keep defaults simple; we'll handle bad inputs with clear errors.
    try:
        df = pd.read_csv(csv_path, sep=delimiter)
    except pd.errors.EmptyDataError as e:
        raise ValueError("CSV file is empty or has no columns.") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            "CSV parsing failed. Check delimiter/format (try --delimiter ';' if needed)."
        ) from e

    if df.shape[1] == 0:
        raise ValueError("CSV has zero columns.")
    return df


def dataset_overview(df: pd.DataFrame) -> str:
    lines = []
    lines.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    lines.append("Columns & dtypes:")
    for col, dtype in df.dtypes.items():
        lines.append(f"  - {col}: {dtype}")

    missing = df.isna().sum()
    missing_total = int(missing.sum())
    if missing_total == 0:
        lines.append("Missing values: 0")
    else:
        lines.append(f"Missing values total: {missing_total}")
        top_missing = missing[missing > 0].sort_values(ascending=False)
        for col, cnt in top_missing.items():
            lines.append(f"  - {col}: {int(cnt)}")
    return "\n".join(lines)


def numeric_stats(df: pd.DataFrame, column: Optional[str] = None) -> pd.DataFrame:
    if column is not None:
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found. Available columns: {', '.join(df.columns)}"
            )
        series = df[column]
        if not pd.api.types.is_numeric_dtype(series):
            raise ValueError(
                f"Column '{column}' is not numeric (dtype={series.dtype}). Choose a numeric column."
            )
        stats = series.describe()  # count, mean, std, min, 25%, 50%, 75%, max
        # Return as DataFrame for consistent printing
        return stats.to_frame(name=column)

    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] == 0:
        raise ValueError("No numeric columns found to analyze.")
    return num_df.describe().T  # one row per numeric column


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)

    try:
        df = load_csv(csv_path, args.delimiter)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    print("=== CSV DATA ANALYZER ===")
    print(f"File: {csv_path.resolve()}\n")

    if not args.stats_only:
        print("=== OVERVIEW ===")
        print(dataset_overview(df))
        print()

        print(f"=== PREVIEW (first {args.head} rows) ===")
        print(df.head(args.head).to_string(index=False))
        print()

    print("=== STATISTICS (numeric) ===")
    try:
        stats_df = numeric_stats(df, args.column)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    # NEW: export stats if requested
    if args.export:
        try:
            stats_df.to_csv(args.export, index=True)
            print(f"[OK] Exported statistics to: {args.export}")
        except Exception as e:
            print(f"[ERROR] Failed to export stats: {e}", file=sys.stderr)
            return 1

    # Pretty print stats with limited decimals
    with pd.option_context("display.float_format", "{:.4f}".format):
        print(stats_df.to_string())
    print()

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())