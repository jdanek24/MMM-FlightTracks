'''This module contains the SQLite conversion script for OpenSky aircraft data'''
__author__ = "jdanek"

import csv
import sqlite3


CSV_FILE = "../data/opensky/aircraft-processed.csv"
DB_FILE = "../data/opensky-aircraft.db"

def main():
    '''Main function'''
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the table structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft (
            icao24 TEXT PRIMARY KEY,
            description TEXT
        )
    ''')
    conn.commit()

    # Open the CSV file and insert data
    with open(CSV_FILE, 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        cursor.executemany('INSERT INTO aircraft VALUES (?, ?)', reader)
    conn.commit()
    conn.close()
    print("Done. Database created:", DB_FILE)

if __name__ == "__main__":
    main()
