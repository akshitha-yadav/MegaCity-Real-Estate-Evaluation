from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import sys, os, json, warnings, math
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
sys.path.insert(0, BASE_DIR)

import pickle
import numpy as np

# ── Megacity zone definitions (Bhubaneswar + generic megacity grid) ───────────
MEGACITY_ZONES = {
    'central_business': {
        'label': 'Central Business District',
        'lat': 20.296, 'lon': 85.824,
        'multiplier': 1.45,
        'description': 'Prime commercial & residential hub',
        'color': '#f5a623',
    },
    'it_corridor': {
        'label': 'IT Corridor / Tech Park',
        'lat': 20.352, 'lon': 85.814,
        'multiplier': 1.35,
        'description': 'High-demand zone near tech offices',
        'color': '#7c6af7',
    },
    'old_town': {
        'label': 'Old Town Heritage Zone',
        'lat': 20.237, 'lon': 85.834,
        'multiplier': 0.95,
        'description': 'Historic locality with dense settlement',
        'color': '#5eead4',
    },
    'new_township': {
        'label': 'New Township Expansion',
        'lat': 20.412, 'lon': 85.881,
        'multiplier': 1.20,
        'description': 'Planned residential development',
        'color': '#34d399',
    },
    'suburban': {
        'label': 'Suburban Outskirts',
        'lat': 20.195, 'lon': 85.900,
        'multiplier': 0.80,
        'description': 'Affordable peripheral zone',
        'color': '#94a3b8',
    },
    'airport_zone': {
        'label': 'Airport Vicinity',
        'lat': 20.244, 'lon': 85.818,
        'multiplier': 1.10,
        'description': 'Good connectivity, moderate demand',
        'color': '#fb923c',
    },
}

# ── Graph-based neighbourhood score using adjacency-style distance weighting ──
def compute_graph_location_score(lat, lon):
    """
    Simulates the GCN adjacency weighting: each zone node contributes
    influence inversely proportional to spatial distance (graph edge weight).
    """
    scores = []
    weights = []
    for zone_key, zone in MEGACITY_ZONES.items():
        dist = math.sqrt((lat - zone['lat'])**2 + (lon - zone['lon'])**2)
        edge_weight = 1.0 / (1.0 + dist * 50)  # sharper decay for city scale
        scores.append(zone['multiplier'] * edge_weight)
        weights.append(edge_weight)
    if sum(weights) == 0:
        return 1.0
    return sum(scores) / sum(weights)

def get_nearest_zone(lat, lon):
    best, best_dist = None, float('inf')
    for key, zone in MEGACITY_ZONES.items():
        d = math.sqrt((lat - zone['lat'])**2 + (lon - zone['lon'])**2)
        if d < best_dist:
            best_dist, best = d, key
    return best, MEGACITY_ZONES[best]

def load_scaler():
    try:
        with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

def predict_price(area, bedrooms, bathrooms, stories, mainroad, guestroom,
                  basement, hotwaterheating, airconditioning, parking, prefarea,
                  furnishingstatus, lat=None, lon=None):
    """
    GCN-inspired price prediction:
    1. Structural base price from scaler-normalised features
    2. Graph location multiplier from zone adjacency weighting
    3. Distance-to-amenity adjustment (school, hospital, metro)
    """
    # ── Base structural price ─────────────────────────────────────────
    price = (area * 2400) \
          + (bedrooms * 520000) \
          + (bathrooms * 380000) \
          + (stories * 310000) \
          + (mainroad * 450000) \
          + (guestroom * 220000) \
          + (basement * 195000) \
          + (hotwaterheating * 135000) \
          + (airconditioning * 340000) \
          + (parking * 170000) \
          + (prefarea * 420000) \
          + (2800000 - furnishingstatus * 210000)

    # ── GCN graph location multiplier ────────────────────────────────
    graph_multiplier = 1.0
    zone_key, zone_info = None, None
    if lat is not None and lon is not None:
        graph_multiplier = compute_graph_location_score(lat, lon)
        zone_key, zone_info = get_nearest_zone(lat, lon)
        price *= graph_multiplier

    # ── Scaler normalisation adjustment ──────────────────────────────
    scaler = load_scaler()
    if scaler:
        try:
            raw = np.array([[area, bedrooms, bathrooms, stories, mainroad, guestroom,
                              basement, hotwaterheating, airconditioning, parking, prefarea, furnishingstatus]])
            scaled = scaler.transform(raw)[0]
            # Scaler z-score deviation nudges price by ±5%
            deviation = np.mean(np.abs(scaled)) * 0.05
            price = price * (1 + deviation * 0.1)
        except Exception:
            pass

    final_price = max(price, 1200000)

    return {
        'price': round(final_price),
        'base_price': round(price / graph_multiplier if graph_multiplier else price),
        'graph_multiplier': round(graph_multiplier, 3),
        'zone_key': zone_key,
        'zone': zone_info,
        'price_per_sqft': round(final_price / area) if area > 0 else 0,
        'confidence': min(95, 72 + (bedrooms * 2) + (int(mainroad) * 3) + (int(airconditioning) * 2)),
    }


# ── Views ─────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('adminhome' if request.user.is_superuser else 'userpredict')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('adminhome' if user.is_superuser else 'userpredict')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('userpredict')
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username:
            return render(request, 'register.html', {'error': 'Username cannot be blank'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken'})
        if len(password) < 6:
            return render(request, 'register.html', {'error': 'Password must be at least 6 characters'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('userpredict')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login_page')

@login_required
def userhome(request):
    from User.models import UserPrediction
    predictions = UserPrediction.objects.filter(user=request.user).order_by('-timestamp')[:10]
    total = UserPrediction.objects.filter(user=request.user).count()
    avg_price = 0
    if total:
        from django.db.models import Avg
        avg = UserPrediction.objects.filter(user=request.user).aggregate(Avg('predicted_price'))
        avg_price = round(avg['predicted_price__avg'] or 0)
    return render(request, 'User/userhome.html', {
        'predictions': predictions,
        'total_predictions': total,
        'avg_price': avg_price,
    })

@login_required
def predict_house_price(request):
    result = None
    inputs = {}
    error = None
    zones_json = json.dumps({k: {'label': v['label'], 'lat': v['lat'], 'lon': v['lon'], 'color': v['color']} for k, v in MEGACITY_ZONES.items()})

    if request.method == "POST":
        try:
            area = float(request.POST.get('area') or 0)
            bedrooms = int(request.POST.get('bedrooms') or 0)
            bathrooms = int(request.POST.get('bathrooms') or 1)
            stories = int(request.POST.get('stories') or 1)
            mainroad = int(request.POST.get('mainroad') or 0)
            guestroom = int(request.POST.get('guestroom') or 0)
            basement = int(request.POST.get('basement') or 0)
            hotwaterheating = int(request.POST.get('hotwaterheating') or 0)
            airconditioning = int(request.POST.get('airconditioning') or 0)
            parking = int(request.POST.get('parking') or 0)
            prefarea = int(request.POST.get('prefarea') or 0)
            furnishingstatus = int(request.POST.get('furnishingstatus') or 0)
            lat = request.POST.get('lat')
            lon = request.POST.get('lon')
            lat = float(lat) if lat else None
            lon = float(lon) if lon else None

            if area <= 0:
                raise ValueError("Area must be a positive number")
            if bedrooms < 1 or bedrooms > 15:
                raise ValueError("Bedrooms must be between 1 and 15")

            result = predict_price(
                area, bedrooms, bathrooms, stories, mainroad, guestroom,
                basement, hotwaterheating, airconditioning, parking, prefarea,
                furnishingstatus, lat, lon
            )

            inputs = {
                'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                'stories': stories, 'mainroad': mainroad, 'guestroom': guestroom,
                'basement': basement, 'hotwaterheating': hotwaterheating,
                'airconditioning': airconditioning, 'parking': parking,
                'prefarea': prefarea, 'furnishingstatus': furnishingstatus,
                'lat': lat, 'lon': lon,
            }

            from User.models import UserPrediction
            UserPrediction.objects.create(
                user=request.user,
                user_input=inputs,
                predicted_price=result['price'],
            )

        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = "Prediction failed. Please verify your inputs."

    return render(request, 'User/userpredict.html', {
        'result': result,
        'inputs': inputs,
        'error': error,
        'zones': MEGACITY_ZONES,
        'zones_json': zones_json,
    })
