// Initialize map
var map = L.map('map').setView([20.5937, 78.9629], 5); // India view

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Function to load hotspots & update map + chart
function loadHotspots() {
  fetch('/get-map-data')
    .then(res => res.json())
    .then(data => {
      // Clear old layers (avoid duplicates)
      map.eachLayer(layer => {
        if (layer instanceof L.Circle) {
          map.removeLayer(layer);
        }
      });

      // Plot hotspots
      let severityCounts = { low: 0, medium: 0, high: 0 };

      data.forEach(point => {
        let color =
          point.severity === "high" ? "red" :
          point.severity === "medium" ? "orange" : "green";

        L.circle([point.lat, point.lng], {
          color: color,
          radius: 50000,
          fillOpacity: 0.5
        }).addTo(map).bindPopup(`Severity: ${point.severity}`);

        severityCounts[point.severity]++;
      });

      // Plotly chart
      var chartData = [{
        values: Object.values(severityCounts),
        labels: Object.keys(severityCounts),
        type: 'pie',
        hole: 0.4
      }];

      var layout = {
        title: "Analysis Results",
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent"
      };

      Plotly.newPlot('chart', chartData, layout);

      // Hide spinner if you have one
      let spinner = document.getElementById("loadingSpinner");
      if (spinner) spinner.style.display = "none";
    })
    .catch(err => console.error("Error fetching map data:", err));
}

// Upload form → send image → get new hotspot → update without reload
document.getElementById("uploadForm").addEventListener("submit", function(e) {
  e.preventDefault();
  let formData = new FormData();
  let fileInput = document.getElementById("fileInput");
  formData.append("file", fileInput.files[0]);

  fetch('/analyze-image', {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(result => {
    alert(
      "New hotspot added at Lat: " +
      result.new_point.lat +
      ", Lng: " +
      result.new_point.lng
    );
    loadHotspots(); // update map/chart dynamically
  })
  .catch(err => console.error("Error analyzing image:", err));
});

// Load initial hotspots
loadHotspots();
