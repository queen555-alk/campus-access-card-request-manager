# Campus Access

A command-line manager for campus access-card requests (visitor, student, staff).
Python standard library only.

Workflow: `requested -> approved -> issued -> returned` (returned is final).

## Team
- Engineer A: registration, validation, unique IDs, lookup, save/load (`storage.py`)
- Engineer B: approve/issue/return workflow and CLI menu

## Project layout
```
campus_access/
├── main.py                  # CLI entry point (Engineer B)
├── storage.py               # request storage and validation (Engineer A)
├── tests/
│   └── test_storage.py      # Engineer A tests
├── docs/
│   ├── design-decisions.md
│   └── ai-learning-log.md
├── README.md
└── .gitignore
```

## Run the tests
```
python -m unittest discover -s tests -v
```

## Request format
```json
{"id": "A001", "fellow_id": "F001", "card_type": "visitor",
 "status": "requested", "approved_by": null}
```

## storage.py functions
| Function | What it does |
|---|---|
| `create_request(fellow_id, card_type)` | Validates, creates the next ID (A001, A002...), returns a copy |
| `get_request(request_id)` | Returns a copy of one request; raises `ValueError` if malformed or unknown |
| `list_requests()` | Returns copies of all requests, sorted by ID |
| `update_request(request_id, status, approved_by)` | Used by Engineer B; validates new values, then stores them |
| `save_requests(path)` | Saves to JSON via a temp file so a failed save keeps the old file |
| `load_requests(path)` | Validates the whole file; replaces stored data only if everything is valid |

All invalid input raises `ValueError`. A rejected operation leaves records unchanged.

## Git workflow
- Engineer A: `feat/1-request-validation`
- Engineer B: `feat/2-access-workflow`
- No direct pushes to `main`. Each PR is reviewed by the other engineer.