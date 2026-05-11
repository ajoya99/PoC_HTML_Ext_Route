from __future__ import annotations

import json
import math
from math import atan2, cos, radians, sin, sqrt
from itertools import permutations
from pathlib import Path
from typing import Callable
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
NOTEBOOK_PATH = BASE_DIR / "Google_maps_model_5.ipynb"

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")


def load_haversine_from_notebook(notebook_path: Path) -> Callable[[float, float, float, float], float]:
    """Load the haversine function from Google_maps_model_5.ipynb."""
    with notebook_path.open("r", encoding="utf-8") as f:
        notebook_data = json.load(f)

    for cell in notebook_data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "def haversine(" not in source:
            continue

        # The notebook defines haversine in a separate cell from imports,
        # so we provide required math symbols explicitly.
        namespace: dict[str, object] = {
            "sin": sin,
            "cos": cos,
            "atan2": atan2,
            "sqrt": sqrt,
            "radians": radians,
        }
        exec(source, namespace)
        func = namespace.get("haversine")
        if callable(func):
            return func

    raise RuntimeError("Could not find haversine function in Google_maps_model_5.ipynb")


HAVERSINE = load_haversine_from_notebook(NOTEBOOK_PATH)


def geocode_location(address: str) -> tuple[float, float]:
    """Resolve a free-text address to latitude/longitude via Nominatim."""
    url = (
        "https://nominatim.openstreetmap.org/search?format=json"
        "&limit=1&q=" + quote(address)
    )
    req = Request(url, headers={"User-Agent": "PoC_HTML_Ext_Route/1.0"})
    with urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not payload:
        raise ValueError(f"Could not geocode location: {address}")

    return float(payload[0]["lat"]), float(payload[0]["lon"])


def route_distance_km(route: tuple[int, ...], coords: list[tuple[float, float]]) -> float:
    distance = 0.0
    for i in range(len(route) - 1):
        lat1, lon1 = coords[route[i]]
        lat2, lon2 = coords[route[i + 1]]
        distance += HAVERSINE(lat1, lon1, lat2, lon2)
    return distance


def optimize_route_for_four_locations(addresses: list[str]) -> dict[str, object]:
    """
    Exact TSP for 4 locations.
    First entered location is treated as start/end depot.
    """
    coords = [geocode_location(addr) for addr in addresses]

    start = 0
    candidates = [1, 2, 3]

    best_route: tuple[int, ...] | None = None
    best_distance = math.inf

    for perm in permutations(candidates):
        route = (start, *perm, start)
        dist = route_distance_km(route, coords)
        if dist < best_distance:
            best_distance = dist
            best_route = route

    if best_route is None:
        raise RuntimeError("No valid route was found")

    ordered_locations = [addresses[i] for i in best_route]
    ordered_coords = [coords[i] for i in best_route]

    maps_link = "https://www.google.com/maps/dir/" + "/".join(
        f"{lat},{lon}" for lat, lon in ordered_coords
    )

    return {
        "ordered_locations": ordered_locations,
        "ordered_coordinates": ordered_coords,
        "total_distance_km": round(best_distance, 2),
        "maps_link": maps_link,
    }


@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "landing.html")


@app.post("/api/route")
def route_api():
    body = request.get_json(silent=True) or {}
    locations = body.get("locations", [])

    if not isinstance(locations, list):
        return jsonify({"error": "'locations' must be a list of strings"}), 400

    cleaned = [str(value).strip() for value in locations if str(value).strip()]
    if len(cleaned) != 4:
        return jsonify({"error": "Please provide exactly 4 locations."}), 400

    try:
        result = optimize_route_for_four_locations(cleaned)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
