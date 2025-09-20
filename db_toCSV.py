# FILE NAME: export_buoy.py

import sqlite3
import pandas as pd
import os

## --- CONFIGURATION --- ##
# 1. Set the path to your database file.
DATABASE_FILE = r"C:\Users\priya\OneDrive\Music\Desktop\SIH_4yr\sih_4y4.db"

# 2. Set the Buoy ID you want to export.
BUOY_ID_TO_EXPORT = "BD14"

# 3. Set the name for the output CSV file.
OUTPUT_CSV_FILE = f"{BUOY_ID_TO_EXPORT}_data.csv"
## ------------------- ##


def export_single_buoy_to_csv():
    """
    Connects to the database, selects all data for a specific buoy,
    and saves it to a CSV file.
    """
    if not os.path.exists(DATABASE_FILE):
        print(f"❌ ERROR: Database file not found at '{DATABASE_FILE}'")
        return

    try:
        con = sqlite3.connect(DATABASE_FILE)
        
        query = f"SELECT * FROM parameter_data WHERE buoy_id = '{BUOY_ID_TO_EXPORT}';"
        print(f"Executing query: {query}")

        # Use Pandas to read the query result directly into a DataFrame
        df = pd.read_sql_query(query, con)

        if df.empty:
            print(f"⚠️ Warning: No data found for buoy ID '{BUOY_ID_TO_EXPORT}'.")
        else:
            # Save the DataFrame to a CSV file
            df.to_csv(OUTPUT_CSV_FILE, index=False)
            print(f"✅ Success! Exported {len(df)} rows for buoy '{BUOY_ID_TO_EXPORT}' to '{OUTPUT_CSV_FILE}'")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'con' in locals():
            con.close()

if __name__ == "__main__":
    export_single_buoy_to_csv()