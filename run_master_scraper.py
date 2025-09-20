# FILE NAME: run_master_scraper.py

import requests
import json
import time
import os

# Import the scraping function from your other file
from get_buoy_data import scrape_buoy_data

## --- CONFIGURATION: SET YOUR OUTPUT FOLDER NAME HERE --- ##
OUTPUT_FOLDER_NAME = "SIH_4yr" 
## --------------------------------------------------- ##

def get_all_buoy_metadata_from_api():
    """
    Calls the INCOIS API to get metadata for all available buoys.
    """
    api_url = "https://incois.gov.in/OON/fetchMooredBuoyData.jsp"
    print(f"Fetching master buoy list from API: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            all_buoy_metadata = response.json()
            print(f"✅ Success! Found metadata for {len(all_buoy_metadata)} buoys.")
            return all_buoy_metadata
        else:
            print(f"❌ Error fetching buoy list: API returned status code {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ A critical error occurred while fetching the buoy list: {e}")
        return []

# --- Main Automation Script ---
if __name__ == "__main__":
    
    # This part creates the full path to your new folder in the parent directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)
    output_folder_path = os.path.join(parent_directory, OUTPUT_FOLDER_NAME)
    print(f"Results will be saved in: {output_folder_path}")
    
    buoys_to_process = get_all_buoy_metadata_from_api()

    if buoys_to_process:
        print("\nStarting automated scraping for all buoys...")
        start_time = time.time()

        for buoy_meta in buoys_to_process:
            buoy_id = buoy_meta.get('buoyId')
            if not buoy_id:
                print("Skipping a record with no buoyId.")
                continue

            try:
                scrape_buoy_data(buoy_id, buoy_meta, output_base_folder=output_folder_path)
            except Exception as e:
                print(f"A critical error occurred while processing {buoy_id}: {e}")

        end_time = time.time()
        print("\n----------------------------------------------------")
        print(f"✅ Automation complete. Total time taken: {end_time - start_time:.2f} seconds.")
        print(f"Check the '{output_folder_path}' folder for your results.")
        print("----------------------------------------------------")
    else:
        print("\nCould not retrieve buoy list. Halting automation.")