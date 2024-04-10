import math
import mysql.connector
import folium

def select_center_point(database, table, criteria):
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = connector.cursor()
    cursor.execute(f"SELECT latitude, longitude FROM {table} WHERE {criteria};")
    center_point = cursor.fetchone()
    connector.close()
    return center_point

def generate_grid(cent_point, distance_km):
    grid = []
    cent_lat, cent_lng = cent_point
    del_lat = (distance_km / 111.32) / 9
    del_lng = (distance_km / (111.32 * math.cos(math.radians(cent_lat)))) / 9
    for i in range(9):
        for j in range(9):
            lat = cent_lat + (i - 4) * del_lat
            lng = cent_lng + (j - 4) * del_lng
            grid.append((lat, lng))
    return grid

def store_grid_points(database, table, cent_point, grid, original_table_id):
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = connector.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INT AUTO_INCREMENT PRIMARY KEY, original_id INT, cent_lat FLOAT, cent_lng FLOAT, latitude FLOAT, longitude FLOAT);")
    cent_lat, cent_lng = cent_point
    for point in grid:
        cursor.execute(f"INSERT INTO {table} (original_id, cent_lat, cent_lng, latitude, longitude) VALUES (%s, %s, %s, %s, %s);",
                       (original_table_id, cent_lat, cent_lng, point[0], point[1]))
    connector.commit()
    connector.close()

center_point = (23.0225, 72.5714)  
distance_km = 10
database = 'internetShipDB'
table_original = 'center_points'
table_grid = 'grid_points'
original_table_id = 1

grid = generate_grid(center_point, distance_km)

store_grid_points(database, table_grid, center_point, grid, original_table_id)

map_center = folium.Map(location=center_point, tiles='OpenStreetMap', zoom_start=12)

for point in grid:
    folium.Marker(location=point).add_to(map_center)

map_center.save("mapped.html")
