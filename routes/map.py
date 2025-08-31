# routes/map.py
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import math
import random

map_bp = Blueprint('map_bp', __name__)

# Define the map route
@map_bp.route('/')
def map():
    if not session.get('logged_in'):
        return redirect(url_for('login_bp.login'))
    return render_template('map.html')

# Add a health check endpoint
@map_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "Map blueprint is working"})

# State-level policy advantages
STATE_POLICIES = {
    "Gujarat": [
        "Pioneering Renewable Energy Policy 2023 with strong incentives.",
        "Excellent port infrastructure for green hydrogen export.",
        "Land subsidies up to 50% for new renewable energy projects."
    ],
    "Maharashtra": [
        "High industrial demand from major economic hubs like Mumbai and Pune.",
        "Draft Green Hydrogen policy aims for 1.5 MMTPA production.",
        "Strong focus on developing hydrogen for the transportation sector."
    ],
    "Uttar Pradesh": [
        "Strategic location with access to large agricultural and industrial markets.",
        "Government focus on bundling green hydrogen with solar energy projects.",
        "Incentives for developing green ammonia and fertilizer plants."
    ],
    "Tamil Nadu": [
        "Exceptional wind energy potential, especially along coastal regions.",
        "Major port at Thoothukudi designated as a green hydrogen hub.",
        "State policy provides single-window clearance for green energy projects."
    ],
    "Odisha": [
        "Rich in mineral resources with major steel and aluminum industries (high demand).",
        "Strategic port locations at Paradip and Dhamra for export.",
        "Government promoting Green Hydrogen/Ammonia parks with dedicated infrastructure."
    ]
}

# City-level "Hubs" with updated scores including transport logistics
# Renamed keys for clarity: 'grid' -> 'infrastructure', 'demand' -> 'demand_center'
HUBS = {
    # --- Gujarat (20 cities) ---
    'Ahmedabad': {'lat': 23.0225, 'lon': 72.5714, 'state': 'Gujarat', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 5, 'infrastructure': 9, 'demand_center': 9, 'transport_logistics': 8},
    'Kutch': {'lat': 23.7337, 'lon': 69.8597, 'state': 'Gujarat', 'solar': 10, 'wind': 9, 'gas': 5, 'water': 7, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 9},
    'Jamnagar': {'lat': 22.4707, 'lon': 70.0577, 'state': 'Gujarat', 'solar': 8, 'wind': 8, 'gas': 8, 'water': 8, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 10},
    'Surat': {'lat': 21.1702, 'lon': 72.8311, 'state': 'Gujarat', 'solar': 7, 'wind': 6, 'gas': 9, 'water': 9, 'infrastructure': 9, 'demand_center': 9, 'transport_logistics': 9},
    'Vadodara': {'lat': 22.3072, 'lon': 73.1812, 'state': 'Gujarat', 'solar': 8, 'wind': 5, 'gas': 8, 'water': 6, 'infrastructure': 9, 'demand_center': 8, 'transport_logistics': 7},
    'Rajkot': {'lat': 22.3039, 'lon': 70.8022, 'state': 'Gujarat', 'solar': 9, 'wind': 6, 'gas': 6, 'water': 4, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 6},
    'Bhavnagar': {'lat': 21.7645, 'lon': 72.1519, 'state': 'Gujarat', 'solar': 8, 'wind': 7, 'gas': 6, 'water': 8, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 8},
    'Kandla': {'lat': 23.03, 'lon': 70.22, 'state': 'Gujarat', 'solar': 8, 'wind': 9, 'gas': 7, 'water': 9, 'infrastructure': 8, 'demand_center': 6, 'transport_logistics': 10},
    'Porbandar': {'lat': 21.6418, 'lon': 69.6293, 'state': 'Gujarat', 'solar': 8, 'wind': 9, 'gas': 5, 'water': 9, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 9},
    'Anand': {'lat': 22.5645, 'lon': 72.9649, 'state': 'Gujarat', 'solar': 8, 'wind': 4, 'gas': 6, 'water': 6, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 6},
    'Mehsana': {'lat': 23.5880, 'lon': 72.3693, 'state': 'Gujarat', 'solar': 9, 'wind': 5, 'gas': 7, 'water': 4, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 5},
    'Gandhinagar': {'lat': 23.2156, 'lon': 72.6369, 'state': 'Gujarat', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 5, 'infrastructure': 9, 'demand_center': 7, 'transport_logistics': 7},
    'Bharuch': {'lat': 21.7051, 'lon': 72.9959, 'state': 'Gujarat', 'solar': 7, 'wind': 6, 'gas': 9, 'water': 8, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 8},
    'Patan': {'lat': 23.8493, 'lon': 72.1266, 'state': 'Gujarat', 'solar': 9, 'wind': 5, 'gas': 5, 'water': 4, 'infrastructure': 6, 'demand_center': 4, 'transport_logistics': 5},
    'Valsad': {'lat': 20.6333, 'lon': 72.9333, 'state': 'Gujarat', 'solar': 7, 'wind': 7, 'gas': 8, 'water': 9, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 8},
    'Vapi': {'lat': 20.3872, 'lon': 72.9095, 'state': 'Gujarat', 'solar': 7, 'wind': 6, 'gas': 9, 'water': 8, 'infrastructure': 9, 'demand_center': 8, 'transport_logistics': 8},
    'Mundra': {'lat': 22.75, 'lon': 69.7, 'state': 'Gujarat', 'solar': 9, 'wind': 9, 'gas': 6, 'water': 9, 'infrastructure': 8, 'demand_center': 6, 'transport_logistics': 10},
    'Gandhidham': {'lat': 23.0833, 'lon': 70.1333, 'state': 'Gujarat', 'solar': 8, 'wind': 9, 'gas': 7, 'water': 8, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 10},
    'Nadiad': {'lat': 22.6971, 'lon': 72.8628, 'state': 'Gujarat', 'solar': 8, 'wind': 4, 'gas': 6, 'water': 5, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 7},
    'Morbi': {'lat': 22.8167, 'lon': 70.8333, 'state': 'Gujarat', 'solar': 9, 'wind': 7, 'gas': 6, 'water': 5, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 6},

    # --- Maharashtra (20 cities) ---
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777, 'state': 'Maharashtra', 'solar': 6, 'wind': 7, 'gas': 9, 'water': 9, 'infrastructure': 10, 'demand_center': 10, 'transport_logistics': 10},
    'Pune': {'lat': 18.5204, 'lon': 73.8567, 'state': 'Maharashtra', 'solar': 7, 'wind': 5, 'gas': 8, 'water': 5, 'infrastructure': 9, 'demand_center': 9, 'transport_logistics': 8},
    'Nagpur': {'lat': 21.1458, 'lon': 79.0882, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 6, 'water': 4, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 8},
    'Nashik': {'lat': 19.9975, 'lon': 73.7898, 'state': 'Maharashtra', 'solar': 7, 'wind': 6, 'gas': 7, 'water': 6, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 7},
    'Aurangabad': {'lat': 19.8762, 'lon': 75.3433, 'state': 'Maharashtra', 'solar': 8, 'wind': 5, 'gas': 6, 'water': 4, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Solapur': {'lat': 17.6599, 'lon': 75.9064, 'state': 'Maharashtra', 'solar': 8, 'wind': 6, 'gas': 5, 'water': 3, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 6},
    'Amravati': {'lat': 20.9374, 'lon': 77.7796, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 5, 'water': 4, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 5},
    'Ratnagiri': {'lat': 16.9944, 'lon': 73.3002, 'state': 'Maharashtra', 'solar': 6, 'wind': 8, 'gas': 6, 'water': 9, 'infrastructure': 7, 'demand_center': 5, 'transport_logistics': 9},
    'Kolhapur': {'lat': 16.7050, 'lon': 74.2433, 'state': 'Maharashtra', 'solar': 7, 'wind': 6, 'gas': 5, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Raigad': {'lat': 18.35, 'lon': 73.18, 'state': 'Maharashtra', 'solar': 6, 'wind': 8, 'gas': 8, 'water': 9, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 9},
    'Thane': {'lat': 19.2183, 'lon': 72.9781, 'state': 'Maharashtra', 'solar': 6, 'wind': 7, 'gas': 9, 'water': 9, 'infrastructure': 9, 'demand_center': 9, 'transport_logistics': 9},
    'Jalgaon': {'lat': 21.0077, 'lon': 75.5626, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 6, 'water': 5, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Satara': {'lat': 17.6805, 'lon': 74.0183, 'state': 'Maharashtra', 'solar': 7, 'wind': 6, 'gas': 5, 'water': 6, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 7},
    'Latur': {'lat': 18.4088, 'lon': 76.5604, 'state': 'Maharashtra', 'solar': 8, 'wind': 5, 'gas': 4, 'water': 3, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 5},
    'Chandrapur': {'lat': 19.9615, 'lon': 79.2961, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 5, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Navi Mumbai': {'lat': 19.0330, 'lon': 73.0297, 'state': 'Maharashtra', 'solar': 6, 'wind': 7, 'gas': 9, 'water': 9, 'infrastructure': 10, 'demand_center': 9, 'transport_logistics': 10},
    'Akola': {'lat': 20.7009, 'lon': 77.0081, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 5, 'water': 4, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 5},
    'Wardha': {'lat': 20.7453, 'lon': 78.6022, 'state': 'Maharashtra', 'solar': 8, 'wind': 4, 'gas': 6, 'water': 4, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 6},
    'Bhiwandi': {'lat': 19.2967, 'lon': 73.0631, 'state': 'Maharashtra', 'solar': 6, 'wind': 6, 'gas': 8, 'water': 7, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 8},
    'Panvel': {'lat': 18.9880, 'lon': 73.1175, 'state': 'Maharashtra', 'solar': 6, 'wind': 7, 'gas': 8, 'water': 8, 'infrastructure': 9, 'demand_center': 8, 'transport_logistics': 9},

    # --- Uttar Pradesh (20 cities) ---
    'Lucknow': {'lat': 26.8467, 'lon': 80.9462, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 7},
    'Noida': {'lat': 28.5355, 'lon': 77.3910, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 8, 'water': 5, 'infrastructure': 9, 'demand_center': 9, 'transport_logistics': 8},
    'Kanpur': {'lat': 26.4499, 'lon': 80.3319, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 7, 'water': 7, 'infrastructure': 8, 'demand_center': 9, 'transport_logistics': 8},
    'Varanasi': {'lat': 25.3176, 'lon': 82.9739, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 5, 'water': 8, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Agra': {'lat': 27.1767, 'lon': 78.0081, 'state': 'Uttar Pradesh', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 6, 'infrastructure': 7, 'demand_center': 8, 'transport_logistics': 8},
    'Meerut': {'lat': 28.9845, 'lon': 77.7064, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 7, 'water': 5, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 7},
    'Prayagraj': {'lat': 25.4358, 'lon': 81.8463, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 8, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Ghaziabad': {'lat': 28.6692, 'lon': 77.4538, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 8, 'water': 5, 'infrastructure': 9, 'demand_center': 8, 'transport_logistics': 8},
    'Gorakhpur': {'lat': 26.7606, 'lon': 83.3732, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 2, 'gas': 5, 'water': 7, 'infrastructure': 6, 'demand_center': 6, 'transport_logistics': 6},
    'Bareilly': {'lat': 28.3670, 'lon': 79.4304, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Aligarh': {'lat': 27.8974, 'lon': 78.0880, 'state': 'Uttar Pradesh', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 5, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Moradabad': {'lat': 28.8386, 'lon': 78.7733, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Jhansi': {'lat': 25.4484, 'lon': 78.5685, 'state': 'Uttar Pradesh', 'solar': 8, 'wind': 4, 'gas': 5, 'water': 5, 'infrastructure': 6, 'demand_center': 6, 'transport_logistics': 7},
    'Mathura': {'lat': 27.4924, 'lon': 77.6737, 'state': 'Uttar Pradesh', 'solar': 8, 'wind': 4, 'gas': 8, 'water': 6, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Firozabad': {'lat': 27.1563, 'lon': 78.4116, 'state': 'Uttar Pradesh', 'solar': 8, 'wind': 4, 'gas': 7, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Saharanpur': {'lat': 29.964, 'lon': 77.546, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Ayodhya': {'lat': 26.793, 'lon': 82.199, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 5, 'water': 7, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 6},
    'Muzaffarnagar': {'lat': 29.47, 'lon': 77.7, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Mirzapur': {'lat': 25.146, 'lon': 82.56, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 4, 'gas': 5, 'water': 7, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 6},
    'Shahjahanpur': {'lat': 27.88, 'lon': 79.91, 'state': 'Uttar Pradesh', 'solar': 7, 'wind': 3, 'gas': 6, 'water': 6, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 5},

    # --- Tamil Nadu (20 cities) ---
    'Chennai': {'lat': 13.0827, 'lon': 80.2707, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 8, 'gas': 7, 'water': 9, 'infrastructure': 9, 'demand_center': 10, 'transport_logistics': 10},
    'Thoothukudi': {'lat': 8.7642, 'lon': 78.1348, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 10, 'gas': 6, 'water': 9, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 9},
    'Coimbatore': {'lat': 11.0168, 'lon': 76.9558, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 7, 'gas': 5, 'water': 6, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 8},
    'Madurai': {'lat': 9.9252, 'lon': 78.1198, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 6, 'gas': 5, 'water': 6, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Tiruchirappalli': {'lat': 10.7905, 'lon': 78.7047, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 6, 'gas': 6, 'water': 7, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Salem': {'lat': 11.6643, 'lon': 78.1460, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 7, 'gas': 5, 'water': 5, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Tirunelveli': {'lat': 8.7139, 'lon': 77.7567, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 9, 'gas': 5, 'water': 7, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 8},
    'Vellore': {'lat': 12.9165, 'lon': 79.1325, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 5, 'gas': 6, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Erode': {'lat': 11.3410, 'lon': 77.7172, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 6, 'gas': 5, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Kanyakumari': {'lat': 8.0883, 'lon': 77.5385, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 10, 'gas': 5, 'water': 9, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 8},
    'Hosur': {'lat': 12.74, 'lon': 77.82, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 6, 'gas': 6, 'water': 5, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 8},
    'Ramanathapuram': {'lat': 9.3639, 'lon': 78.8357, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 9, 'gas': 6, 'water': 9, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 8},
    'Cuddalore': {'lat': 11.75, 'lon': 79.75, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 8, 'gas': 7, 'water': 9, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 9},
    'Nagapattinam': {'lat': 10.7667, 'lon': 79.85, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 8, 'gas': 7, 'water': 9, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 9},
    'Dindigul': {'lat': 10.3673, 'lon': 77.9803, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 7, 'gas': 5, 'water': 5, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 6},
    'Tiruppur': {'lat': 11.1085, 'lon': 77.3411, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 7, 'gas': 5, 'water': 5, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 7},
    'Thanjavur': {'lat': 10.7870, 'lon': 79.1378, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 6, 'gas': 6, 'water': 7, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Karaikudi': {'lat': 10.0691, 'lon': 78.7797, 'state': 'Tamil Nadu', 'solar': 8, 'wind': 7, 'gas': 5, 'water': 5, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 6},
    'Neyveli': {'lat': 11.5367, 'lon': 79.4886, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 7, 'gas': 6, 'water': 6, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 7},
    'Krishnagiri': {'lat': 12.5204, 'lon': 78.2163, 'state': 'Tamil Nadu', 'solar': 7, 'wind': 6, 'gas': 5, 'water': 5, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},

    # --- Odisha (20 cities) ---
    'Bhubaneswar': {'lat': 20.2961, 'lon': 85.8245, 'state': 'Odisha', 'solar': 6, 'wind': 5, 'gas': 4, 'water': 7, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 7},
    'Paradip': {'lat': 20.2662, 'lon': 86.6698, 'state': 'Odisha', 'solar': 6, 'wind': 7, 'gas': 7, 'water': 9, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 10},
    'Cuttack': {'lat': 20.4625, 'lon': 85.8830, 'state': 'Odisha', 'solar': 6, 'wind': 5, 'gas': 4, 'water': 8, 'infrastructure': 7, 'demand_center': 7, 'transport_logistics': 7},
    'Rourkela': {'lat': 22.2604, 'lon': 84.8536, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 6, 'water': 6, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 6},
    'Puri': {'lat': 19.8135, 'lon': 85.8312, 'state': 'Odisha', 'solar': 6, 'wind': 8, 'gas': 5, 'water': 9, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 8},
    'Sambalpur': {'lat': 21.4704, 'lon': 83.9733, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 5, 'water': 7, 'infrastructure': 6, 'demand_center': 6, 'transport_logistics': 6},
    'Berhampur': {'lat': 19.3159, 'lon': 84.7941, 'state': 'Odisha', 'solar': 6, 'wind': 6, 'gas': 5, 'water': 8, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 7},
    'Balasore': {'lat': 21.4925, 'lon': 86.9325, 'state': 'Odisha', 'solar': 6, 'wind': 7, 'gas': 6, 'water': 8, 'infrastructure': 7, 'demand_center': 5, 'transport_logistics': 8},
    'Gopalpur': {'lat': 19.2667, 'lon': 84.9167, 'state': 'Odisha', 'solar': 6, 'wind': 8, 'gas': 5, 'water': 9, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 9},
    'Jharsuguda': {'lat': 21.8548, 'lon': 84.0326, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 7, 'water': 6, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 6},
    'Angul': {'lat': 20.8354, 'lon': 85.1018, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 6, 'water': 6, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 6},
    'Dhamra': {'lat': 20.7833, 'lon': 86.9833, 'state': 'Odisha', 'solar': 6, 'wind': 7, 'gas': 7, 'water': 9, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 10},
    'Keonjhar': {'lat': 21.6335, 'lon': 85.5843, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 5, 'water': 6, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 5},
    'Koraput': {'lat': 18.8164, 'lon': 82.7161, 'state': 'Odisha', 'solar': 7, 'wind': 5, 'gas': 3, 'water': 5, 'infrastructure': 5, 'demand_center': 4, 'transport_logistics': 4},
    'Rayagada': {'lat': 19.1710, 'lon': 83.4168, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 4, 'water': 6, 'infrastructure': 6, 'demand_center': 5, 'transport_logistics': 5},
    'Jajpur': {'lat': 20.85, 'lon': 86.33, 'state': 'Odisha', 'solar': 6, 'wind': 6, 'gas': 6, 'water': 8, 'infrastructure': 8, 'demand_center': 7, 'transport_logistics': 8},
    'Barbil': {'lat': 22.1167, 'lon': 85.4000, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 5, 'water': 5, 'infrastructure': 7, 'demand_center': 8, 'transport_logistics': 6},
    'Dhenkanal': {'lat': 20.66, 'lon': 85.6, 'state': 'Odisha', 'solar': 7, 'wind': 5, 'gas': 5, 'water': 7, 'infrastructure': 7, 'demand_center': 6, 'transport_logistics': 6},
    'Bhawanipatna': {'lat': 19.9, 'lon': 83.16, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 4, 'water': 5, 'infrastructure': 5, 'demand_center': 5, 'transport_logistics': 4},
    'Talcher': {'lat': 20.95, 'lon': 85.22, 'state': 'Odisha', 'solar': 7, 'wind': 4, 'gas': 7, 'water': 6, 'infrastructure': 8, 'demand_center': 8, 'transport_logistics': 6}
}


def find_closest_hub(user_lat, user_lon):
    """
    Calculates the distance from the user's clicked point to all our pre-defined hubs
    and returns the name and data of the closest one.
    """
    closest_distance = float('inf')
    closest_hub_name = None

    for hub_name, hub_data in HUBS.items():
        # Fixed the distance calculation (changed *2 to **2)
        distance = math.sqrt((hub_data['lat'] - user_lat)**2 + (hub_data['lon'] - user_lon)**2)
        if distance < closest_distance:
            closest_distance = distance
            closest_hub_name = hub_name
            
    return closest_hub_name, HUBS[closest_hub_name]

# Add the analyze endpoint to the same blueprint
@map_bp.route('/analyze', methods=['POST'])
def analyze_location():
    # --- Step 1: Get the user's clicked coordinates from the request ---
    data = request.get_json()
    user_lat = data.get('latitude')
    user_lon = data.get('longitude')

    if user_lat is None or user_lon is None:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    # --- Step 2: Find the closest city hub to base our analysis on ---
    hub_name, hub_data = find_closest_hub(user_lat, user_lon)
    state = hub_data['state']

    # --- Step 3: Calculate feasibility scores for each plant type using weights ---
    
    # Updated weights including the new transport_logistics factor
    weights = {
        'SOLAR_BASED': {'solar': 0.5, 'infrastructure': 0.2, 'demand_center': 0.1, 'water': 0.1, 'transport_logistics': 0.1},
        'ELECTROLYSIS': {'solar': 0.3, 'wind': 0.3, 'infrastructure': 0.15, 'water': 0.15, 'demand_center': 0.05, 'transport_logistics': 0.05},
        'THERMAL': {'gas': 0.5, 'demand_center': 0.2, 'transport_logistics': 0.1, 'water': 0.1, 'infrastructure': 0.1}
    }
    
    # Calculate scores (0-10 scale)
    solar_score = (hub_data['solar'] * weights['SOLAR_BASED']['solar'] +
                   hub_data['infrastructure'] * weights['SOLAR_BASED']['infrastructure'] +
                   hub_data['demand_center'] * weights['SOLAR_BASED']['demand_center'] +
                   hub_data['water'] * weights['SOLAR_BASED']['water'] +
                   hub_data['transport_logistics'] * weights['SOLAR_BASED']['transport_logistics'])

    electrolysis_score = (hub_data['solar'] * weights['ELECTROLYSIS']['solar'] +
                          hub_data['wind'] * weights['ELECTROLYSIS']['wind'] +
                          hub_data['infrastructure'] * weights['ELECTROLYSIS']['infrastructure'] +
                          hub_data['water'] * weights['ELECTROLYSIS']['water'] +
                          hub_data['demand_center'] * weights['ELECTROLYSIS']['demand_center'] +
                          hub_data['transport_logistics'] * weights['ELECTROLYSIS']['transport_logistics'])

    thermal_score = (hub_data['gas'] * weights['THERMAL']['gas'] +
                     hub_data['demand_center'] * weights['THERMAL']['demand_center'] +
                     hub_data['transport_logistics'] * weights['THERMAL']['transport_logistics'] +
                     hub_data['water'] * weights['THERMAL']['water'] +
                     hub_data['infrastructure'] * weights['THERMAL']['infrastructure'])

    # --- Step 4: Determine the recommendation and final feasibility score ---
    
    scores = {
        'SOLAR_BASED': solar_score,
        'ELECTROLYSIS': electrolysis_score,
        'THERMAL': thermal_score
    }
    
    # Find the plant type with the highest score
    recommended_plant_type = max(scores, key=scores.get)
    
    # The feasibility score is the highest score, converted to a percentage (0-100)
    # We add a small random factor to make it look unique for each click
    base_feasibility = scores[recommended_plant_type] * 10
    random_factor = random.uniform(-3.0, 3.0)
    final_feasibility_score = round(max(0, min(100, base_feasibility + random_factor)))

    # --- Step 5: Get the policy advantages for the state ---
    policy_advantages = STATE_POLICIES.get(state, ["No policy information available for this state."])

    # --- Step 6: Prepare and send the final JSON response to the frontend ---
    # Format the response to match what the frontend expects
    recommendation_map = {
        'SOLAR_BASED': {'name': 'Solar Electrolysis', 'bgColor': 'rgba(255, 183, 0, 0.1)', 'textColor': '#B37400'},
        'ELECTROLYSIS': {'name': 'Wind Electrolysis', 'bgColor': 'rgba(0, 201, 255, 0.1)', 'textColor': '#007B9A'},
        'THERMAL': {'name': 'Thermal with CCS', 'bgColor': 'rgba(255, 140, 66, 0.1)', 'textColor': '#B3541E'}
    }
    
    # Generate projection data based on feasibility score
    base_value = final_feasibility_score * 1.5
    projection_values = [
        base_value,
        base_value * 1.25,
        base_value * 1.6,
        base_value * 2.1,
        base_value * 2.8,
        base_value * 3.5
    ]
    projection_values = [round(v) for v in projection_values]
    
    response = {
        "location": {"lat": user_lat, "lng": user_lon},
        "feasibilityScore": final_feasibility_score,
        "recommendation": recommendation_map.get(recommended_plant_type, {"name": "Unknown", "bgColor": "#ccc", "textColor": "#000"}),
        "scores": {
            "solar": round(solar_score * 10),
            "wind": round(electrolysis_score * 10),  # Map electrolysis to wind for frontend
            "thermal": round(thermal_score * 10)
        },
        "projection": {
            "years": ["2025", "2030", "2035", "2040", "2045", "2050"],
            "values": projection_values
        },
        "policyAdvantages": policy_advantages
    }
    
    return jsonify(response)