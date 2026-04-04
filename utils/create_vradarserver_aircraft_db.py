__author__ = "jdanek"

import os
import sqlite3
import pandas as pd

CSV_FOLDER = "../data/vradarserver/standing-data/aircraft"
DB_FILE = "../data/vradarserver-aircraft.db"

def get_csv_files(folder):
    # Recursively collect all CSV files
    csv_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files


def main():
    conn = sqlite3.connect(DB_FILE)

    csv_files = get_csv_files(CSV_FOLDER)
    print(f"Found {len(csv_files)} CSV files.")

    first = True
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df_selected = df[['ICAO', 'ManufacturerAndModel']]

            # Write to SQLite
            df_selected.to_sql(
                "aircraft",
                conn,
                if_exists="replace" if first else "append",
                index=False
            )
            first = False

        except Exception as e:
            print(f"Error processing {file}: {e}")

    conn.execute("CREATE INDEX idx_icao ON aircraft(ICAO);")
    conn.close()
    print("Done. Database created:", DB_FILE)


if __name__ == "__main__":
    main()
