from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from map_construction import test_route_planning

app = Flask(__name__)
CORS(app, origins=["https://yr2.vercel.app", "http://localhost:5173", "http://localhost:3000"])  # Allow cross-origin requests (from React)

@app.route("/")
def home():
    return "Welcome to the EV Planner API. Use the /generate-route endpoint to generate routes."



@app.route("/generate-route", methods=["POST"])
def generate_route():
    print("=== Flask route handler called ===")
    try:
        print("Parsing request data...")
        # Parse input from React frontend form (now expects JSON)
        data = request.get_json()
        print(f"Received data: {data}")
        
        start = data.get("start")
        destination = data.get("destination")
        initial_soc = float(data.get("initial_soc"))
        threshold_soc = float(data.get("threshold_soc"))
        consumption_rate = float(data.get("consumption_rate"))
        
        print(f"Parsed parameters:")
        print(f"  Start: {start}")
        print(f"  Destination: {destination}")
        print(f"  Initial SOC: {initial_soc}")
        print(f"  Threshold SOC: {threshold_soc}")
        print(f"  Consumption Rate: {consumption_rate}")

        print("Calling test_route_planning...")
        # Call existing route planning function
        road_network, charging_stations, paths, costs, map_filenames_or_status, legend_htmls = test_route_planning(
            start, destination, initial_soc, threshold_soc, consumption_rate
        )
        print(f"test_route_planning returned:")
        print(f"  road_network: {'Loaded' if road_network else 'None'}")
        print(f"  charging_stations: {'Loaded' if charging_stations else 'None'}")
        print(f"  paths: {len(paths) if paths else 'None'}")
        print(f"  costs: {len(costs) if costs else 'None'}")
        print(f"  map_filenames_or_status: {map_filenames_or_status}")
        print(f"  legend_htmls: {'Present' if legend_htmls else 'None'}")

        if map_filenames_or_status == "invalid_address":
            print("ERROR: Invalid address")
            return jsonify({"success": False, "error": "Invalid address entered. Please check your start or destination address."})

        if paths is None:
            print("ERROR: No valid paths found")
            return jsonify({"success": False, "error": "No valid paths found."})

        map_urls = []
        legend_list = []

        def to_url(map_file):
            # Extract just the filename from the full path
            filename = os.path.basename(map_file)
            # Return URL pointing to Flask server
            base_url = os.environ.get("BASE_URL", "https://evplanner-1.onrender.com")
            url = f"{base_url}/maps/{filename}"
            print(f"Generated map URL: {url} for file: {map_file}")
            return url

        if isinstance(map_filenames_or_status, list):
            for idx, map_file in enumerate(map_filenames_or_status):
                if os.path.exists(map_file):
                    print(f"Map file exists: {map_file}")
                    map_urls.append(to_url(map_file))
                    legend_list.append(legend_htmls[idx] if legend_htmls and idx < len(legend_htmls) else "")
                else:
                    print(f"Map file does not exist: {map_file}")
                    map_urls.append(None)
                    legend_list.append("")
        else:
            if os.path.exists(map_filenames_or_status):
                print(f"Single map file exists: {map_filenames_or_status}")
                map_urls = [to_url(map_filenames_or_status)]
                legend_list = [legend_htmls]
            else:
                print(f"Single map file does not exist: {map_filenames_or_status}")
                return jsonify({
                    "success": False,
                    "error": f"Map file {map_filenames_or_status} was not generated."
                })

        print(f"Final map URLs: {map_urls}")
        print(f"Final legend list: {legend_list}")

        return jsonify({
            "success": True,
            "map_urls": map_urls,
            "legend_htmls": legend_list
        })

    except Exception as e:
        print(f"ERROR in Flask route handler: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route('/maps/<path:filename>')
def serve_map(filename):
    # Get the absolute path to the static/maps directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maps_dir = os.path.join(script_dir, 'static', 'maps')
    return send_from_directory(maps_dir, filename)

# No "/" route — React handles frontend separately

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
