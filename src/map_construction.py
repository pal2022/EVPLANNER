import requests
import json
import folium
from folium import plugins
import osmnx as ox
import networkx as nx
import math
from math import radians, sin, cos, sqrt, atan2
from shapely import wkt
import os
from queue import PriorityQueue
import re
import map_renderer


SAFETY_FACTOR = 0.85 # Safety margin factor for available SOC when planning detours


# Global variables for caching data to avoid repeated overloading
_cached_road_network = None
_cached_charging_stations = None
_cached_intersections = None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # This is needed for edge length when OSM 'length' is not available,
    # and to measure distance to the charging stations.

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371000 * c
    
    return distance

def find_nearest_charging_station(node_lat, node_lon, charging_stations):
    """
    Find the nearest charging station to a given node usinng the Haversine distance
    """
    min_distance = float('inf')
    nearest_station = None
    
    for station in charging_stations:
        station_lat = station['location']['latitude']
        station_lon = station['location']['longitude']
        
        distance = haversine_distance(node_lat, node_lon, station_lat, station_lon)
        
        if distance < min_distance:
            min_distance = distance
            nearest_station = {
                'name': station['name'],
                'location': station['location'],
                'distance': distance
            }
    
    return nearest_station

def filter_similar_routes(paths, costs, socs, time_diff_threshold=0.02):
    """
    Filter out routes that have less than 2 percentage time difference.
    """
    if not paths or len(paths) <= 1:
        return paths, costs, socs
    
    sorted_indices = sorted(range(len(costs)), key=lambda i: costs[i]['time'])
    sorted_paths = [paths[i] for i in sorted_indices]
    sorted_costs = [costs[i] for i in sorted_indices]
    sorted_socs = [socs[i] for i in sorted_indices]
    
    filtered_indices = [sorted_indices[0]]
    last_kept_time = sorted_costs[0]['time']
    
    for i in range(1, len(sorted_indices)):
        current_time = sorted_costs[i]['time']
        time_diff_ratio = (current_time - last_kept_time) / last_kept_time
        
        if time_diff_ratio >= time_diff_threshold:
            filtered_indices.append(sorted_indices[i])
            last_kept_time = current_time
    
    filtered_paths = [paths[i] for i in filtered_indices]
    filtered_costs = [costs[i] for i in filtered_indices]
    filtered_socs = [socs[i] for i in filtered_indices]
    
    print(f"Filtered routes from {len(paths)} to {len(filtered_paths)} (removed {len(paths) - len(filtered_paths)} similar routes)")
    
    return filtered_paths, filtered_costs, filtered_socs

def find_pareto_paths(G, nearest_stations, start_node, end_node, max_paths, initial_soc, threshold_soc, energy_consumption):
    """
    Find Pareto-optimal paths using A* search with state space exploration.
    Optimizes for both travel time and charging safety (distance to nearest charging station).
    """

    def heuristic(node):
        """
        Estimate remaining time to goal using Euclidean distance and average speed
        This is the heuristic function for A* algorithm.
        """
        try:
            node_y = G.nodes[node]['y']
            node_x = G.nodes[node]['x']
            end_y = G.nodes[end_node]['y']
            end_x = G.nodes[end_node]['x']
            
            dist_degrees = ((node_y - end_y)**2 + (node_x - end_x)**2)**0.5
            
            dist_meters = dist_degrees * 111000
            
            avg_speed = 60 * 1000 / 3600  
            time_estimate = dist_meters / avg_speed
            
            return time_estimate
        except:
            return 0  
    
    # Initialize the priority queue for A* search
    # The frontier represents the set of nodes to be explored in the A* search.
    # Each element in the frontier is a tuple of (f_score, total_time, max_charging_dist, node, path)
    # Nodes with lower combined cost are explored first, ensuring we prioritize efficient and safe paths toward the destination.
    frontier = PriorityQueue()
    
    #Calculate the initial heuristic score (h_score) for the start node.
    h_score = heuristic(start_node)
    f_score = h_score
    
    frontier.put((f_score, 0, 0, start_node, [start_node]))
    
    pareto_paths = []
    pareto_costs = []
    remaining_socs = []
    
    visited = {}
    
    infeasible_path_counter = 0
    
    infeasible_paths_info = []
    
    unique_charging_stations = set()
    
    def is_dominated(costs, existing_costs_list, tolerance=0.05):
        """Check if costs are dominated by any existing costs with tolerance"""
        for existing_costs in existing_costs_list:
            if (existing_costs[0] * (1 + tolerance) <= costs[0] and 
                existing_costs[1] * (1 + tolerance) <= costs[1]):
                return True
        return False
    
    def is_state_dominated(node, time, max_dist):
        """Check if current state is dominated by previously visited states"""
        if node not in visited:
            return False
        
        for v_time, v_max_dist in visited[node]:
            if v_time <= time and v_max_dist <= max_dist:
                return True
        return False
    
    def update_visited(node, time, max_dist):
        """Update visited states, removing dominated states"""
        if node not in visited:
            visited[node] = []
            visited[node].append((time, max_dist))
            return
        
        new_states = [(time, max_dist)]
        
        for v_time, v_max_dist in visited[node]:
            if not (time <= v_time and max_dist <= v_max_dist):
                new_states.append((v_time, v_max_dist))
        
        visited[node] = new_states
    
    # A* search loop
    # max_paths is the maximum number of Pareto-optimal paths to find and this variable can be changed
    while not frontier.empty() and len(pareto_paths) < max_paths:
        f_score, total_time, max_charging_dist, current, path = frontier.get()
        
        if is_state_dominated(current, total_time, max_charging_dist):
            continue
        
        update_visited(current, total_time, max_charging_dist)
        
        if current == end_node:
            remaining_soc = calculate_remaining_soc(path, G, initial_soc, energy_consumption)
            
            if remaining_soc < threshold_soc:
                infeasible_path_counter += 1
                
                available_soc = SAFETY_FACTOR * (initial_soc - threshold_soc)
                max_distance_km = available_soc / energy_consumption
                max_distance_m = max_distance_km * 1000
                
                cumulative_distance = 0
                last_reachable_node_idx = 0
                
                for j in range(len(path) - 1):
                    try:
                        edge_data = G.edges[path[j], path[j+1], 0]
                        
                        if 'length' in edge_data:
                            distance = edge_data['length']  
                        else:
                            start_y, start_x = G.nodes[path[j]]['y'], G.nodes[path[j]]['x']
                            end_y, end_x = G.nodes[path[j+1]]['y'], G.nodes[path[j+1]]['x']
                            distance = haversine_distance(start_y, start_x, end_y, end_x)
                        
                        cumulative_distance += distance
                        
                        if cumulative_distance > max_distance_m:
                            break
                        
                        last_reachable_node_idx = j + 1
                        
                    except Exception as e:
                        continue
                
                last_node_info = ""
                nearest_charging_station_info = ""
                station_id = None  
                
                if last_reachable_node_idx < len(path):
                    last_node = path[last_reachable_node_idx]
                    try:
                        node_data = G.nodes[last_node]
                        if 'y' in node_data and 'x' in node_data:
                            last_node_info = f"Coordinates: ({node_data['y']:.6f}, {node_data['x']:.6f})"
                            
                            try:
                                with open('charging_stations_bc_regions.json', 'r') as f:
                                    charging_stations = json.load(f)
                                
                                nearest_station = find_nearest_charging_station(
                                    node_data['y'], node_data['x'], charging_stations)
                                
                                if nearest_station:
                                    station_name = nearest_station['name']
                                    station_lat = nearest_station['location']['latitude']
                                    station_lon = nearest_station['location']['longitude']
                                    nearest_charging_station_info = f"{station_name} (Location: {station_lat:.6f}, {station_lon:.6f})"
                                    
                                    station_id = f"{station_name}|{station_lat}|{station_lon}"
                                    unique_charging_stations.add(station_id)
                            except Exception as e:
                                print(f"Error finding nearest charging station: {str(e)}")
                    except:
                        pass
                
                infeasible_paths_info.append({
                    'path_index': infeasible_path_counter,
                    'remaining_soc': remaining_soc,
                    'threshold_soc': threshold_soc,
                    'total_nodes': len(path),
                    'last_reachable_node_idx': last_reachable_node_idx,
                    'last_node_info': last_node_info,
                    'nearest_charging_station': nearest_charging_station_info,
                    'station_id': station_id
                })
                
                print(f"Path #{infeasible_path_counter} not feasible")
                print(f"Remaining: {remaining_soc:.1f}%")
                print(f"Threshold: {threshold_soc}%")
                print(f"Total Nodes: {len(path)}")
                print(f"Last Node Visited: #{last_reachable_node_idx+1}")
                if last_node_info:
                    print(f"Last Node Info: {last_node_info}")
                if nearest_charging_station_info:
                    print(f"Nearest Charging Station to Last Node: {nearest_charging_station_info}")
                print("")  
                
                continue
            
            costs = (total_time, max_charging_dist)
            
            if not is_dominated(costs, pareto_costs):
                non_dominated_idx = []
                non_dominated_costs = []
                non_dominated_socs = []
                for i, existing_costs in enumerate(pareto_costs):
                    if not (costs[0] <= existing_costs[0] and costs[1] <= existing_costs[1] and 
                           (costs[0] < existing_costs[0] or costs[1] < existing_costs[1])):
                        non_dominated_idx.append(i)
                        non_dominated_costs.append(existing_costs)
                        non_dominated_socs.append(remaining_socs[i])
                
                pareto_paths = [pareto_paths[i] for i in non_dominated_idx]
                pareto_costs = non_dominated_costs
                remaining_socs = non_dominated_socs
                
                pareto_paths.append(path)
                pareto_costs.append(costs)
                remaining_socs.append(remaining_soc)
                
                continue
        
        for neighbor in G.neighbors(current):
            if neighbor in path:
                continue
                
            edge_data = G.edges[current, neighbor, 0]
            
            if 'travel_time' in edge_data:
                travel_time = edge_data['travel_time']
            else:
                edge_length = edge_data.get('length', 0)  
                
                road_type = edge_data.get('highway', 'residential')
                if isinstance(road_type, list):
                    road_type = road_type[0] if road_type else 'residential'
                
                speed = {
                    'motorway': 100,     
                    'trunk': 80,         
                    'primary': 50,        
                    'secondary': 50,      
                    'tertiary': 50,       
                }.get(road_type, 30)     
                
                speed_ms = speed * 1000 / 3600
                
                travel_time = edge_length / speed_ms if speed_ms > 0 else 60  
            
            new_total_time = total_time + travel_time
            
            if neighbor in nearest_stations:
                charging_dist = nearest_stations[neighbor]['distance']
            else:
                charging_dist = float('inf')
            new_max_charging_dist = max(max_charging_dist, charging_dist)
            
            if is_state_dominated(neighbor, new_total_time, new_max_charging_dist):
                continue
            
            h_score = heuristic(neighbor)
            
            time_norm = 3600  
            dist_norm = 10000  
            
            if new_max_charging_dist <= 10000:
                safety_score = new_max_charging_dist / 10000
            else:
                excess = new_max_charging_dist - 10000
                safety_score = 1.0 + 0.5 * math.log10(1 + excess / 10000)  
            
            f_score = ((new_total_time + h_score) / time_norm) + safety_score
            
            new_path = path + [neighbor]
            frontier.put((f_score, new_total_time, new_max_charging_dist, neighbor, new_path))
    
    if len(pareto_paths) == 0 and infeasible_paths_info:
        stations_dict = {}
        for info in infeasible_paths_info:
            if info['station_id']:
                if info['station_id'] not in stations_dict:
                    stations_dict[info['station_id']] = {
                        'station_info': info['nearest_charging_station'],
                        'paths': []
                    }
                stations_dict[info['station_id']]['paths'].append(info['path_index'])
        
        print("\n===== Summary of Nearest Charging Stations =====")
        print(f"Found {len(stations_dict)} unique charging stations near the last reachable nodes:")
        
        for i, (station_id, data) in enumerate(stations_dict.items()):
            print(f"\n{i+1}. {data['station_info']}")
            print(f"   Found in paths: {', '.join(map(str, data['paths']))}")
        
        print("\n=================================================")
    
    formatted_costs = []
    for time_cost, safety_cost in pareto_costs:
        formatted_costs.append({'time': time_cost, 'safety': safety_cost})
    
    sorted_indices = sorted(range(len(formatted_costs)), key=lambda i: formatted_costs[i]['time'])
    paths = [pareto_paths[i] for i in sorted_indices]
    costs = [formatted_costs[i] for i in sorted_indices]
    socs = [remaining_socs[i] for i in sorted_indices]
    
    if len(paths) > max_paths:
        paths = paths[:max_paths]
        costs = costs[:max_paths]
        socs = socs[:max_paths]
    
    paths, costs, socs = filter_similar_routes(paths, costs, socs)

    print("\nPareto-optimal paths:")
    for i, (path, cost) in enumerate(zip(paths, costs)):
        remaining_soc = calculate_remaining_soc(path, G, initial_soc, energy_consumption)
        
        safety_km = cost['safety'] / 1000
        print(f"Path {i+1}: Travel time: {cost['time']:.1f}s, Safety: {safety_km:.2f}km, Remaining SOC: {remaining_soc:.1f}%")
    
    return paths, costs, infeasible_paths_info, socs

def calculate_charging_time(current_soc, target_soc=100, charging_rate=3.0):
    """
    Calculate the time needed to charge from current SOC to target SOC(100)
    """
    if current_soc >= target_soc:
        return 0
    
    soc_to_charge = target_soc - current_soc
    charging_time_minutes = soc_to_charge / charging_rate
    charging_time_seconds = charging_time_minutes * 60
    
    return charging_time_seconds


def test_route_planning(start_address, end_address, initial_soc, threshold_soc, energy_consumption):
    """
    Test route planning with given parameters and return the results.
    This function is the main entry point for the route planning process. It loads necessary data, 
    geocodes the start and end addresses, and then calls the route_planning function to find the optimal paths. 
    
    """
    try:
        road_network, charging_stations, intersections = load_bc_province_data()
        
        if road_network and charging_stations and intersections:
            print(f"Planning route from {start_address} to {end_address}")
            print(f"Battery settings: initial SOC: {initial_soc}%, threshold: {threshold_soc}%, consumption: {energy_consumption}%/km")
            
            if 'crs' not in road_network.graph:
                road_network.graph['crs'] = 'epsg:4326'
            
            print(f"\nGeocoding start address: {start_address}")
            start_coords = geocode_address(start_address + ", BC, Canada")
            print(f"Geocoding end address: {end_address}")
            end_coords = geocode_address(end_address + ", BC, Canada")
            
            if not start_coords or not end_coords:
                print("Error: Could not geocode one or both addresses.")
                return None, None, None, None, "invalid_address", None
            
            start_lat, start_lon = start_coords
            end_lat, end_lon = end_coords
            
            print(f"Start coordinates: ({start_lat}, {start_lon})")
            print(f"End coordinates: ({end_lat}, {end_lon})")
            
            print("\nFinding nearest nodes in the road network...")
            start_node, start_dist = find_nearest_node(road_network, start_lat, start_lon)
            end_node, end_dist = find_nearest_node(road_network, end_lat, end_lon)
            
            if start_node is None or end_node is None:
                print("Error: Could not find nodes in the road network close to the provided coordinates.")
                return None, None, None, None, "invalid_address", None
            
            print(f"Start node: {start_node} (distance: {start_dist:.2f}m)")
            print(f"End node: {end_node} (distance: {end_dist:.2f}m)")
            
            nearest_stations = {}
            road_network_nodes = set(road_network.nodes())
            
            for node_id, data in intersections.items():
                node_id_int = int(node_id) if node_id.isdigit() else node_id
                
                if node_id_int not in road_network_nodes:
                    continue
                
                if 'nearest_charging_station' in data and data['nearest_charging_station'] is not None:
                    nearest_stations[node_id_int] = {
                        'distance': data['nearest_charging_station']['distance'],
                        'station': {
                            'name': data['nearest_charging_station']['name'],
                            'lat': data['nearest_charging_station']['location']['latitude'],
                            'lon': data['nearest_charging_station']['location']['longitude']
                        }
                    }
            
            print(f"Prepared nearest stations data for {len(nearest_stations)} nodes")
            
            print("Checking if start and end nodes are connected...")
            try:
                test_path = nx.shortest_path(road_network, start_node, end_node)
                print(f"Start and end nodes are connected with a path")
            except nx.NetworkXNoPath:
                print("No path exists between start and end nodes!")
                connected_components = list(nx.weakly_connected_components(road_network))
                start_component = None
                end_component = None
                
                for i, component in enumerate(connected_components):
                    if start_node in component:
                        start_component = i
                    if end_node in component:
                        end_component = i
                
                print(f"Start node is in component {start_component}, end node is in component {end_component}")
                print(f"Total number of components: {len(connected_components)}")
                
                if start_component is not None and end_component is not None and start_component != end_component:
                    print("Start and end nodes are in different connected components!")
                    largest_component = max(connected_components, key=len)
                    print(f"Largest component has {len(largest_component)} nodes")
                    
                    new_start_node = None
                    new_end_node = None
                    min_start_dist = float('inf')
                    min_end_dist = float('inf')
                    
                    for node in largest_component:
                        node_lat = road_network.nodes[node]['y']
                        node_lon = road_network.nodes[node]['x']
                        
                        start_dist = haversine_distance(start_lat, start_lon, node_lat, node_lon)
                        end_dist = haversine_distance(end_lat, end_lon, node_lat, node_lon)
                        
                        if start_dist < min_start_dist:
                            min_start_dist = start_dist
                            new_start_node = node
                        
                        if end_dist < min_end_dist:
                            min_end_dist = end_dist
                            new_end_node = node
                    
                    if new_start_node and new_end_node:
                        print(f"Using alternative start node at distance {min_start_dist:.2f}m")
                        print(f"Using alternative end node at distance {min_end_dist:.2f}m")
                        start_node = new_start_node
                        end_node = new_end_node
                    else:
                        print("Could not find suitable alternative nodes")
                        return None, None, None, None, "invalid_address", None
                
                return None, None, None, None, "invalid_address", None
            
            print("Finding Pareto optimal paths...")
            paths, costs, infeasible_paths_info, remaining_socs = find_pareto_paths(road_network, nearest_stations, start_node, end_node,
                                                                max_paths=10, initial_soc=initial_soc, 
                                                                threshold_soc=threshold_soc, energy_consumption=energy_consumption)
            
            if not paths and infeasible_paths_info:
                print("\n\nNo feasible direct paths found. Attempting two-segment route with charging station...")
                
                stations_dict = {}
                for info in infeasible_paths_info:
                    if info['station_id']:
                        if info['station_id'] not in stations_dict:
                            stations_dict[info['station_id']] = {
                                'station_info': info['nearest_charging_station'],
                                'station_name': info['nearest_charging_station'].split(' (Location:')[0],
                                'station_location': {
                                    'latitude': float(info['nearest_charging_station'].split('Location: ')[1].split(',')[0]),
                                    'longitude': float(info['nearest_charging_station'].split(', ')[1].split(')')[0])
                                },
                                'paths': []
                            }
                        stations_dict[info['station_id']]['paths'].append(info['path_index'])
                
                if stations_dict:
                    first_station_id = list(stations_dict.keys())[0]
                    charging_station = stations_dict[first_station_id]
                    
                    print(f"\nPlanning two-segment route via charging station: {charging_station['station_name']}")
                    
                    charging_station_lat = charging_station['station_location']['latitude']
                    charging_station_lon = charging_station['station_location']['longitude']
                    
                    charging_station_node, charging_station_dist = find_nearest_node(road_network, charging_station_lat, charging_station_lon)
                    
                    if charging_station_node is None:
                        print("Could not find a road network node near the charging station.")
                        return None, None, None, None

                    print(f"Found charging station node at coordinates: ({charging_station_lat}, {charging_station_lon})")
                    print(f"Node ID: {charging_station_node}, Distance: {charging_station_dist:.2f}m")
                    
                    print("\n--- Section 1: Start to Charging Station ---")
                    section1_paths, section1_costs, section1_infeasible, section1_socs = find_pareto_paths(
                        road_network, nearest_stations, start_node, charging_station_node,
                        max_paths=5, initial_soc=initial_soc, 
                        threshold_soc=threshold_soc, energy_consumption=energy_consumption
                    )

                    for i, (path, cost, soc) in enumerate(zip(section1_paths, section1_costs, section1_socs)):
                        # Calculate charging time from current SOC to 100%
                        charging_time = calculate_charging_time(soc)
                        # Add charging time to the cost dictionary
                        cost['charging_time'] = charging_time
                        # Update total time to include charging time
                        cost['total_time'] = cost['time'] + charging_time
                        print(f"Path {i+1}: Travel time: {cost['time']:.1f}s, Charging time: {charging_time:.1f}s, Total time: {cost['total_time']:.1f}s")
                    
                    print("\n--- Section 2: Charging Station to End ---")
                    section2_paths, section2_costs, section2_infeasible, section2_socs = find_pareto_paths(
                        road_network, nearest_stations, charging_station_node, end_node,
                        max_paths=5, initial_soc=100,  
                        threshold_soc=threshold_soc, energy_consumption=energy_consumption
                    )
                    
                    if section1_paths and section2_paths:
                        print(f"\nFound {len(section1_paths)} paths for Section 1 and {len(section2_paths)} paths for Section 2")
                        
                        section1_paths, section1_costs, section1_socs = filter_similar_routes(section1_paths, section1_costs, section1_socs)
                        section2_paths, section2_costs, section2_socs = filter_similar_routes(section2_paths, section2_costs, section2_socs)
                        
                        all_paths = []
                        all_costs = []
                        path_sections = []
                        
                        for i, (path, cost) in enumerate(zip(section1_paths, section1_costs)):
                            all_paths.append(path)
                            all_costs.append(cost)
                            path_sections.append({
                                'section': 1,
                                'index': i+1,
                                'description': f"Section 1 Path {i+1}: Start to Charging Station"
                            })
                        
                        for i, (path, cost) in enumerate(zip(section2_paths, section2_costs)):
                            all_paths.append(path)
                            all_costs.append(cost)
                            path_sections.append({
                                'section': 2,
                                'index': i+1,
                                'description': f"Section 2 Path {i+1}: Charging Station to End"
                            })
                        
                        map_filename = f"route_{start_address}_to_{end_address}_two_segments.html"
                        try:
                            m, legend_html = map_renderer.display_two_segment_paths(
                                road_network, charging_stations, all_paths, all_costs, section1_socs, section2_socs, path_sections,
                                {'latitude': start_lat, 'longitude': start_lon},
                                {'latitude': end_lat, 'longitude': end_lon},
                                nearest_stations, map_filename,
                                initial_soc, energy_consumption, threshold_soc,
                                charging_stop={
                                    'node': charging_station_node,
                                    'latitude': charging_station_lat,
                                    'longitude': charging_station_lon,
                                    'name': charging_station['station_name']
                                }
                            )
                            print(f"\nMap with two-segment routes saved as {map_filename}")
                            
                            return road_network, charging_stations, all_paths, all_costs, map_filename, legend_html
                        except Exception as e:
                            print(f"Error creating two-segment map: {str(e)}")
                    else:
                        if not section1_paths:
                            print("Could not find feasible paths for Section 1.")
                        if not section2_paths:
                            print("Could not find feasible paths for Section 2.")
                else:
                    print("No suitable charging stations found.")
            
            if not paths:
                print("No valid paths found")
                return None, None, None, None, None, None
            
            map_filename = f'pareto_paths_{start_address.replace(" ", "_")}_{end_address.replace(" ", "_")}.html'
                
            try:
                m, legend_html = map_renderer.display_paths_on_map(road_network, charging_stations, paths, costs, remaining_socs,
                                   {'latitude': start_lat, 'longitude': start_lon},
                                   {'latitude': end_lat, 'longitude': end_lon},
                                   nearest_stations, map_filename, initial_soc, energy_consumption, threshold_soc)
            except Exception as e:
                print(f"Error in display_paths_on_map: {str(e)}")
                import traceback
                traceback.print_exc()
                return None, None, None, None, None, None
            
            return road_network, charging_stations, paths, costs, map_filename, legend_html
        
        else:
            print("BC region data not found. Please load it first.")
            return None, None, None, None, "error", None
            
    except Exception as e:
        print(f"General error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, "invalid_address", None

def load_bc_province_data(force_reload=False):
    """
    Load BC province data files from local storage with caching
    
    Parameters:
    force_reload (bool): Whether to force reload data even if cached
    
    Returns:
    Tuple of (road_network, charging_stations, intersections)
    """
    global _cached_road_network, _cached_charging_stations, _cached_intersections
    

    if not force_reload and _cached_road_network is not None and _cached_charging_stations is not None and _cached_intersections is not None:
        print("Using cached data (road network, charging stations, intersections)")
        return _cached_road_network, _cached_charging_stations, _cached_intersections
    
    print("Loading BC province data from local files...")
    
    bc_files_exist = all(os.path.exists(f) for f in [
        'roads_bc_regions.json', 
        'charging_stations_bc_regions.json', 
        'intersections_bc_regions.json'
    ])
    
    if not bc_files_exist:
        print("Error: Required data files not found. Please ensure the following files exist:")
        print("- roads_bc_regions.json")
        print("- charging_stations_bc_regions.json")
        print("- intersections_bc_regions.json")
        return None, None, None

    try:
        with open('roads_bc_regions.json', 'r', encoding='utf-8') as f:
            road_data = json.load(f)
        
        road_network = nx.MultiDiGraph()
        
        for node_id, node_data in road_data['nodes'].items():
            road_network.add_node(int(node_id) if node_id.isdigit() else node_id, **node_data)
        
        for edge in road_data['edges']:
            source = int(edge['source']) if edge['source'].isdigit() else edge['source']
            target = int(edge['target']) if edge['target'].isdigit() else edge['target']
            key = edge['key']
            
            edge_data = {k: v for k, v in edge.items() if k not in ['source', 'target', 'key']}
            
            if 'geometry' in edge_data and isinstance(edge_data['geometry'], str):
                try:
                    edge_data['geometry'] = wkt.loads(edge_data['geometry'])
                except:
                    del edge_data['geometry']
            
            if 'travel_time' not in edge_data:
                if 'length' in edge_data:
                    length = edge_data['length']  
                    speed = 13.89  
                    edge_data['travel_time'] = length / speed  
                else:
                    edge_data['travel_time'] = 60 
            
            road_network.add_edge(source, target, key=key, **edge_data)
        
        print(f"Loaded road network with {len(road_network.nodes)} nodes and {len(road_network.edges)} edges")
        
        with open('charging_stations_bc_regions.json', 'r') as f:
            charging_stations = json.load(f)
        
        print(f"Loaded {len(charging_stations)} charging stations")
        
        with open('intersections_bc_regions.json', 'r') as f:
            intersections = json.load(f)
        
        print(f"Loaded {len(intersections)} intersections")
        

        _cached_road_network = road_network
        _cached_charging_stations = charging_stations
        _cached_intersections = intersections
        
        return road_network, charging_stations, intersections
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

def calculate_remaining_soc(path, road_network, initial_soc, energy_consumption):
    """
    Calculate the remaining state of charge (SOC) after traveling along a path
    
    path: list of node IDs representing the path
    road_network: NetworkX graph of the road network
    initial_soc: initial state of charge (percentage)
    energy_consumption: energy consumption rate (percentage per km)
    
    Returns: remaining SOC (percentage)
    """
    total_distance = 0
    
    for i in range(len(path) - 1):
        try:
            edge_data = road_network.edges[path[i], path[i+1], 0]
            
            if 'length' in edge_data:
                distance = edge_data['length'] 
            else:
                start_y, start_x = road_network.nodes[path[i]]['y'], road_network.nodes[path[i]]['x']
                end_y, end_x = road_network.nodes[path[i+1]]['y'], road_network.nodes[path[i+1]]['x']
                distance = haversine_distance(start_y, start_x, end_y, end_x)
            
            total_distance += distance
        except Exception as e:
            print(f"Error calculating distance for edge ({path[i]}, {path[i+1]}): {str(e)}")
            total_distance += 500 
    
    total_distance_km = total_distance / 1000
    
    energy_consumed = total_distance_km * energy_consumption
    
    remaining_soc = initial_soc - energy_consumed
    
    remaining_soc = max(0, remaining_soc)
    
    return remaining_soc


def geocode_address(address):
    """
    Geocode an address to get its coordinates
    Returns (latitude, longitude) tuple or None if geocoding fails
    """
    try:
        coords = ox.geocoder.geocode(address)
        return coords  
    except Exception as e:
        print(f"Geocoding error for address '{address}': {str(e)}")
        return None

def find_nearest_node(G, lat, lon):
    """
    Find the nearest node in the graph to the given coordinates
    Returns (node_id, distance) tuple
    """
    min_distance = float('inf')
    nearest_node = None
    
    for node, data in G.nodes(data=True):
        if 'y' in data and 'x' in data:
            node_lat = data['y']
            node_lon = data['x']
            
            distance = haversine_distance(lat, lon, node_lat, node_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
    
    return nearest_node, min_distance