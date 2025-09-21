from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

# Dummy hotspot data - In a real application, this would come from a database.
hotspots = [
    {"lat": 19.0760, "lng": 72.8777, "severity": "high"},  # Mumbai
    {"lat": 28.7041, "lng": 77.1025, "severity": "medium"}, # Delhi
    {"lat": 13.0827, "lng": 80.2707, "severity": "low"}     # Chennai
]

# Route to serve the start page (landing page)
@app.route('/')
def start():
    """
    Serve the start.html page as the landing page
    """
    return render_template("start.html")

# Route to serve the main application page
@app.route('/app')
def home():
    """
    Serve the main application (index.html)
    """
    return render_template("index.html")

# Additional route for backward compatibility
@app.route('/index.html')
def index_redirect():
    """
    Redirect old index.html requests to /app
    """
    return render_template("index.html")

@app.route('/get-map-data')
def get_map_data():
    """
    Endpoint to retrieve existing plastic hotspot data.
    """
    print("Serving map data...")
    return jsonify(hotspots)

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Endpoint to simulate image analysis and add a new hotspot.
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    # In a real-world scenario, you would process the image here.
    # For this example, we'll just simulate a new hotspot being detected.
        
    # Generate random data for the new hotspot
    new_point = {
        "lat": round(random.uniform(10, 30), 4),
        "lng": round(random.uniform(70, 90), 4),
        "severity": random.choice(["low", "medium", "high"])
    }
        
    # Add the new point to our dummy data store
    hotspots.append(new_point)
        
    print(f"New hotspot detected: {new_point}")
    return jsonify({"status": "success", "new_point": new_point})

if __name__ == '__main__':
    # Ensure a 'templates' directory exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # Run the application
    app.run(debug=True)