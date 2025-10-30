import requests
from typing import Dict, List, Tuple


class RouteCalculator:

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.osrm_url = "https://router.project-osrm.org"
    def geocode_address(self, address: str) -> Tuple[float, float]:
        url = f"{self.nominatim_url}/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "TruckRoutingApp/1.0" 
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError(f"Could not geocode address: '{address}'")

            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f" Geocoded '{address}' → ({lat}, {lon})")
            return (lat, lon)

        except requests.RequestException as e:
            print(f" Geocoding request failed for '{address}': {e}")
            raise
        except ValueError as e:
            print(f" {e}")
            raise

    def calculate_route(self, waypoints: List[Tuple[float, float]]) -> Dict:
        if not waypoints or len(waypoints) < 2:
            raise ValueError("At least two waypoints are required for routing.")

        coords_str = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
        url = f"{self.osrm_url}/route/v1/driving/{coords_str}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 'Ok' or not data.get('routes'):
                raise ValueError(f"Route calculation error: {data.get('code', 'Unknown')}")

            route = data['routes'][0]
            distance_miles = route['distance'] / 1609.34  
            duration_hours = route['duration'] / 3600      

            print(f" Route calculated: {distance_miles:.1f} miles, {duration_hours:.1f} hours")

            return {
                "distance": distance_miles,
                "duration": duration_hours,
                "geometry": route['geometry'],
                "coordinates": [[c[1], c[0]] for c in route['geometry']['coordinates']],
                "instructions": route['legs'][0]['steps'] if route['legs'] else []
            }

        except requests.RequestException as e:
            print(f" Route calculation request failed: {e}")
            raise
        except ValueError as e:
            print(f"{e}")
            raise

    def calculate_fuel_stops(self, route_distance: float) -> List[float]:
        fuel_stops = []
        current_distance = 1000

        while current_distance < route_distance:
            fuel_stops.append(current_distance)
            current_distance += 1000

        return fuel_stops
