"""
Flask web app for route planning and map generation.
Provides endpoints to render the home page and generate routes.
"""
from flask import Flask, request, jsonify, render_template
import os
import map_construction

# Initialize Flask app
app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    # Home page endpoint
    return render_template("index.html")

@app.route("/generate-route", methods=["POST"])
def generate_route():
    # Route planning endpoint
    try:
        # parse input parameters from the submitted form
        start = request.form["start"]
        destination = request.form["destination"]
        initial_soc = float(request.form["initial_soc"])
        threshold_soc = float(request.form["threshold_soc"])
        consumption_rate = float(request.form["consumption_rate"])
        
        # execute the route planning function
        road_network, charging_stations, paths, costs, map_filename_or_status, legend_html = map_construction.test_route_planning(
            start, destination, initial_soc, threshold_soc, consumption_rate
        )

        if map_filename_or_status == "invalid_address":
            return jsonify({"success": False, "error": "Invalid address entered. Please check your start or destination address."})

        expected_map_filename = map_filename_or_status
        
        if paths is None:
            return jsonify({"success": False, "error": "No valid paths found."})

        os.makedirs("static/maps", exist_ok=True)
        
        static_map_path = f"static/maps/route_{start.replace(' ', '_')}_{destination.replace(' ', '_')}.html"
        
        if os.path.exists(expected_map_filename):
            import shutil
            shutil.copy(expected_map_filename, static_map_path)
        else:
            return jsonify({"success": False, "error": f"Map file {expected_map_filename} was not generated."})

        return jsonify({"success": True, "map_url": "/" + static_map_path, "legend_html": legend_html})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    # Run the Flask development server with debug mode on
    app.run(debug=True)



# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import os
# from map_construction import test_route_planning

# app = Flask(__name__)
# CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# @app.route("/")
# def home():
#     return "Welcome to the EV Planner API. Use the /generate-route endpoint to generate routes."

# @app.route("/test")
# def test():
#     return jsonify({"status": "ok", "message": "API is working"})

# @app.route("/generate-route", methods=["OPTIONS"])
# def generate_route_options():
#     response = jsonify({"status": "ok"})
#     return response

# @app.route("/generate-route", methods=["POST"])
# def generate_route():
#     print(f"Received POST request to /generate-route")
#     print(f"Request headers: {dict(request.headers)}")
#     try:
#         # Parse input from React frontend form (now expects JSON)
#         data = request.get_json()
#         print(f"Received data: {data}")
#         start = data.get("start")
#         destination = data.get("destination")
#         initial_soc = float(data.get("initial_soc"))
#         threshold_soc = float(data.get("threshold_soc"))
#         consumption_rate = float(data.get("consumption_rate"))
#         print(f"Parsed values - start: {start}, destination: {destination}, initial_soc: {initial_soc}, threshold_soc: {threshold_soc}, consumption_rate: {consumption_rate}")

#         # Call existing route planning function
#         road_network, charging_stations, paths, costs, map_filenames_or_status, legend_htmls = test_route_planning(
#             start, destination, initial_soc, threshold_soc, consumption_rate
#         )

#         if map_filenames_or_status == "invalid_address":
#             return jsonify({"success": False, "error": "Invalid address entered. Please check your start or destination address."})

#         if paths is None:
#             return jsonify({"success": False, "error": "No valid paths found."})

#         map_urls = []
#         legend_list = []

#         def to_url(map_file):
#             # Extract just the filename from the full path
#             filename = os.path.basename(map_file)
#             # Return URL pointing to Flask server
#             base_url = os.environ.get("BASE_URL", "https://evplanner-1.onrender.com")
#             url = f"{base_url}/maps/{filename}"
#             print(f"Generated map URL: {url} for file: {map_file}")
#             return url

#         if isinstance(map_filenames_or_status, list):
#             for idx, map_file in enumerate(map_filenames_or_status):
#                 if os.path.exists(map_file):
#                     print(f"Map file exists: {map_file}")
#                     map_urls.append(to_url(map_file))
#                     legend_list.append(legend_htmls[idx] if legend_htmls and idx < len(legend_htmls) else "")
#                 else:
#                     print(f"Map file does not exist: {map_file}")
#                     map_urls.append(None)
#                     legend_list.append("")
#         else:
#             if os.path.exists(map_filenames_or_status):
#                 print(f"Single map file exists: {map_filenames_or_status}")
#                 map_urls = [to_url(map_filenames_or_status)]
#                 legend_list = [legend_htmls]
#             else:
#                 print(f"Single map file does not exist: {map_filenames_or_status}")
#                 return jsonify({
#                     "success": False,
#                     "error": f"Map file {map_filenames_or_status} was not generated."
#                 })

#         print(f"Final map URLs: {map_urls}")
#         print(f"Final legend list: {legend_list}")

#         return jsonify({
#             "success": True,
#             "map_urls": map_urls,
#             "legend_htmls": legend_list
#         })

#     except Exception as e:
#         print(f"Server error: {e}")
#         return jsonify({"success": False, "error": str(e)})

# @app.route('/maps/<path:filename>')
# def serve_map(filename):
#     # Get the absolute path to the static/maps directory
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     maps_dir = os.path.join(script_dir, 'static', 'maps')
#     return send_from_directory(maps_dir, filename)

# # No "/" route — React handles frontend separately

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     print(f"Starting Flask app on port {port}")
#     app.run(debug=False, host="0.0.0.0", port=port)
