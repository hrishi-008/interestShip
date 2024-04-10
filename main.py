import math
import folium
import mysql.connector

# Function to select center point from a database table
def select_center_point(database : 'internetShipDB', table, criteria):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT lat, lng FROM {table} WHERE {criteria};")
    center_point = cursor.fetchone()
    conn.close()
    return center_point

# Function to generate a 9x9 grid of geolocations around the center point
def generate_grid(center_point, distance_km):
    grid = []
    center_lat, center_lng = center_point
    # Calculate the change in latitude and longitude for each grid point
    delta_lat = (distance_km / 111.32) / 9  # 1 degree of latitude is approximately 111.32 km
    delta_lng = (distance_km / (111.32 * math.cos(math.radians(center_lat)))) / 9

    # Generate grid points
    for i in range(9):
        for j in range(9):
            lat = center_lat + (i - 4) * delta_lat
            lng = center_lng + (j - 4) * delta_lng
            grid.append((lat, lng))
    
    return grid

# Function to store grid points in a new table with reference to the previous table
def store_grid_points(database, table, center_point, grid):
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

# Example usage
center_point = (40.7128, -74.0060)  # Example center point (latitude, longitude)
distance_km = 10  # Example distance in kilometers
database = 'internetShipDB'  # Example database name
table_original = 'center_points'  # Example original table name
table_grid = 'grid_points'  # Example new table name

# Select center point from the database
# Assuming the criteria for selection is provided, replace 'criteria' with appropriate condition
# criteria = "some_condition = some_value"
# center_point = select_center_point(database, table_original, criteria)

# Generate grid of geo-locations around the center point
grid = generate_grid(center_point, distance_km)

# Store grid points in a new table with reference to the original table
store_grid_points(database, table_grid, center_point, grid)

# Create a Folium map centered around the center point
map_center = folium.Map(location=center_point, zoom_start=12)

# Add markers for each grid point to the map
for point in grid:
    folium.Marker(location=point).add_to(map_center)

# Save the map to an HTML file
map_center.save("grid_points_map.html")
