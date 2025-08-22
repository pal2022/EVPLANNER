import folium
import os
import math
import json
from shapely import wkt
import networkx as nx

def apply_charging_icon_styles(m):
    """Apply consistent styling to charging station icons on the map"""
    m.get_root().header.add_child(folium.Element('''
        <style>
            .leaflet-marker-icon.fa-charging-station {
                transform: scale(0.1) !important;
                transition: none !important;
            }
            
            .leaflet-marker-icon.fa-play,
            .leaflet-marker-icon.fa-stop {
                transform: scale(1.0) !important;
            }
            
            .custom-charging-icon {
                opacity: 0;
                animation: fadeIn 0.3s forwards;
                animation-delay: 0.5s;
            }
            
            @keyframes fadeIn {
                to { opacity: 1; }
            }
        </style>
    '''))

    m.get_root().html.add_child(folium.Element('''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            function applyIconStyles() {
                var icons = document.querySelectorAll('.fa-charging-station');
                for (var i = 0; i < icons.length; i++) {
                    var icon = icons[i].parentNode;
                    if (icon) {
                        icon.style.transform = 'scale(0.1)';
                    }
                }
            }
            
            applyIconStyles();
            setTimeout(applyIconStyles, 500);
            setTimeout(applyIconStyles, 1000);
            setTimeout(applyIconStyles, 2000);
            
            var observer = new MutationObserver(function(mutations) {
                applyIconStyles();
            });
            
            observer.observe(document.body, { 
                childList: true,
                subtree: true
            });
        });
        </script>
    '''))
    
    m.get_root().header.add_child(folium.Element('''
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    '''))
    
    return m

def display_paths_on_map(road_network, charging_stations, paths, costs, remaining_socs, start_point, end_point, 
                        nearest_stations, map_filename, initial_soc, energy_consumption, threshold_soc=20,
                        charging_stop=None):
    """Display paths with charging information"""
    center_lat = (start_point['latitude'] + end_point['latitude']) / 2
    center_lon = (start_point['longitude'] + end_point['longitude']) / 2
    
    # Create map with smooth zoom and interaction options
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=11,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True,
        touchZoom=True,
        doubleClickZoom=True,
        boxZoom=True,
        keyboard=True,
        preferCanvas=True
    )
    
    # Add smooth zoom and interaction JavaScript
    smooth_zoom_js = """
    <script>
    // Wait for map to load
    document.addEventListener('DOMContentLoaded', function() {
        // Get the map instance
        var map = document.querySelector('.folium-map')._leaflet_map;
        
        // Add smooth zoom controls
        var zoomInBtn = L.Control.zoomIn = L.Control.extend({
            onAdd: function() {
                var container = L.DomUtil.create('div', 'leaflet-control-zoom-in leaflet-control-zoom');
                container.innerHTML = '+';
                container.title = 'Zoom in';
                container.style.cssText = 'width: 30px; height: 30px; line-height: 30px; text-align: center; font-size: 18px; font-weight: bold; color: #333; cursor: pointer; transition: all 0.2s ease; user-select: none;';
                
                L.DomEvent.on(container, 'click', function(e) {
                    L.DomEvent.stopPropagation(e);
                    L.DomEvent.preventDefault(e);
                    smoothZoom(map, 1);
                });
                
                L.DomEvent.on(container, 'mouseover', function() {
                    this.style.background = '#f4f4f4';
                    this.style.color = '#2563eb';
                    this.style.transform = 'scale(1.05)';
                });
                
                L.DomEvent.on(container, 'mouseout', function() {
                    this.style.background = '#fff';
                    this.style.color = '#333';
                    this.style.transform = 'scale(1)';
                });
                
                return container;
            }
        });
        
        var zoomOutBtn = L.Control.zoomOut = L.Control.extend({
            onAdd: function() {
                var container = L.DomUtil.create('div', 'leaflet-control-zoom-out leaflet-control-zoom');
                container.innerHTML = '−';
                container.title = 'Zoom out';
                container.style.cssText = 'width: 30px; height: 30px; line-height: 30px; text-align: center; font-size: 18px; font-weight: bold; color: #333; cursor: pointer; transition: all 0.2s ease; user-select: none;';
                
                L.DomEvent.on(container, 'click', function(e) {
                    L.DomEvent.stopPropagation(e);
                    L.DomEvent.preventDefault(e);
                    smoothZoom(map, -1);
                });
                
                L.DomEvent.on(container, 'mouseover', function() {
                    this.style.background = '#f4f4f4';
                    this.style.color = '#2563eb';
                    this.style.transform = 'scale(1.05)';
                });
                
                L.DomEvent.on(container, 'mouseout', function() {
                    this.style.background = '#fff';
                    this.style.color = '#333';
                    this.style.transform = 'scale(1)';
                });
                
                return container;
            }
        });
        
        // Add custom zoom controls
        new zoomInBtn({ position: 'topright' }).addTo(map);
        new zoomOutBtn({ position: 'topright' }).addTo(map);
        
        // Remove default zoom control
        if (map.zoomControl) {
            map.removeControl(map.zoomControl);
        }
        
        // Smooth zoom function
        function smoothZoom(map, direction) {
            var currentZoom = map.getZoom();
            var targetZoom = Math.max(0, Math.min(18, currentZoom + direction));
            
            if (targetZoom !== currentZoom) {
                map.flyTo(map.getCenter(), targetZoom, {
                    duration: 0.5,
                    easeLinearity: 0.25
                });
            }
        }
        
        // Add smooth transitions for markers and paths
        var style = document.createElement('style');
        style.textContent = `
            .leaflet-marker-icon {
                transition: transform 0.2s ease;
            }
            .leaflet-marker-icon:hover {
                transform: scale(1.1);
            }
            .leaflet-control-zoom {
                border: 2px solid rgba(0,0,0,0.2);
                background: #fff;
                border-radius: 4px;
                box-shadow: 0 1px 5px rgba(0,0,0,0.4);
            }
            .leaflet-control-zoom-in,
            .leaflet-control-zoom-out {
                border-bottom: 1px solid #ccc;
            }
            .leaflet-control-zoom-in:last-child,
            .leaflet-control-zoom-out:last-child {
                border-bottom: none;
            }
        `;
        document.head.appendChild(style);
    });
    </script>
    """
    
    m = apply_charging_icon_styles(m)
    
    charging_stations_dict = {}
    for station in charging_stations:
        try:
            station_lat = station['location']['latitude']
            station_lon = station['location']['longitude']
            station_id = f"{station_lat},{station_lon}"
            charging_stations_dict[station_id] = station
            
            popup_html = f"""
            <div style="width: 200px">
                <b>{station['name']}</b><br>
                Address: {station.get('address', 'N/A')}<br>
                Connector Types: {', '.join(station.get('connector_types', ['Unknown']))}<br>
                Power: {station.get('power_kw', 'Unknown')} kW
            </div>
            """
            
            icon_html = """
            <div style="font-size: 72px; color: white; background-color: #3186cc; border-radius: 50%; width: 144px; height: 144px; display: flex; align-items: center; justify-content: center;">
            <i class="fa fa-charging-station"></i>
            </div>
            """
            
            custom_icon = folium.DivIcon(
                icon_size=(144, 144),
                icon_anchor=(72, 72),
                html=icon_html,
                class_name="custom-charging-icon"
            )
            
            folium.Marker(
                [station_lat, station_lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=custom_icon
            ).add_to(m)
        except Exception as e:
            print(f"Error adding charging station: {str(e)}")
            continue
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'darkorange']
    
    path_data = []
    
    for i, (path, cost) in enumerate(zip(paths, costs)):
        color = colors[i % len(colors)]
        
        coords = []
        for node in path:
            try:
                lat = road_network.nodes[node]['y']
                lon = road_network.nodes[node]['x']
                coords.append([lat, lon])
            except:
                continue
        
        if not coords:
            continue
        
        # folium.PolyLine(
        #     coords,
        #     color=color,
        #     weight=4,
        #     opacity=0.8,
        #     tooltip=f"Path {i+1}: {cost['time']:.1f}s, {cost['safety']/1000:.2f}km"
        # ).add_to(m)
        group_name = f"Path {i+1}: {int(cost['time']//60)}m {int(cost['time']%60)}s, {cost['safety']/1000:.2f} km"
        feature_group = folium.FeatureGroup(name=group_name)

        # Route line
        folium.PolyLine(
            coords,
            color=color,
            weight=4,
            opacity=0.8,
            tooltip=group_name
        ).add_to(feature_group)
        
        max_dist = 0
        critical_node = None
        for node in path:
            if node in nearest_stations:
                dist = nearest_stations[node]['distance']
                if dist > max_dist:
                    max_dist = dist
                    critical_node = node
        
        if critical_node:
            node_data = road_network.nodes[critical_node]
            folium.CircleMarker(
                location=[node_data['y'], node_data['x']],
                radius=5,
                color=color,
                fill=True,
                popup=f'Critical point: {max_dist:.0f}m to nearest charging station'
            # ).add_to(m)
            ).add_to(feature_group)
            
            if critical_node in nearest_stations:
                station_info = nearest_stations[critical_node]
                
                if 'station' in station_info and 'lat' in station_info['station']:
                    station_lat = station_info['station']['lat']
                    station_lon = station_info['station']['lon']
                    station_name = station_info['station'].get('name', 'Unnamed Station')
                else:
                    print(f"Warning: Could not find location in station_info: {station_info}")
                    continue
                
                folium.PolyLine(
                    [[node_data['y'], node_data['x']], [station_lat, station_lon]],
                    color=color,
                    weight=2,
                    dash_array='5,10',
                    popup=f'Distance to nearest station: {max_dist:.0f}m'
                # ).add_to(m)
                ).add_to(feature_group)
                
                small_purple_icon = folium.DivIcon(
                    icon_size=(144, 144),
                    icon_anchor=(72, 72),
                    html=f'<div style="font-size: 72px; color: white; background-color: purple; border-radius: 50%; width: 144px; height: 144px; display: flex; align-items: center; justify-content: center;"><i class="fa fa-charging-station"></i></div>',
                    class_name="custom-charging-icon"
                )
                
                folium.Marker(
                    location=[station_lat, station_lon],
                    popup=f'Nearest station to critical point: {station_name}',
                    icon=small_purple_icon
                ).add_to(m)
        
        feature_group.add_to(m)
        path_data.append({
            'color': color,
            'time': cost['time'],
            'max_dist': cost['safety'],
            'description': f"Path {i+1}",
            'critical_dist': max_dist / 1000 if critical_node else 0,
            'remaining_soc': remaining_socs[i] if i < len(remaining_socs) else 0  
        })
    
    folium.Marker(
        [start_point['latitude'], start_point['longitude']],
        popup="Start",
        icon=folium.Icon(icon="play", prefix="fa", color="green")
    ).add_to(m)
    
    folium.Marker(
        [end_point['latitude'], end_point['longitude']],
        popup="End",
        icon=folium.Icon(icon="stop", prefix="fa", color="red")
    ).add_to(m)
    
    if charging_stop:
        folium.Marker(
            [charging_stop['latitude'], charging_stop['longitude']],
            popup=f"Charging Stop: {charging_stop['name']}",
            icon=folium.Icon(icon="bolt", prefix="fa", color="purple", icon_color="white")
        ).add_to(m)
    
    folium.LayerControl(collapsed=False).add_to(m)
    
    legend_html = '''
    <div style="bottom: 50px; left: 50px; width: 200px; height: auto;
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; padding: 10px;
                overflow-y: auto; max-height: 400px;">
    <div style="font-weight: bold; margin-bottom: 10px;">Route Legend</div>
    '''
    
    for data in path_data:
        color = data['color']
        total_time = data['time']
        max_charging_dist = data['max_dist'] / 1000
        critical_dist = data['critical_dist']
        
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        else:
            time_str = f"{minutes}m {seconds}s"
        
        legend_html += f'''
        <div style="display: flex; align-items: center; margin-top: 5px;">
            <div style="background-color: {color}; width: 15px; height: 3px; margin-right: 5px;"></div>
            <div>{data['description']}: Total Time: {time_str}, Proximity: {critical_dist:.2f}km, Remaining Battery: {data['remaining_soc']:.1f}%</div>
        </div>
        '''
    
    legend_html += '</div>'
    
    # m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(map_filename)
    print(f"\nMap with paths saved as {map_filename}")
    return m, legend_html

def display_two_segment_paths(G, charging_stations, paths, costs, section1_socs, section2_socs, path_sections, start_point, end_point, 
                             nearest_stations, map_filename, initial_soc, energy_consumption, threshold_soc=20,
                             charging_stop=None):
    """Display two-segment paths with charging information"""
    center_lat = (start_point['latitude'] + end_point['latitude']) / 2
    center_lon = (start_point['longitude'] + end_point['longitude']) / 2
    
    # Create map with smooth zoom and interaction options
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=11,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True,
        touchZoom=True,
        doubleClickZoom=True,
        boxZoom=True,
        keyboard=True,
        preferCanvas=True
    )
    
    # Add smooth zoom and interaction JavaScript
    smooth_zoom_js = """
    <script>
    // Wait for map to load
    document.addEventListener('DOMContentLoaded', function() {
        // Get the map instance
        var map = document.querySelector('.folium-map')._leaflet_map;
        
        // Add smooth zoom controls
        var zoomInBtn = L.Control.zoomIn = L.Control.extend({
            onAdd: function() {
                var container = L.DomUtil.create('div', 'leaflet-control-zoom-in leaflet-control-zoom');
                container.innerHTML = '+';
                container.title = 'Zoom in';
                container.style.cssText = 'width: 30px; height: 30px; line-height: 30px; text-align: center; font-size: 18px; font-weight: bold; color: #333; cursor: pointer; transition: all 0.2s ease; user-select: none;';
                
                L.DomEvent.on(container, 'click', function(e) {
                    L.DomEvent.stopPropagation(e);
                    L.DomEvent.preventDefault(e);
                    smoothZoom(map, 1);
                });
                
                L.DomEvent.on(container, 'mouseover', function() {
                    this.style.background = '#f4f4f4';
                    this.style.color = '#2563eb';
                    this.style.transform = 'scale(1.05)';
                });
                
                L.DomEvent.on(container, 'mouseout', function() {
                    this.style.background = '#fff';
                    this.style.color = '#333';
                    this.style.transform = 'scale(1)';
                });
                
                return container;
            }
        });
        
        var zoomOutBtn = L.Control.zoomOut = L.Control.extend({
            onAdd: function() {
                var container = L.DomUtil.create('div', 'leaflet-control-zoom-out leaflet-control-zoom');
                container.innerHTML = '−';
                container.title = 'Zoom out';
                container.style.cssText = 'width: 30px; height: 30px; line-height: 30px; text-align: center; font-size: 18px; font-weight: bold; color: #333; cursor: pointer; transition: all 0.2s ease; user-select: none;';
                
                L.DomEvent.on(container, 'click', function(e) {
                    L.DomEvent.stopPropagation(e);
                    L.DomEvent.preventDefault(e);
                    smoothZoom(map, -1);
                });
                
                L.DomEvent.on(container, 'mouseover', function() {
                    this.style.background = '#f4f4f4';
                    this.style.color = '#2563eb';
                    this.style.transform = 'scale(1.05)';
                });
                
                L.DomEvent.on(container, 'mouseout', function() {
                    this.style.background = '#fff';
                    this.style.color = '#333';
                    this.style.transform = 'scale(1)';
                });
                
                return container;
            }
        });
        
        // Add custom zoom controls
        new zoomInBtn({ position: 'topright' }).addTo(map);
        new zoomOutBtn({ position: 'topright' }).addTo(map);
        
        // Remove default zoom control
        if (map.zoomControl) {
            map.removeControl(map.zoomControl);
        }
        
        // Smooth zoom function
        function smoothZoom(map, direction) {
            var currentZoom = map.getZoom();
            var targetZoom = Math.max(0, Math.min(18, currentZoom + direction));
            
            if (targetZoom !== currentZoom) {
                map.flyTo(map.getCenter(), targetZoom, {
                    duration: 0.5,
                    easeLinearity: 0.25
                });
            }
        }
        
        // Add smooth transitions for markers and paths
        var style = document.createElement('style');
        style.textContent = `
            .leaflet-marker-icon {
                transition: transform 0.2s ease;
            }
            .leaflet-marker-icon:hover {
                transform: scale(1.1);
            }
            .leaflet-control-zoom {
                border: 2px solid rgba(0,0,0,0.2);
                background: #fff;
                border-radius: 4px;
                box-shadow: 0 1px 5px rgba(0,0,0,0.4);
            }
            .leaflet-control-zoom-in,
            .leaflet-control-zoom-out {
                border-bottom: 1px solid #ccc;
            }
            .leaflet-control-zoom-in:last-child,
            .leaflet-control-zoom-out:last-child {
                border-bottom: none;
            }
        `;
        document.head.appendChild(style);
    });
    </script>
    """
    
    m = apply_charging_icon_styles(m)
    
    # Add smooth zoom JavaScript to the map
    m.get_root().html.add_child(folium.Element(smooth_zoom_js))
    
    section1_colors = ['red', 'blue', 'green', 'purple', 'orange']
    section2_colors = ['darkred', 'darkblue', 'darkgreen', 'darkpurple', 'darkorange']
    
    critical_stations = set()
    
    for station in charging_stations:
        try:
            station_lat = station['location']['latitude']
            station_lon = station['location']['longitude']
            station_id = f"{station_lat},{station_lon}"
            
            if station_id in critical_stations:
                continue
                
            popup_html = f"""
            <div style="width: 200px">
                <b>{station['name']}</b><br>
                Address: {station.get('address', 'N/A')}<br>
                Connector Types: {', '.join(station.get('connector_types', ['Unknown']))}<br>
                Power: {station.get('power_kw', 'Unknown')} kW
            </div>
            """
            
            icon_html = """
            <div style="font-size: 72px; color: white; background-color: #3186cc; border-radius: 50%; width: 144px; height: 144px; display: flex; align-items: center; justify-content: center;">
            <i class="fa fa-charging-station"></i>
            </div>
            """
            
            custom_icon = folium.DivIcon(
                icon_size=(144, 144),
                icon_anchor=(72, 72),
                html=icon_html,
                class_name="custom-charging-icon"
            )
            
            folium.Marker(
                [station_lat, station_lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=custom_icon
            ).add_to(m)
        except Exception as e:
            print(f"Error adding charging station: {str(e)}")
            continue
    
    path_data = []
    
    for i, (path, cost) in enumerate(zip(paths, costs)):
        section_info = path_sections[i]
        section = section_info['section']
        index = section_info['index']
        
        color = (section1_colors if section == 1 else section2_colors)[(index - 1) % 5]
        
        if section == 1 and 'total_time' in cost and 'charging_time' in cost:
            travel_time_str = format_time(cost['time'])
            charging_time_str = format_time(cost['charging_time'])
            total_time_str = format_time(cost['total_time'])
            
            group_name = f"Section {section} - Path {index}: {total_time_str}, {cost['safety']/1000:.2f} km"
        else:
            time_str = format_time(cost['time'])
            group_name = f"Section {section} - Path {index}: {time_str}, {cost['safety']/1000:.2f} km"

        feature_group = folium.FeatureGroup(name=group_name)
        
        # group_name = f"Section {section} - Path {index}: {int(cost['time']//60)}m {int(cost['time']%60)}s, {cost['safety']/1000:.2f} km"
        # feature_group = folium.FeatureGroup(name=group_name)

        if section == 1:
            color = section1_colors[(section_info['index'] - 1) % len(section1_colors)]
        else:
            color = section2_colors[(section_info['index'] - 1) % len(section2_colors)]
        
        coords = []
        for node in path:
            try:
                lat = G.nodes[node]['y']
                lon = G.nodes[node]['x']
                coords.append([lat, lon])
            except:
                continue
        
        if not coords:
            continue

        tooltip_text = section_info['description']
        if section == 1 and 'total_time' in cost:
            total_time_str = format_time(cost['total_time'])
            tooltip_text = f"{section_info['description']} (Total: {total_time_str})"
        
        folium.PolyLine(
            coords,
            color=color,
            weight=4,
            opacity=0.8,
            tooltip=tooltip_text
        # ).add_to(m)
        ).add_to(feature_group)
        
        max_dist = 0
        critical_node = None
        
        for node in path:
            if node in nearest_stations:
                dist = nearest_stations[node]['distance']
                if dist > max_dist:
                    max_dist = dist
                    critical_node = node
        
        if critical_node:
            node_data = G.nodes[critical_node]
            folium.CircleMarker(
                location=[node_data['y'], node_data['x']],
                radius=5,
                color=color,
                fill=True,
                popup=f'Critical point: {max_dist:.0f}m to nearest charging station'
            # ).add_to(m)
            ).add_to(feature_group)
            
            if critical_node in nearest_stations:
                station_info = nearest_stations[critical_node]
                
                if 'station' in station_info and 'lat' in station_info['station']:
                    station_lat = station_info['station']['lat']
                    station_lon = station_info['station']['lon']
                    station_name = station_info['station'].get('name', 'Unnamed Station')
                else:
                    print(f"Warning: Could not find location in station_info: {station_info}")
                    continue
                
                station_id = f"{station_lat},{station_lon}"
                critical_stations.add(station_id)
                
                folium.PolyLine(
                    [[node_data['y'], node_data['x']], [station_lat, station_lon]],
                    color=color,
                    weight=2,
                    dash_array='5,10',
                    popup=f'Distance to nearest station: {max_dist:.0f}m'
                # ).add_to(m)
                ).add_to(feature_group)
                
                purple_icon = folium.DivIcon(
                    icon_size=(144, 144),
                    icon_anchor=(72, 72),
                    html=f'<div style="font-size: 72px; color: white; background-color: purple; border-radius: 50%; width: 144px; height: 144px; display: flex; align-items: center; justify-content: center;"><i class="fa fa-charging-station"></i></div>',
                    class_name="custom-charging-icon"
                )
                
                folium.Marker(
                    location=[station_lat, station_lon],
                    popup=f'Nearest station to critical point: {station_name}',
                    icon=purple_icon
                ).add_to(m)
        
        feature_group.add_to(m)

        soc1 = section1_socs[index-1] if section == 1 and (index-1) < len(section1_socs) else 0
        soc2 = section2_socs[index-1] if section == 2 and (index-1) < len(section2_socs) else 0
        soc = soc1 + soc2

        # Add charging time to path_data for section 1
        path_data_entry = {
            'color': color,
            'time': cost['time'],
            'max_dist': cost['safety'],
            'description': section_info['description'],
            'critical_dist': max_dist / 1000 if critical_node else 0,
            'remaining_soc': soc
        }
        
        # Add charging time to path_data if it exists
        if section == 1 and 'charging_time' in cost:
            path_data_entry['charging_time'] = cost['charging_time']
            if 'total_time' in cost:
                path_data_entry['total_time'] = cost['total_time']
        
        path_data.append(path_data_entry)
        # path_data.append({
        #     'color': color,
        #     'time': cost['time'],
        #     'max_dist': cost['safety'],
        #     'description': section_info['description'],
        #     'critical_dist': max_dist / 1000 if critical_node else 0,
        #     'remaining_soc': soc
        # })
    
    folium.Marker(
        [start_point['latitude'], start_point['longitude']],
        popup="Start",
        icon=folium.Icon(icon="play", prefix="fa", color="green")
    ).add_to(m)
    
    folium.Marker(
        [end_point['latitude'], end_point['longitude']],
        popup="End",
        icon=folium.Icon(icon="stop", prefix="fa", color="red")
    ).add_to(m)
    
    if charging_stop:
        folium.Marker(
            [charging_stop['latitude'], charging_stop['longitude']],
            popup=f"Charging Stop: {charging_stop['name']}",
            icon=folium.Icon(icon="bolt", prefix="fa", color="purple", icon_color="white")
        ).add_to(m)
    
    folium.LayerControl(collapsed=False).add_to(m)

    legend_html = '''
    <div style="bottom: 50px; left: 50px; width: 200px; height: auto;
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; padding: 10px;
                overflow-y: auto; max-height: 400px;">
    <div style="font-weight: bold; margin-bottom: 10px;">Two-Segment Route Legend</div>
    <div style="margin-bottom: 5px;"><b>Section 1: Start to Charging Station</b></div>
    '''
    
    for data in path_data:
        if "Section 1" in data['description']:
            color = data['color']
            total_time = data['time']
            max_charging_dist = data['max_dist'] / 1000
            critical_dist = data['critical_dist']
            soc = data['remaining_soc']
            
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            else:
                time_str = f"{minutes}m {seconds}s"

            time_info = f"Travel: {travel_time_str}"
        
            if 'total_time' in data:
                total_time_str = format_time(data['total_time'])
                time_info = f"Total: {total_time_str}"
            else:
                total_time_str = format_time(data['time'])
                time_info = f"Total: {total_time_str}"

            
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-top: 5px;">
                <div style="background-color: {color}; width: 15px; height: 3px; margin-right: 5px;"></div>
                <div>{data['description']}: Total Time: {time_info}, Proximity: {critical_dist:.2f}km</div>
            </div>
            '''
    
    legend_html += '<div style="margin: 10px 0 5px 0;"><b>Section 2: Charging Station to End</b></div>'
    
    for data in path_data:
        if "Section 2" in data['description']:
            color = data['color']
            total_time = data['time']
            max_charging_dist = data['max_dist'] / 1000
            critical_dist = data['critical_dist']
            soc = data['remaining_soc']
            
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            else:
                time_str = f"{minutes}m {seconds}s"
            
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-top: 5px;">
                <div style="background-color: {color}; width: 15px; height: 3px; margin-right: 5px;"></div>
                <div>{data['description']}: Total Time: {time_str}, Proximity: {critical_dist:.2f}km, Remaining Battery: {soc:.1f}%</div>
            </div>
            '''
    
    legend_html += '</div>'
    
    # m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(map_filename)
    return m, legend_html

def update_html_with_section2(map_filename, G, section2_paths, section2_costs, 
                             charging_station_lat, charging_station_lon, end_lat, end_lon):
    """Update an existing HTML map file with section 2 paths"""
    try:
        with open(map_filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        backup_filename = map_filename + '.backup'
        with open(backup_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        section2_colors = ['darkred', 'darkblue', 'darkgreen', 'darkpurple', 'darkorange']
        
        js_start = """
        <script>
        (function() {
            var map = document.querySelector('.folium-map')._leaflet_map;
        """
        
        js_end = """
        })();
        </script>
        """
        
        js_code = js_start
        
        for i, (path, cost) in enumerate(zip(section2_paths, section2_costs)):
            color = section2_colors[i % len(section2_colors)]
            
            coords_js = []
            for node in path:
                try:
                    lat = G.nodes[node]['y']
                    lon = G.nodes[node]['x']
                    coords_js.append([lat, lon])
                except:
                    continue
            
            if not coords_js:
                continue
            
            coords_str = str(coords_js).replace('(', '[').replace(')', ']')
            
            path_js = f"""
            var path{i} = L.polyline({coords_str}, {{
                color: '{color}',
                weight: 4,
                opacity: 0.8
            }}).addTo(map);
            
            path{i}.bindTooltip("Section 2, Path {i+1}: {cost['time']:.1f}s, {cost['safety']/1000:.2f}km");
            """
            
            js_code += path_js
        
        markers_js = f"""
        var endIcon = L.divIcon({{
            html: '<i class="fa fa-stop" style="color: white;"></i>',
            iconSize: [20, 20],
            className: 'leaflet-div-icon-end'
        }});
        
        L.marker([{end_lat}, {end_lon}], {{
            icon: L.icon({{
                icon: 'stop',
                prefix: 'fa',
                iconColor: 'white',
                markerColor: 'red'
            }})
        }}).addTo(map).bindPopup('End');
        
        var chargingIcon = L.divIcon({{
            html: '<i class="fa fa-bolt" style="color: white;"></i>',
            iconSize: [20, 20],
            className: 'leaflet-div-icon-charging'
        }});
        
        L.marker([{charging_station_lat}, {charging_station_lon}], {{
            icon: L.icon({{
                icon: 'bolt',
                prefix: 'fa',
                iconColor: 'white',
                markerColor: 'blue'
            }})
        }}).addTo(map).bindPopup('Charging Station');
        
        map.fitBounds([
            [{charging_station_lat}, {charging_station_lon}],
            [{end_lat}, {end_lon}]
        ]);
        """
        
        js_code += markers_js + js_end
        
        html_content = html_content.replace('</body>', js_code + '\n</body>')
        
        with open(map_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Updated {map_filename} with section 2 paths")
        return True
        
    except Exception as e:
        print(f"Error updating HTML with section 2: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def format_time(seconds):
    """Format time in seconds to a human-readable string"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000
    return c * r 