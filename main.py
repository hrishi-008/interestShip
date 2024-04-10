'''
Pre-requisites:
1. Install mysql-connector-python
2. Install folium
3. CREATE TABLE IF NOT EXISTS center_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT
);
excecuting the above query in mysql database
4. Replace the database name, username, password in the code
5. Run the code
6. The code will generate a html file named mapped.html which will contain the map with the center point and the grid points
7. The center point is the center of the grid

IMPORTANT - THE MAP.HTML FILE WILL BE GENERATED IN THE SAME DIRECTORY AS THE LOCATION WHERE THE COMMAND IS RUN

'''
import math
import mysql.connector
import folium

def select_or_insert_center_point(database, table, center_point):
    """
    Selects the center point from the database table or inserts it if it doesn't exist.

    Parameters:
        database (str): Name of the MySQL database.
        table (str): Name of the database table containing center points.
        center_point (tuple): Tuple containing the latitude and longitude of the center point.

    Returns:
        int: ID of the center point.
    """
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = connector.cursor()
    cursor.execute(f"SELECT id, latitude, longitude FROM {table} WHERE latitude = %s AND longitude = %s;", center_point)
    existing_center_point = cursor.fetchone()
    if existing_center_point:
        center_id = existing_center_point[0]
    else:
        cursor.execute(f"INSERT INTO {table} (latitude, longitude) VALUES (%s, %s);", center_point)
        center_id = cursor.lastrowid
        connector.commit()
    connector.close()
    return center_id

def generate_grid(center_point, distance_km):
    """
    Generates a 9x9 grid of geolocations around the center point.

    Parameters:
        center_point (tuple): Tuple containing the latitude and longitude of the center point.
        distance_km (float): Distance in kilometers specifying the distance between grid points.

    Returns:
        list: List of tuples containing the latitude and longitude of each grid point.
    """
    grid = []
    cent_lat, cent_lng = center_point
    del_lat = (distance_km / 111.32) / 9  # 1 degree of latitude is approximately 111.32 km
    del_lng = (distance_km / (111.32 * math.cos(math.radians(cent_lat)))) / 9
    for i in range(9):
        for j in range(9):
            lat = cent_lat + (i - 4) * del_lat
            lng = cent_lng + (j - 4) * del_lng
            grid.append((lat, lng))
    return grid

def store_grid_points(database, table, center_id, grid):
    """
    Stores the generated grid points in a new database table with a foreign key linked to the center point.

    Parameters:
        database (str): Name of the MySQL database.
        table (str): Name of the new table to store grid points.
        center_id (int): ID of the center point in the original table.
        grid (list): List of tuples containing the latitude and longitude of each grid point.
    """
    connector = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12373',
        database=database
    )
    cursor = connector.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INT AUTO_INCREMENT PRIMARY KEY, center_id INT, latitude FLOAT, longitude FLOAT, FOREIGN KEY (center_id) REFERENCES center_points(id));")
    for point in grid:
        cursor.execute(f"INSERT INTO {table} (center_id, latitude, longitude) VALUES (%s, %s, %s);",
                       (center_id, point[0], point[1]))
    connector.commit()
    connector.close()

# Example usage
# The center point is the center of the grid, can change it to any other point of interest
# please provide the center point in the form of (latitude, longitude)
center_point = (23.0225, 72.5714)
# You can change the distance_km to generate a different grid
distance_km = 40
database = 'internetshipdb'
table_original = 'center_points'
table_grid = 'grid_points'

center_id = select_or_insert_center_point(database, table_original, center_point)
grid = generate_grid(center_point, distance_km)
store_grid_points(database, table_grid, center_id, grid)

map_center = folium.Map(location=center_point, tiles='OpenStreetMap', zoom_start=12)
folium.Marker(location=center_point, icon=folium.Icon(color='red'),tooltip='Center Point').add_to(map_center)
for point in grid:
    if point != center_point:
        folium.Marker(location=point, tooltip=f'Coordinates: {point}').add_to(map_center)

map_center.save("mapped.html")
