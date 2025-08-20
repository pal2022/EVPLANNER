import requests
import json
import math
from math import radians, sin, cos, sqrt, atan2
import os
import time

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371000 * c  
    
    return distance

def get_charging_stations(bbox):
    """
    Get charging station data from Overpass API for the specified bounding box
    bbox: bounding box coordinates [south, west, north, east]
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json][timeout:25];
    (
        node["amenity"="charging_station"]
            ({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["amenity"="charging_station"]
            ({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        relation["amenity"="charging_station"]
            ({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    
    if response.status_code != 200:
        print(f"Error: Failed to retrieve charging station data")
        return {"elements": []}
    
    return response.json()

def process_charging_stations(data, region_name):
    """
    Process charging station data from Overpass API
    Keep only essential information and remove unnecessary tags
    """
    stations = []
    
    for element in data.get('elements', []):
        if element.get('type') == 'node' and element.get('tags', {}).get('amenity') == 'charging_station':
            station = {
                'name': element.get('tags', {}).get('name', "Unnamed Station"),
                'location': {
                    'latitude': element.get('lat'),
                    'longitude': element.get('lon')
                },
                'tags': {
                    'amenity': 'charging_station'
                },
                'region': region_name  
            }
            
            stations.append(station)
    
    return stations

def generate_charging_stations_data():
    """
    Generate charging station data for BC regions
    """
    print("Generating charging station data for BC regions...")
    start_time = time.time()
    
    southwest = [49.0, -123.3, 49.9, -121.7] 
    northeast = [55.0, -124.0, 58.0, -120.0]  
    
    print("\nFetching charging stations for Southwest region...")
    bc_southwest_stations_data = get_charging_stations(southwest)
    bc_southwest_stations = process_charging_stations(bc_southwest_stations_data, "southwest")
    print(f"    ✓ Found {len(bc_southwest_stations)} charging stations in Southwest region")
    
    print("\nFetching charging stations for Northeast region...")
    bc_northeast_stations_data = get_charging_stations(northeast)
    bc_northeast_stations = process_charging_stations(bc_northeast_stations_data, "northeast")
    print(f"    ✓ Found {len(bc_northeast_stations)} charging stations in Northeast region")
    
    all_charging_stations = bc_southwest_stations + bc_northeast_stations
    total_stations = len(all_charging_stations)
    print(f"\nTotal charging stations found: {total_stations}")
    
    print("\nSaving charging station data to JSON file...")
    with open("charging_stations_bc_regions.json", "w") as f:
        json.dump(all_charging_stations, f, indent=2)
    print(f"    ✓ Saved {total_stations} charging stations to charging_stations_bc_regions.json")
    
    total_elapsed = time.time() - start_time
    hours = int(total_elapsed // 3600)
    minutes = int((total_elapsed % 3600) // 60)
    seconds = int(total_elapsed % 60)
    
    print("\n" + "="*80)
    print("CHARGING STATION DATA GENERATION COMPLETE!")
    print(f"Total charging stations: {total_stations}")
    print(f"- BC Southwest region: {len(bc_southwest_stations)} stations")
    print(f"- BC Northeast region: {len(bc_northeast_stations)} stations")
    print(f"Total time: {hours}h {minutes}m {seconds}s")
    print("Generated files:")
    print("- charging_stations_bc_regions.json")
    print("="*80)
    
    return all_charging_stations

if __name__ == "__main__":
    print("Starting BC regions charging station data generation...")
    start_time = time.time()
    
    try:
        generate_charging_stations_data()
        
        total_elapsed = time.time() - start_time
        hours = int(total_elapsed // 3600)
        minutes = int((total_elapsed % 3600) // 60)
        seconds = int(total_elapsed % 60)
        
        print(f"\nScript execution complete! Total time: {hours}h {minutes}m {seconds}s")
    except Exception as e:
        print(f"\nError occurred during execution: {str(e)}")
        import traceback
        traceback.print_exc() 