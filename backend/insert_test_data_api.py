import requests
from datetime import datetime, timedelta

API_URL = 'http://localhost:5000/api'

# Sample data for 3 batches
batches = [
    {'batch_id': 101, 'personnel': 'Alice', 'drying_method': 'Sun Drying', 'status': 'in_progress'},
    {'batch_id': 102, 'personnel': 'Bob', 'drying_method': 'Oven', 'status': 'in_progress'},
    {'batch_id': 103, 'personnel': 'Charlie', 'drying_method': 'Sun Drying', 'status': 'in_progress'},
]

now = datetime.now()
inputs = [
    {'batch_id': 101, 'wet_harvested': 120, 'wet_placed': 115, 'dried_by_personnel': 'Alice', 'sand_used': 10, 'sand_reused': 5, 'notes': 'Batch 101', 'created_at': (now - timedelta(days=3)).isoformat()},
    {'batch_id': 102, 'wet_harvested': 130, 'wet_placed': 125, 'dried_by_personnel': 'Bob', 'sand_used': 12, 'sand_reused': 6, 'notes': 'Batch 102', 'created_at': (now - timedelta(days=2)).isoformat()},
    {'batch_id': 103, 'wet_harvested': 140, 'wet_placed': 135, 'dried_by_personnel': 'Charlie', 'sand_used': 11, 'sand_reused': 5, 'notes': 'Batch 103', 'created_at': (now - timedelta(days=1)).isoformat()},
]

outputs = [
    {'batch_id': 101, 'dried_produced': 40, 'solar_drying_taken': 10, 'silo_bag_stored': 5, 'dried_sold': 20, 'notes': 'Good yield'},
    {'batch_id': 102, 'dried_produced': 30, 'solar_drying_taken': 8, 'silo_bag_stored': 4, 'dried_sold': 15, 'notes': 'Low yield'},
    {'batch_id': 103, 'dried_produced': 50, 'solar_drying_taken': 12, 'silo_bag_stored': 6, 'dried_sold': 25, 'notes': 'Excellent yield'},
]

def post(endpoint, data):
    url = f"{API_URL}{endpoint}"
    resp = requests.post(url, json=data)
    print(f"POST {endpoint} -> {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    return resp

def main():
    # Insert batches
    for b in batches:
        post('/drying/batch', b)
    # Insert drying input
    for d in inputs:
        d2 = d.copy()
        d2.pop('created_at', None)  # created_at is auto-set by DB
        post('/drying/input', d2)
    # Insert drying output
    for o in outputs:
        post('/drying/output', o)

if __name__ == '__main__':
    main() 