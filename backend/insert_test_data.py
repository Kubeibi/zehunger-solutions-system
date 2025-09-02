import mysql.connector

# --- CONFIGURE THESE ---
DB_CONFIG = {
    'user': 'root',
    'password': 'kubai@123',
    'host': 'localhost',
    'database': 'bsf_farm'
}

# --- TEST DATA ---
batches = [
    {'batch_id': 10, 'personnel': 'Alice', 'drying_method': 'Sun Drying', 'status': 'in_progress', 'drying_date': '2023-01-10'},
    {'batch_id': 11, 'personnel': 'Bob', 'drying_method': 'Oven', 'status': 'in_progress', 'drying_date': '2023-02-15'},
    {'batch_id': 12, 'personnel': 'Charlie', 'drying_method': 'Sun Drying', 'status': 'in_progress', 'drying_date': '2024-03-10'},
    {'batch_id': 13, 'personnel': 'Dana', 'drying_method': 'Oven', 'status': 'in_progress', 'drying_date': '2024-04-18'},
    {'batch_id': 14, 'personnel': 'Eve', 'drying_method': 'Sun Drying', 'status': 'in_progress', 'drying_date': '2024-05-25'},
]

drying_inputs = [
    {'batch_id': 10, 'wet_harvested': 120, 'wet_placed': 115, 'dried_by_personnel': 'Alice', 'sand_used': 10, 'sand_reused': 5, 'notes': '2023 batch A'},
    {'batch_id': 11, 'wet_harvested': 130, 'wet_placed': 125, 'dried_by_personnel': 'Bob', 'sand_used': 12, 'sand_reused': 6, 'notes': '2023 batch B'},
    {'batch_id': 12, 'wet_harvested': 140, 'wet_placed': 135, 'dried_by_personnel': 'Charlie', 'sand_used': 11, 'sand_reused': 5, 'notes': '2024 batch A'},
    {'batch_id': 13, 'wet_harvested': 150, 'wet_placed': 145, 'dried_by_personnel': 'Dana', 'sand_used': 13, 'sand_reused': 7, 'notes': '2024 batch B'},
    {'batch_id': 14, 'wet_harvested': 160, 'wet_placed': 155, 'dried_by_personnel': 'Eve', 'sand_used': 14, 'sand_reused': 8, 'notes': '2024 batch C'},
]

drying_outputs = [
    {'batch_id': 10, 'dried_produced': 40, 'solar_drying_taken': 10, 'silo_bag_stored': 5, 'dried_sold': 20, 'actual_ratio': 0.35, 'yield_percentage': 35.0, 'notes': 'Good yield'},
    {'batch_id': 11, 'dried_produced': 30, 'solar_drying_taken': 8, 'silo_bag_stored': 4, 'dried_sold': 15, 'actual_ratio': 0.24, 'yield_percentage': 24.0, 'notes': 'Low yield'},
    {'batch_id': 12, 'dried_produced': 50, 'solar_drying_taken': 12, 'silo_bag_stored': 6, 'dried_sold': 25, 'actual_ratio': 0.37, 'yield_percentage': 37.0, 'notes': 'Excellent yield'},
    {'batch_id': 13, 'dried_produced': 35, 'solar_drying_taken': 9, 'silo_bag_stored': 5, 'dried_sold': 18, 'actual_ratio': 0.24, 'yield_percentage': 24.1, 'notes': 'Below expected'},
    {'batch_id': 14, 'dried_produced': 60, 'solar_drying_taken': 15, 'silo_bag_stored': 7, 'dried_sold': 30, 'actual_ratio': 0.39, 'yield_percentage': 39.0, 'notes': 'Very efficient'},
]

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Insert batches
    for b in batches:
        cursor.execute(
            "INSERT INTO drying_batches (batch_id, personnel, drying_method, status, drying_date) VALUES (%s, %s, %s, %s, %s)",
            (b['batch_id'], b['personnel'], b['drying_method'], b['status'], b['drying_date'])
        )

    # Insert drying_input
    for d in drying_inputs:
        cursor.execute(
            "INSERT INTO drying_input (batch_id, wet_harvested, wet_placed, dried_by_personnel, sand_used, sand_reused, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (d['batch_id'], d['wet_harvested'], d['wet_placed'], d['dried_by_personnel'], d['sand_used'], d['sand_reused'], d['notes'])
        )

    # Insert drying_output (no drying_date)
    for d in drying_outputs:
        cursor.execute(
            "INSERT INTO drying_output (batch_id, dried_produced, solar_drying_taken, silo_bag_stored, dried_sold, actual_ratio, yield_percentage, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (d['batch_id'], d['dried_produced'], d['solar_drying_taken'], d['silo_bag_stored'], d['dried_sold'], d['actual_ratio'], d['yield_percentage'], d['notes'])
        )

    conn.commit()
    print('Test data inserted successfully!')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main() 