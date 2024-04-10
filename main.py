import math
import folium
import mysql.connector

def select_center_point(database : 'internetShipDB', table, criteria):
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = connector.cursor()
    cursor.execute(f"SELECT lat, lng FROM {table} WHERE {criteria};")
    center_point = cursor.fetchone()
    connector.close()
    return center_point

def generate_grid(center_point, distance_km):
    grid = []
    center_lat, center_lng = center_point
    delta_lat = (distance_km / 111.32) / 9  
    delta_lng = (distance_km / (111.32 * math.cos(math.radians(center_lat)))) / 9

    for i in range(9):
        for j in range(9):
            lat = center_lat + (i - 4) * delta_lat
            lng = center_lng + (j - 4) * delta_lng
            grid.append((lat, lng))

    return grid


def store_grid_points(database:'internetShipDB', table, center_point, grid):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INT AUTO_INCREMENT PRIMARY KEY, center_lat FLOAT, center_lng FLOAT, grid_lat FLOAT, grid_lng FLOAT);")
    center_lat, center_lng = center_point

    for point in grid:
        cursor.execute(f"INSERT INTO {table} (center_lat, center_lng, grid_lat, grid_lng) VALUES (%s, %s, %s, %s);",
                       (center_lat, center_lng, point[0], point[1]))
    conn.commit()
    conn.close()

center_point = (40.7128, -74.0060)  
distance_km = 10  
database = 'internetShipDB'  
table_original = 'center_points'  
table_grid = 'grid_points'

grid = generate_grid(center_point, distance_km)

store_grid_points(database, table_grid, center_point, grid)

map_center = folium.Map(location=center_point, zoom_start=12)

for point in grid:
    folium.Marker(location=point).add_to(map_center)

map_center.save("mapped.html")

