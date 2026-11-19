
"""Run queries against the flight database."""

import re
import math
from datetime import datetime

FLIGHT_FIELDS = {
    "flight_id", "origin", "destination",
    "departure_datetime", "arrival_datetime", "price"
}

QUERY_KEYS = FLIGHT_FIELDS | {
    "min_price", "sort_by", "order", "limit"
}


def valid_datetime(value):
    if not isinstance(value, str):
        return False

    pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"

    if re.fullmatch(pattern, value) is None:
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def run_query(db: list[dict], query: dict) -> dict:
    invalid = {
        "query": query,
        "error": "INVALID_QUERY",
        "matches": []
    }

    if not isinstance(query, dict):
        return invalid

    if any(key not in QUERY_KEYS for key in query):
        return invalid

    for key, value in query.items():
        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return invalid

        elif key in ("departure_datetime", "arrival_datetime"):
            if not valid_datetime(value):
                return invalid

        elif key in ("price", "min_price"):
            if (isinstance(value, bool) or
                not isinstance(value, (int, float)) or
                not math.isfinite(value)):
                return invalid

        elif key == "sort_by":
            if not isinstance(value, str) or value not in FLIGHT_FIELDS:
                return invalid

        elif key == "order":
            if value not in ("asc", "desc"):
                return invalid

        elif key == "limit":
            if type(value) is not int or value < 0:
                return invalid

    if "order" in query and "sort_by" not in query:
        return invalid

    matches = []

    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue

        if "origin" in query and flight["origin"] != query["origin"]:
            continue

        if "destination" in query and flight["destination"] != query["destination"]:
            continue

        if ("departure_datetime" in query and
            flight["departure_datetime"] < query["departure_datetime"]):
            continue

        if ("arrival_datetime" in query and
            flight["arrival_datetime"] > query["arrival_datetime"]):
            continue

        if "price" in query and flight["price"] > query["price"]:
            continue

        if "min_price" in query and flight["price"] < query["min_price"]:
            continue

        matches.append(flight)

    if "sort_by" in query:
        matches.sort(
            key=lambda flight: flight[query["sort_by"]],
            reverse=query.get("order") == "desc"
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    if (not isinstance(queries, list) or
        any(not isinstance(query, dict) for query in queries)):
        raise ValueError("queries must be an object or array of objects")

    return [run_query(db, query) for query in queries]
