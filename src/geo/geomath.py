import numpy as np
import math

from typing import List, Tuple


def vec_haversine(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> np.ndarray:
    """
    Vectorized haversine distance calculation
    :param lat1: Array of initial latitudes in degrees
    :param lon1: Array of initial longitudes in degrees
    :param lat2: Array of destination latitudes in degrees
    :param lon2: Array of destination longitudes in degrees
    :return: Array of distances in meters
    """
    earth_radius = 6378137.0

    rad_lat1 = np.radians(lat1)
    rad_lon1 = np.radians(lon1)
    rad_lat2 = np.radians(lat2)
    rad_lon2 = np.radians(lon2)

    d_lon = rad_lon2 - rad_lon1
    d_lat = rad_lat2 - rad_lat1

    a = np.sin(d_lat / 2.0) ** 2 + np.multiply(
        np.multiply(np.cos(rad_lat1), np.cos(rad_lat2)), np.sin(d_lon / 2.0) ** 2
    )

    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    meters = earth_radius * c
    return meters


def num_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine distance calculation
    :param lat1: Initial latitude in degrees
    :param lon1: Initial longitude in degrees
    :param lat2: Destination latitude in degrees
    :param lon2: Destination longitude in degrees
    :return: Distances in meters
    """
    earth_radius = 6378137.0

    rad_lat1 = math.radians(lat1)
    rad_lon1 = math.radians(lon1)
    rad_lat2 = math.radians(lat2)
    rad_lon2 = math.radians(lon2)

    d_lon = rad_lon2 - rad_lon1
    d_lat = rad_lat2 - rad_lat1

    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lon / 2.0) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    meters = c * earth_radius
    return meters


def outer_haversine(lat1: np.ndarray,
                    lon1: np.ndarray,
                    lat2: np.ndarray,
                    lon2: np.ndarray) -> np.ndarray:
    matrix = np.zeros((lat1.shape[0], lat2.shape[0]))
    for i in range(lat1.shape[0]):
        matrix[i, :] = vec_haversine(lat2, lon2, lat1[i], lon1[i])
    return matrix


def delta_location(lat: float,
                   lon: float,
                   bearing: float,
                   meters: float) -> Tuple[float, float]:
    """
    Calculates a destination location from a starting location, a bearing and a
    distance in meters.
    :param lat: Start latitude
    :param lon: Start longitude
    :param bearing: Bearing (North is zero degrees, measured clockwise)
    :param meters: Distance to displace from the starting point
    :return: Tuple with the new latitude and longitude
    """
    delta = meters / 6378137.0
    theta = math.radians(bearing)
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    lat_r2 = math.asin(math.sin(lat_r) * math.cos(delta) + math.cos(lat_r) *
                       math.sin(delta) * math.cos(theta))
    lon_r2 = lon_r + math.atan2(math.sin(theta) * math.sin(delta) *
                                math.cos(lat_r),
                                math.cos(delta) - math.sin(lat_r) *
                                math.sin(lat_r2))
    return math.degrees(lat_r2), math.degrees(lon_r2)


def x_meters_to_degrees(meters: float,
                        lat: float,
                        lon: float) -> float:
    """
    Converts a horizontal distance in meters to an angle in degrees.
    :param meters: Distance to convert
    :param lat: Latitude of reference location
    :param lon: Longitude of reference location
    :return: Horizontal angle in degrees
    """
    _, lon2 = delta_location(lat, lon, 90, meters)
    return abs(lon - lon2)


def y_meters_to_degrees(meters: float,
                        lat: float,
                        lon: float) -> float:
    """
    Converts a vertical distance in meters to an angle in degrees.
    :param meters: Distance to convert
    :param lat: Latitude of reference location
    :param lon: Longitude of reference location
    :return: Vertical angle in degrees
    """
    lat2, _ = delta_location(lat, lon, 0, meters)
    return abs(lat - lat2)


def vec_bearings(latitudes: np.ndarray,
                 longitudes: np.ndarray) -> np.ndarray:
    r_lats = np.radians(latitudes)
    r_lons = np.radians(longitudes)
    r_lat1 = r_lats[1:]
    r_lat0 = r_lats[:-1]

    delta_lons = r_lons[1:] - r_lons[:-1]

    y = np.multiply(np.sin(delta_lons), np.cos(r_lat1))
    x = np.multiply(np.cos(r_lat0), np.sin(r_lat1)) - \
        np.multiply(np.sin(r_lat0), np.multiply(np.cos(r_lat1), np.cos(delta_lons)))
    bearings = (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0
    return bearings


def num_bearing(lat0: float, lon0: float, lat1: float, lon1: float) -> float:
    return float(vec_bearings(np.array([lat0, lat1]), np.array([lon0, lon1]))[0])


def heron_area(a: float, b: float, c: float) -> float:
    c, b, a = np.sort(np.array([a, b, c]))
    return math.sqrt((a + (b + c)) *
                     (c - (a - b)) *
                     (c + (a - b)) *
                     (a + (b - c))) / 4.0


def heron_distance(a: float, b: float, c: float) -> float:
    c, b, a = np.sort(np.array([a, b, c]))
    area: float = math.sqrt((a + (b + c)) *
                            (c - (a - b)) *
                            (c + (a - b)) *
                            (a + (b - c))) / 4
    return 2 * area / b


def decode_polyline(encoded: str,
                    order: str = "lonlat") -> List[List]:
    """
    Code drawn from https://valhalla.github.io/valhalla/decoding/
    :param order: Coordinate order: 'lonlat' (default) or 'latlon'
    :param encoded: String-encoded polyline
    :return: Decoded polyline as a list of [lat, lon] coordinates
    """
    inv = 1.0 / 1e6
    decoded = []
    previous = [0, 0]
    i = 0
    # for each byte
    while i < len(encoded):
        # for each coord (lat, lon)
        ll = [0, 0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            # keep decoding bytes until you have this coord
            while byte >= 0x20:
                byte = ord(encoded[i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            # get the final value adding the previous offset and remember it for the next
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        # scale by the precision and chop off long coords also flip the positions so
        # its the far more standard lon,lat instead of lat,lon
        if order == "lonlat":
            decoded.append([float('%.6f' % (ll[1] * inv)), float('%.6f' % (ll[0] * inv))])
        else:
            decoded.append([float('%.6f' % (ll[0] * inv)), float('%.6f' % (ll[1] * inv))])
    # hand back the list of coordinates
    return decoded
