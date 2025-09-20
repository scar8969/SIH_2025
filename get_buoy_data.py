# FILE NAME: get_buoy_data.py

import requests
from datetime import datetime
import re
import json
import time
import os

## --- CONFIGURATION: SET THE DATE RANGE TO SCRAPE --- ##
START_YEAR = 2023
END_YEAR = 2024
## -------------------------------------------------- ##

URL_TEMPLATES = {
    "Air Temperature": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=air_temperature&buoy={buoy_id}",
    "Air Pressure": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=air_pressure&buoy={buoy_id}",
    "Relative Humidity": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=humidity&buoy={buoy_id}",
    "Wind Speed": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=wind_speed&buoy={buoy_id}",
    "Rainfall": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=rainfall&buoy={buoy_id}",
    "Radiation In": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=radiationin&buoy={buoy_id}",
    "Water Temperature 0.5m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_0_5m&buoy={buoy_id}",
    "Water Temperature 1m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_001m&buoy={buoy_id}",
    "Water Temperature 5m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_005m&buoy={buoy_id}",
    "Water Temperature 30m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_030m&buoy={buoy_id}",
    "Water Temperature 100m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_100m&buoy={buoy_id}",
    "Water Temperature 200m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_200m&buoy={buoy_id}",
    "Water Temperature 500m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=water_temperature_500m&buoy={buoy_id}",
    "Salinity 0.5m": "https://incois.gov.in/site/datainfo/moored_omnidata_stock.jsp?parameter=salinity_0_5m&buoy={buoy_id}"
}

def scrape_buoy_data(buoy_id, buoy_metadata, output_base_folder):
    print(f"--- Processing Buoy ID: {buoy_id} for years {START_YEAR}-{END_YEAR} ---")
    buoy_specific_folder = os.path.join(output_base_folder, buoy_id)
    os.makedirs(buoy_specific_folder, exist_ok=True)
    all_parameters_data = []

    start_date = datetime(START_YEAR, 1, 1)
    end_date = datetime(END_YEAR + 1, 1, 1)

    for friendly_name, url_template in URL_TEMPLATES.items():
        url = url_template.format(buoy_id=buoy_id)
        print(f"Fetching '{friendly_name}'...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                html_content = response.text
                data_match = re.search(r"data\s*:\s*(\[\[.*?\]\])", html_content, re.DOTALL)

                if data_match:
                    # This is the key fix: Use the 'friendly_name' from the dictionary for reliability
                    parameter_name = friendly_name 
                    time_series_data = json.loads(data_match.group(1))
                    
                    print(f"-> Found {len(time_series_data)} total records. Filtering for {START_YEAR}-{END_YEAR}...")
                    
                    records_in_range = 0
                    for entry in time_series_data:
                        timestamp_ms, value = entry[0], entry[1]
                        observation_dt = datetime.fromtimestamp(timestamp_ms / 1000)
                        
                        if start_date <= observation_dt < end_date:
                            all_parameters_data.append({
                                'parameter_name': parameter_name,
                                'parameter_value': str(value),
                                'observation_date': observation_dt.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            records_in_range += 1
                    
                    print(f"-> Extracted {records_in_range} records from the date range.")
                else:
                    print(f"-> WARNING: Could not find data pattern in HTML for {friendly_name}.")
            else:
                print(f"-> ERROR: Failed fetch for {friendly_name}. Status: {response.status_code}")
            time.sleep(1)
        except Exception as e:
            print(f"-> An error occurred while fetching {friendly_name}: {e}")

    if not all_parameters_data:
        print(f"No data collected for {buoy_id} in the range {START_YEAR}-{END_YEAR}. No SQL file generated.")
        return

    sql_file_path = os.path.join(buoy_specific_folder, 'import_data.sql')
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write("BEGIN TRANSACTION;\n\n")
        f.write(f"INSERT OR IGNORE INTO buoys (buoy_id, buoy_type) VALUES ('{buoy_id}', '{buoy_metadata.get('type', 'N/A')}');\n")
        f.write(f"INSERT INTO buoy_metadata (buoy_id, latitude, longitude) VALUES ('{buoy_id}', {buoy_metadata.get('latitude', 0.0)}, {buoy_metadata.get('longitude', 0.0)});\n\n")
        f.write("-- Parameter Data --\n")
        for record in all_parameters_data:
            p_name = record['parameter_name'].replace("'", "''")
            p_val = record['parameter_value'].replace("'", "''")
            f.write(
                f"INSERT INTO parameter_data (buoy_id, parameter_name, parameter_value, measurement_depth_m, observation_date) "
                f"VALUES ('{buoy_id}', '{p_name}', '{p_val}', 'N/A', '{record['observation_date']}');\n"
            )
        f.write("\nCOMMIT;\n")

    print(f"--- ✅ Successfully created SQL file for {buoy_id} ---")