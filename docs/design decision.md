# Design Decisions

Draft by Engineer A. Confirm each answer with Engineer B and edit as agreed.

## 1. What does one request dictionary look like?
```python
{"id": "A001", "fellow_id": "F001", "card_type": "visitor",
 "status": "requested", "approved_by": None}
```
Exactly these five keys. `approved_by` is `None` until approval.

## 2. What should create_request return?
A copy of the new request dictionary, so the caller cannot change stored data by accident.

## 3. How will functions report invalid inputs?
They raise `ValueError` with a clear message. Nothing is written before validation passes.

## 4. Where is the next ID generated?
In `storage.py` (`_next_id`). It takes the highest existing ID number and adds 1, so IDs stay unique after reloading from JSON.

## 5. How will Engineer B call Engineer A's storage functions?
B imports `storage` and uses only `get_request`, `list_requests`, `update_request`, `save_requests` and `load_requests`. B decides whether a transition is legal (for example approved -> issued). A only checks that the new values are valid. B never edits records directly.

## 6. What happens if a saved JSON file is invalid?
`load_requests` raises `ValueError` (or `FileNotFoundError` if the file is missing). Records already in memory and the file on disk are not replaced or wiped. Checks include corrupt JSON, wrong top-level type, missing or extra keys, duplicate IDs, bad statuses and bad IDs.

## 7. Which data must never change on a rejected operation?
Every field of every request: id, fellow_id, card_type, status and approved_by. Updates build a new record, validate it, and only then replace the old one.