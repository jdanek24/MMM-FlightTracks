__author__ = "jdanek"

import csv
import sqlite3


CSV_FILE = "../data/opensky/aircraft-processed.csv"
DB_FILE = "../data/opensky-aircraft.db"

def main():
    # Connect to SQLite database
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
    # print(f"Processing: {CSV_FILE}")
    with open(CSV_FILE, 'r') as f:
        reader = csv.reader(f)
        cursor.executemany('INSERT INTO aircraft VALUES (?, ?)', reader)
    conn.commit()
    conn.close()
    print("Done. Database created:", DB_FILE)

if __name__ == "__main__":
    main()
