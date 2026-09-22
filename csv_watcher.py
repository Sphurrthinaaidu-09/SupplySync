from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


# ============================================================
# SUPPLYSYNC CSV WATCHER
# ============================================================

CSV_ROOT = Path(r"D:\SupplySync_exact_postgresql_schema_dataset")
SYNC_SCRIPT = Path(__file__).resolve().parent / "sync_csv_to_postgres.py"

CHECK_INTERVAL_SECONDS = 60


def should_watch(path: Path) -> bool:
    """Return True only for CSV files we want to monitor."""
    if path.suffix.lower() != ".csv":
        return False

    name = path.name.lower()

    if "postgres_ready" in name:
        return False

    if "corrected" in name:
        return False

    return True


def get_csv_files() -> list[Path]:
    """Find all eligible CSV files recursively."""
    if not CSV_ROOT.exists():
        print(f"ERROR: CSV folder not found: {CSV_ROOT}")
        return []

    return [
        path
        for path in CSV_ROOT.rglob("*.csv")
        if should_watch(path)
    ]


def run_sync(csv_path: Path) -> None:
    """Run the existing SupplySync CSV-to-PostgreSQL sync script."""
    print()
    print("=" * 70)
    print("CSV CHANGE DETECTED")
    print("=" * 70)
    print(f"File: {csv_path}")

    command = [
        sys.executable,
        str(SYNC_SCRIPT),
        str(csv_path),
    ]

    try:
        result = subprocess.run(
            command,
            cwd=SYNC_SCRIPT.parent,
            check=False,
        )

        print(f"Sync process exit code: {result.returncode}")

        if result.returncode == 0:
            print("PostgreSQL sync completed successfully.")
        else:
            print("WARNING: PostgreSQL sync failed.")

    except Exception as exc:
        print(f"ERROR while running sync: {exc}")


def main() -> None:
    print("=" * 70)
    print("SUPPLYSYNC CSV WATCHER")
    print("=" * 70)
    print(f"Watching: {CSV_ROOT}")
    print(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    print()
    print("Watcher started.")
    print("Existing files will be used as the initial baseline.")
    print("Only changes made after the watcher starts will trigger sync.")
    print()

    # Initial baseline.
    known_files: dict[Path, float] = {}

    for path in get_csv_files():
        try:
            known_files[path] = path.stat().st_mtime
        except OSError:
            pass

    print(f"Monitoring {len(known_files)} CSV files.")
    print("Waiting for changes...")
    print()

    while True:
        try:
            current_files = get_csv_files()
            current_paths = set(current_files)

            # Detect new or modified files.
            for path in current_files:
                try:
                    modified_time = path.stat().st_mtime
                except OSError:
                    continue

                previous_time = known_files.get(path)

                if previous_time is None:
                    print(f"New CSV detected: {path}")
                    known_files[path] = modified_time
                    run_sync(path)

                elif modified_time > previous_time:
                    known_files[path] = modified_time
                    run_sync(path)

            # Remove files that no longer exist.
            for path in list(known_files):
                if path not in current_paths:
                    del known_files[path]

            time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print()
            print("SupplySync CSV watcher stopped.")
            break

        except Exception as exc:
            print(f"Watcher error: {exc}")
            print("Continuing to monitor...")
            time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()