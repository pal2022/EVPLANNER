import json
import networkx as nx
import math
from math import radians, sin, cos, sqrt, atan2
import time
import os

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on the Earth's surface
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371000 * c
    
    return distance

def calculate_road_distance(node_id, station_lat, station_lon, G):
    """
    Calculate the actual road distance from a node to a charging station
    
    Parameters:
    node_id: node ID
    station_lat: charging station latitude
    station_lon: charging station longitude
    G: road network graph
    
    Returns:
    Actual road distance, if unable to calculate, returns infinity
    """
    min_dist = float('inf')
    closest_node = None
    
    for n, data in G.nodes(data=True):
        if 'y' in data and 'x' in data:
            dist = haversine_distance(station_lat, station_lon, data['y'], data['x'])
            if dist < min_dist:
                min_dist = dist
                closest_node = n
    
    if closest_node is not None:
        try:
            if closest_node in G and node_id in G:
                try:
                    path = nx.shortest_path(G, node_id, closest_node, weight='length')
                    
                    path_length = 0
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        edge_data = G.get_edge_data(u, v)
                        
                        edge_length = 0
                        if edge_data is not None:
                            if isinstance(edge_data, dict):
                                if 'length' in edge_data:
                                    edge_length = float(edge_data['length'])
                                elif len(edge_data) > 0:
                                    first_key = next(iter(edge_data))
                                    first_edge = edge_data[first_key]
                                    if isinstance(first_edge, dict) and 'length' in first_edge:
                                        edge_length = float(first_edge['length'])
                            elif isinstance(edge_data, (int, float)):
                                edge_length = float(edge_data)
                        
                        path_length += edge_length
                    
                    return path_length + min_dist, closest_node
                    
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    return float('inf'), None
        except Exception as e:
            return float('inf'), None
    
    return float('inf'), None

def find_nearest_charging_station(node_id, G, charging_stations):
    """
    Find the nearest charging station to a given node using an optimized direct distance filtering strategy:
    1. Find the charging station with the minimum direct distance
    2. Calculate the actual road distance to this charging station
    3. Use this actual road distance as a threshold to filter all charging stations with direct distance less than this threshold
    4. Calculate the actual road distance to these candidate stations and find the minimum
    """
    node_data = G.nodes[node_id]
    if node_data.get('is_charging_station', False):
        return {
            "nearest_charging_station": {
                "distance": 0,
                "name": node_data.get('station_name', 'Unknown Station'),
                "location": {
                    "latitude": node_data.get('y'),
                    "longitude": node_data.get('x')
                }
            }
        }
    
    node_y = node_data.get('y')
    node_x = node_data.get('x')
    
    if node_y is None or node_x is None:
        return {"nearest_charging_station": None}
    
    min_direct_dist = float('inf')
    closest_station = None
    stations_with_direct_dist = []
    
    for station in charging_stations:
        station_lat = station['location']['latitude']
        station_lon = station['location']['longitude']
        
        direct_dist = haversine_distance(node_y, node_x, station_lat, station_lon)
        stations_with_direct_dist.append((station, direct_dist))
        
        if direct_dist < min_direct_dist:
            min_direct_dist = direct_dist
            closest_station = station
    
    if closest_station is None:
        return {"nearest_charging_station": None}
    
    closest_station_lat = closest_station['location']['latitude']
    closest_station_lon = closest_station['location']['longitude']
    
    road_dist_to_closest, closest_node = calculate_road_distance(
        node_id, closest_station_lat, closest_station_lon, G
    )
    
    nearest_station = closest_station
    min_road_distance = road_dist_to_closest
    
    if road_dist_to_closest < float('inf'):
        for station, direct_dist in stations_with_direct_dist:
            if direct_dist >= road_dist_to_closest:
                continue
                
            if station == closest_station:
                continue
            
            station_lat = station['location']['latitude']
            station_lon = station['location']['longitude']
            
            road_dist, _ = calculate_road_distance(node_id, station_lat, station_lon, G)
            
            if road_dist < min_road_distance:
                min_road_distance = road_dist
                nearest_station = station
    
    if min_road_distance == float('inf'):
        nearest_station = closest_station
        min_road_distance = min_direct_dist
        print(f"      Warning: No road path found for node {node_id}, using direct distance")
    
    if nearest_station is None or min_road_distance > 100000:
        return {"nearest_charging_station": None}
    
    return {
        "nearest_charging_station": {
            "distance": min_road_distance,
            "name": nearest_station.get('name', 'Unknown Station'),
            "location": {
                "latitude": nearest_station.get('location', {}).get('latitude'),
                "longitude": nearest_station.get('location', {}).get('longitude')
            }
        }
    }

def calculate_nearest_stations():
    """
    Calculate the actual road distance from each road node to the nearest charging station
    """
    start_time_total = time.time()
    
    print("Loading road network data...")
    try:
        with open("roads_bc_regions.json", "r") as f:
            roads_data = json.load(f)
        print(f"    ✓ Loaded road network with {len(roads_data['nodes'])} nodes and {len(roads_data['edges'])} edges")
    except Exception as e:
        print(f"    Error loading road network data: {str(e)}")
        return
    
    print("\nLoading charging station data...")
    try:
        with open("charging_stations_bc_regions.json", "r") as f:
            all_charging_stations = json.load(f)
        print(f"    ✓ Loaded {len(all_charging_stations)} charging stations")
    except Exception as e:
        print(f"    Error loading charging station data: {str(e)}")
        return
    
    print("\nCreating road network graph (undirected)...")
    road_network = nx.Graph()
    
    for node_id, node_data in roads_data['nodes'].items():
        road_network.add_node(int(node_id), **node_data)
    
    for edge in roads_data['edges']:
        source = int(edge['source'])
        target = int(edge['target'])
        
        edge_attrs = edge.copy()
        if 'source' in edge_attrs:
            del edge_attrs['source']
        if 'target' in edge_attrs:
            del edge_attrs['target']
        
        road_network.add_edge(source, target, **edge_attrs)
    
    print(f"    ✓ Created graph with {road_network.number_of_nodes()} nodes and {road_network.number_of_edges()} edges")
    
    print("\nAnalyzing graph connectivity...")
    connected_components = list(nx.connected_components(road_network))
    print(f"    Graph has {len(connected_components)} connected components")
    print(f"    Largest component has {len(connected_components[0])} nodes ({len(connected_components[0])/road_network.number_of_nodes()*100:.2f}% of total)")
    
    print("\nCalculating distances to nearest charging stations...")
    print("    This will calculate actual road distances and may take a long time...")
    
    processed_count = 0
    total_nodes = len(road_network.nodes())
    intersections = {}
    start_time = time.time()
    
    all_nodes = list(road_network.nodes())
    
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Processing {total_nodes} nodes sequentially...")
    print(f"Progress updates every 100 nodes, checkpoints every 1000 nodes")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    checkpoint_interval = 1000
    
    for node_id in all_nodes:
        try:
            nearest_info = find_nearest_charging_station(node_id, road_network, all_charging_stations)
            
            if nearest_info["nearest_charging_station"]:
                station_info = nearest_info["nearest_charging_station"]
                nearest_info["nearest_charging_station"] = {
                    "distance": station_info.get("distance"),
                    "name": station_info.get("name", "Unnamed"),
                    "location": {
                        "latitude": station_info.get("location", {}).get("latitude"),
                        "longitude": station_info.get("location", {}).get("longitude")
                    }
                }
                
                intersections[str(node_id)] = nearest_info
            
            processed_count += 1
            
            if processed_count % 100 == 0:
                elapsed = time.time() - start_time
                nodes_per_second = processed_count / elapsed if elapsed > 0 else 0
                estimated_total = total_nodes / nodes_per_second if nodes_per_second > 0 else 0
                remaining = estimated_total - elapsed
                
                hours_remaining = int(remaining // 3600)
                minutes_remaining = int((remaining % 3600) // 60)
                seconds_remaining = int(remaining % 60)
                
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"[{current_time}] Processed: {processed_count}/{total_nodes} nodes ({processed_count/total_nodes*100:.2f}%)")
                print(f"    Speed: {nodes_per_second:.2f} nodes/second")
                print(f"    Est. remaining: {hours_remaining}h {minutes_remaining}m {seconds_remaining}s")
                print(f"    Est. completion: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + remaining))}")
                print("-" * 40)
            
            if processed_count % checkpoint_interval == 0:
                checkpoint_file = os.path.join(output_dir, f"intersections_checkpoint_{processed_count}.json")
                with open(checkpoint_file, "w") as f:
                    json.dump(intersections, f, indent=2)
                print(f"    ✓ Saved checkpoint at {processed_count} nodes to {checkpoint_file}")
                
                sample_node = next(iter(intersections))
                print(f"    Sample data structure for node {sample_node}:")
                print(f"    {json.dumps(intersections[sample_node], indent=4)}")
                print("-" * 40)
                
        except Exception as e:
            print(f"    Error processing node {node_id}: {str(e)}")

    print("\nSaving final results to JSON file...")
    final_file = "intersections_bc_regions.json"
    with open(final_file, "w") as f:
        json.dump(intersections, f, indent=2)
    print(f"    ✓ Saved final results to {final_file}")
    
    total_elapsed = time.time() - start_time_total
    hours = int(total_elapsed // 3600)
    minutes = int((total_elapsed % 3600) // 60)
    seconds = int(total_elapsed % 60)
    
    print("\n" + "="*80)
    print("CALCULATION COMPLETE!")
    print(f"Total time: {hours}h {minutes}m {seconds}s")
    print(f"Processed {processed_count} nodes")
    print(f"Results saved to {final_file}")
    print("="*80)

if __name__ == "__main__":
    print("Starting calculation of nearest charging stations...")
    start_time = time.time()
    
    try:
        calculate_nearest_stations()
        
        total_elapsed = time.time() - start_time
        hours = int(total_elapsed // 3600)
        minutes = int((total_elapsed % 3600) // 60)
        seconds = int(total_elapsed % 60)
        
        print(f"\nScript execution complete! Total time: {hours}h {minutes}m {seconds}s")
    except Exception as e:
        print(f"\nError occurred during execution: {str(e)}")
        import traceback
        traceback.print_exc()