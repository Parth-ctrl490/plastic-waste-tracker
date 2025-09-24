from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random
import os

# -----------------------------
# YOLO Model Setup with Auto-Download (Once)
# -----------------------------
yolo_model = None
model_status = "Disabled"

try:
    from ultralytics import YOLO

    # Custom model path
    custom_model_path = "plastic-detection.pt"
    fallback_model_path = "yolov8n.pt"

    if os.path.exists(custom_model_path):
        yolo_model = YOLO(custom_model_path)
        model_status = f"Custom model loaded ({custom_model_path})"
        print(f"✅ YOLO model loaded: {custom_model_path}")
    else:
        if not os.path.exists(fallback_model_path):
            print(f"⚠️ {custom_model_path} not found. Downloading default YOLOv8n model...")
        yolo_model = YOLO(fallback_model_path)
        model_status = f"Fallback YOLOv8n model loaded ({fallback_model_path})"
        print(f"✅ YOLOv8n model loaded successfully: {fallback_model_path}")

except ImportError:
    print("❌ Ultralytics YOLO not installed. Run `pip install ultralytics` to enable detection.")
    model_status = "Ultralytics YOLO not installed"
    yolo_model = None
except Exception as e:
    print("❌ YOLO initialization failed:", e)
    model_status = "Initialization failed"
    yolo_model = None

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------
# Dummy Hotspot Data (initial)
# -----------------------------
hotspots = [
    {"lat": 19.0760, "lng": 72.8777, "severity": "high"},   # Mumbai
    {"lat": 28.7041, "lng": 77.1025, "severity": "medium"}, # Delhi
    {"lat": 13.0827, "lng": 80.2707, "severity": "low"}     # Chennai
]

# -----------------------------
# Routes for Pages
# -----------------------------
@app.route('/')
def start():
    return render_template("start.html")

@app.route('/app')
def home():
    return render_template("index.html")

@app.route('/index.html')
def index_redirect():
    return render_template("index.html")

@app.route('/help')
def help_page():
    # Send YOLO model status to frontend
    return render_template("help.html", model_status=model_status)

@app.route('/aboutus')
def aboutus_page():
    return render_template("aboutus.html")

@app.route('/info')
def info_page():
    return render_template("info.html")

@app.route('/mission')
def mission_page():
    return render_template("mission.html")

# -----------------------------
# API: Get Map Data
# -----------------------------
@app.route('/get-map-data')
def get_map_data():
    print("📡 Serving hotspot map data...")
    return jsonify({"status": "success", "hotspots": hotspots})

# -----------------------------
# API: Analyze Image
# -----------------------------
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Empty filename"}), 400

    detections = []

    # Run YOLO if available
    if yolo_model:
        try:
            results = yolo_model.predict(file)
            detections = results[0].tojson()
            print("✅ YOLO detection completed.")
        except Exception as e:
            print("❌ YOLO detection error:", e)
            detections = []
    else:
        print("⚠️ YOLO model not loaded. Skipping detection.")

    # Always add a random hotspot
    new_point = {
        "lat": round(random.uniform(10, 30), 4),
        "lng": round(random.uniform(70, 90), 4),
        "severity": random.choice(["low", "medium", "high"])
    }
    hotspots.append(new_point)
    print(f"📍 New hotspot added: {new_point}")

    return jsonify({
        "status": "success",
        "new_point": new_point,
        "detections": detections
    })

# -----------------------------
# Run the Application
# -----------------------------
if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
