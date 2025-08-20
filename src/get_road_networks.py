import requests
import json
import networkx as nx
import math
from math import radians, sin, cos, sqrt, atan2
import os
import time
import xml.etree.ElementTree as ET
from shapely.geometry import LineString

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

def get_roads_from_osm(bbox, cell_name):
    """
    Get road network from OpenStreetMap using direct API
    Only include major road types and specific service road subtypes
    """
    print(f"    Querying roads for {cell_name} region...")
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:xml][timeout:180];
    (
        way["highway"="motorway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="trunk"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="primary"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="secondary"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="tertiary"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="motorway_link"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="trunk_link"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="primary_link"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="secondary_link"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="tertiary_link"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="service"]["service"="rest_area"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="service"]["service"="fuel"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        way["highway"="service"]["service"="parking"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    (._;>;);
    out body;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    
    if response.status_code != 200:
        print(f"    Error: Failed to retrieve road data for {cell_name} region")
        return None
    
    return response.text

def get_roads_direct(bbox, grid_size=2):
    """
    Get road network directly from OSM API using XML
    Divides the bounding box into a grid_size x grid_size grid of smaller boxes
    """
    print(f"Fetching road network for bbox: {bbox} using direct OSM API")
    
    south, west, north, east = bbox
    
    lat_step = (north - south) / grid_size
    lon_step = (east - west) / grid_size
    
    G = nx.MultiDiGraph()
    
    total_cells = grid_size * grid_size
    processed_cells = 0
    
    for i in range(grid_size):
        for j in range(grid_size):
            cell_south = south + i * lat_step
            cell_north = south + (i + 1) * lat_step
            cell_west = west + j * lon_step
            cell_east = west + (j + 1) * lon_step
            
            cell_bbox = [cell_south, cell_west, cell_north, cell_east]
            cell_name = f"Cell {i*grid_size + j + 1}/{total_cells}"
            
            road_data = get_roads_from_osm(cell_bbox, cell_name)
            
            if road_data:
                G = process_osm_roads(road_data, G)
            
            processed_cells += 1
            print(f"    Processed {processed_cells}/{total_cells} cells")
    
    return G

def process_osm_roads(osm_data, G=None):
    """
    Process OSM road data and add to NetworkX graph
    """
    if G is None:
        G = nx.MultiDiGraph()
    
    try:
        root = ET.fromstring(osm_data)
        
        nodes = {}
        for node in root.findall(".//node"):
            node_id = int(node.get('id'))
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            nodes[node_id] = (lat, lon)
        
        for way in root.findall(".//way"):
            way_id = way.get('id')
            
            attrs = {
                'osmid': way_id,
                'oneway': False,
                'highway': None,
                'reversed': False,
            }
            
            for tag in way.findall("tag"):
                key = tag.get('k')
                value = tag.get('v')
                
                if key == 'highway':
                    attrs['highway'] = value
                elif key == 'oneway' and value == 'yes':
                    attrs['oneway'] = True
                elif key in ['name', 'lanes', 'ref', 'maxspeed', 'bridge', 'surface']:
                    attrs[key] = value
            
            if attrs['highway'] is None:
                continue
            
            way_nodes = []
            for nd in way.findall("nd"):
                ref = int(nd.get('ref'))
                way_nodes.append(ref)
            
            for node_id in way_nodes:
                if node_id in nodes:
                    lat, lon = nodes[node_id]
                    if node_id not in G:
                        G.add_node(node_id, y=lat, x=lon)
            
            for i in range(len(way_nodes) - 1):
                u = way_nodes[i]
                v = way_nodes[i + 1]
                
                if u not in nodes or v not in nodes:
                    continue
                
                u_lat, u_lon = nodes[u]
                v_lat, v_lon = nodes[v]
                distance = haversine_distance(u_lat, u_lon, v_lat, v_lon)
                
                speed_km_h = 50  
                if attrs['highway'] == 'motorway':
                    speed_km_h = 100
                elif attrs['highway'] == 'trunk':
                    speed_km_h = 80
                elif attrs['highway'] == 'primary':
                    speed_km_h = 60
                elif attrs['highway'] == 'secondary':
                    speed_km_h = 50
                elif attrs['highway'] == 'tertiary':
                    speed_km_h = 40
                elif attrs['highway'] == 'residential':
                    speed_km_h = 30
                
                speed_m_s = speed_km_h * 1000 / 3600  
                travel_time = distance / speed_m_s
                
                edge_data = attrs.copy()
                edge_data['length'] = distance
                edge_data['travel_time'] = travel_time
                
                G.add_edge(u, v, **edge_data)
                
                if not attrs['oneway']:
                    reverse_data = attrs.copy()
                    reverse_data['length'] = distance
                    reverse_data['travel_time'] = travel_time
                    reverse_data['reversed'] = True
                    G.add_edge(v, u, **reverse_data)
        
        for node in G.nodes():
            G.nodes[node]['street_count'] = len(list(G.neighbors(node)))
        
        return G
    
    except Exception as e:
        print(f"Error processing OSM data: {str(e)}")
        import traceback
        traceback.print_exc()
        return G

def connect_charging_stations_to_road_network(G, charging_stations_file):
    """
    Add charging stations as nodes to the road network and connect them to the nearest road nodes
    
    Parameters:
    G : networkx.Graph
        Road network graph
    charging_stations_file : str
        Path to the JSON file containing charging station data
    
    Returns:
    networkx.Graph
        Road network graph with added charging station nodes and connections
    """

    print("\nLoading charging stations data from local file...")
    try:
        with open(charging_stations_file, 'r') as f:
            all_charging_stations = json.load(f)
        print(f"    ✓ Loaded {len(all_charging_stations)} charging stations from {charging_stations_file}")
    except FileNotFoundError:
        print(f"    ✗ Error: File {charging_stations_file} not found")
        return G
    except json.JSONDecodeError:
        print(f"    ✗ Error: File {charging_stations_file} contains invalid JSON")
        return G
    
    charging_stations_already_added = any(
        data.get('is_charging_station', False) 
        for _, data in G.nodes(data=True)
    )
    
    if charging_stations_already_added:
        print("    ✓ Charging stations already added to the road network, skipping...")
        return G
    
    print("\nAdding charging stations as nodes to the road network...")
    
    charging_station_node_id_start = max(G.nodes()) + 1 if G.nodes else 1000000
    
    added_stations = 0
    
    for i, station in enumerate(all_charging_stations):
        station_node_id = charging_station_node_id_start + i
        
        station_lat = station['location']['latitude']
        station_lon = station['location']['longitude']
        
        G.add_node(
            station_node_id, 
            y=station_lat, 
            x=station_lon, 
            is_charging_station=True,
            station_name=station.get('name', "Unnamed Station")
        )
        
        min_dist = float('inf')
        closest_node = None
        
        for node_id, data in G.nodes(data=True):
            if data.get('is_charging_station', False):
                continue
            
            if 'y' in data and 'x' in data:
                dist = haversine_distance(
                    station_lat, station_lon,
                    data['y'], data['x']
                )
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node_id
        
        if closest_node is not None:
            G.add_edge(
                station_node_id, 
                closest_node, 
                length=min_dist,
                highway='service',
                oneway=False,
                is_charging_connection=True
            )
            
            if isinstance(G, nx.MultiDiGraph):
                G.add_edge(
                    closest_node,
                    station_node_id,
                    length=min_dist,
                    highway='service',
                    oneway=False,
                    reversed=True,
                    is_charging_connection=True
                )
                
            added_stations += 1
    
    print(f"    ✓ Added {added_stations} charging stations as nodes to the road network")
    print(f"    ✓ Road network now has {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    return G

def generate_roads_data():
    """
    Generate road network data for BC regions
    """
    print("Generating road network data for BC regions...")
    start_time = time.time()
    
    southwest = [49.0, -123.3, 49.9, -121.7]
    northeast = [55.0, -124.0, 58.0, -120.0]
    
    print("\nFetching road network for Southwest region...")
    southwest_G = get_roads_direct(southwest, grid_size=3)
    print(f"    ✓ Created graph with {southwest_G.number_of_nodes()} nodes and {southwest_G.number_of_edges()} edges")
    
    print("\nFetching road network for Northeast region...")
    northeast_G = get_roads_direct(northeast, grid_size=3)
    print(f"    ✓ Created graph with {northeast_G.number_of_nodes()} nodes and {northeast_G.number_of_edges()} edges")
    
    print("\nCombining road networks...")
    combined_G = nx.compose(southwest_G, northeast_G)
    print(f"    ✓ Combined graph has {combined_G.number_of_nodes()} nodes and {combined_G.number_of_edges()} edges")
    
    charging_stations_file = "charging_stations_bc_regions.json"
    combined_G = connect_charging_stations_to_road_network(combined_G, charging_stations_file)
    
    print("\nSaving road network data to JSON file...")
    roads_json = {
        "directed": True,
        "multigraph": True,
        "graph": {
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_with": "Direct OSM API with charging stations",
            "crs": "epsg:4326",
            "simplified": True
        },
        "nodes": {},
        "edges": []
    }

    for node_id, data in combined_G.nodes(data=True):
        node_data = {
            "y": data.get("y"),
            "x": data.get("x"),
            "street_count": data.get("street_count", 0)
        }
        
        if data.get("is_charging_station", False):
            node_data["is_charging_station"] = True
            node_data["station_name"] = data.get("station_name", "")
            
        roads_json["nodes"][str(node_id)] = node_data

    for u, v, data in combined_G.edges(data=True):
        edge = {
            "source": str(u),
            "target": str(v),
            "key": 0, 
            "length": round(float(data.get('length', 0)), 3),
            "highway": data.get('highway', ''),
            "travel_time": data.get('travel_time', 0),
            "geometry": data.get('geometry', '')
        }
        
        if 'osmid' in data:
            if isinstance(data['osmid'], str):
                try:
                    if ',' in data['osmid']:
                        edge['osmid'] = [int(id.strip()) for id in data['osmid'].split(',')]
                    else:
                        edge['osmid'] = int(data['osmid'])
                except ValueError:
                    edge['osmid'] = data['osmid']
            else:
                edge['osmid'] = data['osmid']
        
        if 'oneway' in data:
            edge['oneway'] = bool(data['oneway'])
        
        if 'lanes' in data:
            edge['lanes'] = data['lanes']
        
        if 'ref' in data:
            edge['ref'] = data['ref']
        
        if 'name' in data:
            edge['name'] = data['name']
        
        if 'maxspeed' in data:
            edge['maxspeed'] = data['maxspeed']
        
        if 'reversed' in data:
            edge['reversed'] = bool(data['reversed'])
        
        if 'bridge' in data:
            edge['bridge'] = data['bridge']
        
        if data.get("is_charging_connection", False):
            edge["is_charging_connection"] = True
        
        roads_json["edges"].append(edge)

    with open("roads_bc_regions.json", "w") as f:
        json.dump(roads_json, f, indent=2)
    print(f"    ✓ Saved road network data to roads_bc_regions.json")
    
    total_elapsed = time.time() - start_time
    hours = int(total_elapsed // 3600)
    minutes = int((total_elapsed % 3600) // 60)
    seconds = int(total_elapsed % 60)
    
    charging_station_count = sum(1 for _, data in combined_G.nodes(data=True) if data.get('is_charging_station', False))
    
    print("\n" + "="*80)
    print("ROAD NETWORK DATA GENERATION COMPLETE!")
    print(f"Total nodes: {combined_G.number_of_nodes()}")
    print(f"Total edges: {combined_G.number_of_edges()}")
    print(f"Total charging stations: {charging_station_count}")
    print(f"- Southwest region: {southwest_G.number_of_nodes()} nodes, {southwest_G.number_of_edges()} edges")
    print(f"- Northeast region: {northeast_G.number_of_nodes()} nodes, {northeast_G.number_of_edges()} edges")
    print(f"Total time: {hours}h {minutes}m {seconds}s")
    print("Generated files:")
    print("- roads_bc_regions.json")
    print("="*80)
    
    return combined_G

if __name__ == "__main__":
    print("Starting BC regions road network data generation...")
    start_time = time.time()
    
    try:
        generate_roads_data()
        
        total_elapsed = time.time() - start_time
        hours = int(total_elapsed // 3600)
        minutes = int((total_elapsed % 3600) // 60)
        seconds = int(total_elapsed % 60)
        
        print(f"\nScript execution complete! Total time: {hours}h {minutes}m {seconds}s")
    except Exception as e:
        print(f"\nError occurred during execution: {str(e)}")
        import traceback
        traceback.print_exc() 