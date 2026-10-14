"""Engineer A: request creation, validation, lookup, save and load."""
import json
import os
import re

CARD_TYPES = ("visitor", "student", "staff")
STATUSES = ("requested", "approved", "issued", "returned")
ID_PATTERN = re.compile(r"A[0-9]{3,}") 

_requests = {}  


def _check_id(request_id):
    if not isinstance(request_id, str) or not ID_PATTERN.fullmatch(request_id):
        raise ValueError(f"Malformed request ID: {request_id!r}")


def _check_record(record):
    """Validate one request dict. Raises ValueError if anything is wrong."""
    if not isinstance(record, dict):
        raise ValueError("Request must be an object")
    needed = {"id", "fellow_id", "card_type", "status", "approved_by"}
    if set(record) != needed:
        raise ValueError(f"Request keys must be exactly {sorted(needed)}")
    _check_id(record["id"])
    fellow = record["fellow_id"]
    if not isinstance(fellow, str) or not fellow.strip():
        raise ValueError("fellow_id must be a nonempty string")
    if record["card_type"] not in CARD_TYPES:
        raise ValueError(f"card_type must be one of {CARD_TYPES}")
    if record["status"] not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    approver = record["approved_by"]
    if approver is not None and (not isinstance(approver, str) or not approver.strip()):
        raise ValueError("approved_by must be null or a nonempty string")
    if record["status"] == "requested" and approver is not None:
        raise ValueError("A requested record cannot have approved_by")
    if record["status"] != "requested" and approver is None:
        raise ValueError("Approved/issued/returned records need approved_by")


def _next_id():
    """Next ID is based on the highest existing one, so it survives reloads."""
    highest = max((int(r_id[1:]) for r_id in _requests), default=0)
    return f"A{highest + 1:03d}"


def create_request(fellow_id, card_type):
    """Validate first, then write. Returns a copy of the new request."""
    if not isinstance(fellow_id, str) or not fellow_id.strip():
        raise ValueError("fellow_id must be a nonempty string")
    if card_type not in CARD_TYPES:
        raise ValueError(f"card_type must be one of {CARD_TYPES}")
    record = {
        "id": _next_id(),
        "fellow_id": fellow_id.strip(),
        "card_type": card_type,
        "status": "requested",
        "approved_by": None,
    }
    _requests[record["id"]] = record
    return dict(record)


def get_request(request_id):
    """Read-only lookup: returns a COPY, so callers cannot change storage."""
    _check_id(request_id)
    if request_id not in _requests:
        raise ValueError(f"Unknown request ID: {request_id}")
    return dict(_requests[request_id])


def list_requests():
    return [dict(_requests[k]) for k in sorted(_requests)]


def update_request(request_id, status, approved_by):
    """Contract for Engineer B: B decides WHEN a transition is legal,
    A only checks the new values are valid, then stores them."""
    old = get_request(request_id)  # raises on bad/unknown ID
    new = dict(old, status=status, approved_by=approved_by)
    _check_record(new)  # validate BEFORE touching storage
    _requests[request_id] = new
    return dict(new)


def save_requests(path):
    """Write to a temp file first, then swap, so a failed save keeps the old file."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(list_requests(), f, indent=2)
    os.replace(tmp, path)


def load_requests(path):
    """Validate everything into a new dict; only replace storage if all is valid."""
    with open(path) as f:  # FileNotFoundError propagates
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupt JSON file: {e}")
    if not isinstance(data, list):
        raise ValueError("File must contain a list of requests")
    loaded = {}
    for record in data:
        _check_record(record)
        if record["id"] in loaded:
            raise ValueError(f"Duplicate ID in file: {record['id']}")
        loaded[record["id"]] = record
    _requests.clear()
    _requests.update(loaded)


def reset():
    """For tests only."""
    _requests.clear()

# storage.py

_REQUESTS = {}          # or however storage already keeps state
_NEXT_ID = 1


def add_request(holder):
    """Create a new 'requested' record and return it."""
    global _NEXT_ID
    req = {
        "id": str(_NEXT_ID),
        "holder": holder,
        "status": "requested",
        "approved_by": None,
    }
    _REQUESTS[req["id"]] = req
    _NEXT_ID += 1
    return req


def list_requests():
    """Return all records."""
    return list(_REQUESTS.values())


def reset_storage():
    """Clear all state. Used by tests."""
    global _NEXT_ID
    _REQUESTS.clear()
    _NEXT_ID = 1