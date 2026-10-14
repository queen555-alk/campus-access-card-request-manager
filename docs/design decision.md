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

# Engineer B
I split my work into two modules with one job each: workflow.py enforces
the state machine and never calls print() or input(), while cli.py
talks to the user and holds no business rules. This boundary is what lets me
test every workflow rule directly without simulating a user at a prompt, and
it means workflow.py stays strict while cli.py stays forgiving. The
state machine I enforce is requested → approved → issued → returned, with
rejected reachable from requested or approved and returned/rejected
both terminal; every illegal transition raises WorkflowError with no silent
no-ops, and issue_card additionally refuses an approved record that has
no approver on it.

Every function in workflow.py follows the same three-step order: load the
record (raising if missing), validate status and preconditions, and only then
call update_request. I chose this "validate before mutate" rule because a
failure that half-changes a record would be a nightmare to debug from a CLI,
and it lets me prove atomicity with a single test that snapshots the record
before a failing call and asserts it is identical afterward. Errors are
exceptions rather than return codes so the caller cannot accidentally ignore
a failure, cli.py can catch one type and print one message, and the public
API stays tiny; success paths return the updated record.

cli.py::run_menu catches WorkflowError and a last-resort Exception
inside the loop, prints a readable message, and re-shows the menu, so typos,
blank input, and unknown options never crash the app. I deliberately do not
silently retry the same operation on failure — the loop returns to the menu
so the user can see the current state and choose again, because blind retries
hide problems. This split of concerns — strict correctness in workflow.py,
user-facing safety net in cli.py — is also what keeps the two files
independently testable and reviewable.

I do not own storage.py, so I pinned the contract I depend on: get_request
returns a dict or None and never raises on missing IDs, update_request
merges fields and returns the record, add_request creates a requested
record with a new id, list_requests returns an iterable, and
reset_storage clears state for tests. If any of these change, my module
and my tests need to change with them, which is why the contract lives here
in writing rather than only in my head. Anything that would violate the
contract — a get_request that raises, or an add_request that returns
something other than the record — would make my tests flaky and my error
handling wrong.

My tests in tests/test_workflow.py cover four categories: every legal
transition, every illegal transition (wrong starting state, re-entry into a
terminal state, unknown IDs), input validation for blank and None
approvers, and atomicity of failed calls. An autouse fixture calls
reset_storage() before and after each test so order never matters, and the
small state machine means "every pair of (start_state, operation)" fits in
a handful of functions — much cheaper than debugging in a live demo. I
deliberately did not build persistence, printing, history logs, role checks,
argparse subcommands, or async in workflow.py, because none of those are
needed for checkpoints B1–B6, and saying "not yet" out loud keeps my diff
small and my review fast. Open questions I left for later — whether
reject_request should require a reason, whether we want an audit log, and
whether approved_by should be validated against a known list — are recorded
so they aren't lost, but they are explicitly out of scope for this milestone.
