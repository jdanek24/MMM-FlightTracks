'''This module contains the SQLite conversion script for vradarserver airline data'''
__author__ = "jdanek"

import os
import sqlite3
import pandas as pd

CSV_FOLDER = "../data/vradarserver/standing-data/airlines"
DB_FILE = "../data/vradarserver-airline.db"

def get_csv_files(folder):
    '''Recursively collect all CSV files'''
    csv_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files


def main():
    '''Main function'''
    conn = sqlite3.connect(DB_FILE)

    csv_files = get_csv_files(CSV_FOLDER)
    print(f"Found {len(csv_files)} CSV files.")

    first = True
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df_selected = df[['Code', 'Name']]

            # Write to SQLite
            df_selected.to_sql(
                "airline",
                conn,
                if_exists="replace" if first else "append",
                index=False
            )
            first = False

        except Exception as e:
            print(f"Error processing {file}: {e}")

    conn.execute("CREATE INDEX idx_name ON airline(Name);")
    conn.close()
    print("Done. Database created:", DB_FILE)


if __name__ == "__main__":
    main()
