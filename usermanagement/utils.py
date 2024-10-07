from math import radians, cos, sin, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c  # Radius of earth in kilometers. Use 3956 for miles

    return distance

# user_lat, user_lon = map(float, "12.9716,77.5946".split(','))
# shop_lat, shop_lon = map(float, "19.9716,47.5946".split(','))
# distance = calculate_distance(user_lat, user_lon, shop_lat, shop_lon)
# print(f"Distance: {distance:.2f} km")