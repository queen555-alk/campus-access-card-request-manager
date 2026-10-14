"""Workflow module: state transitions for campus access requests.

State machine:
    requested -> approved -> issued -> returned
    requested -> rejected (terminal)
    requested -> approved -> rejected (rejected at any pre-issued stage)

Engineer B owns this file.
"""

from storage import get_request, update_request


class WorkflowError(Exception):
    """Raised when an illegal transition is attempted."""
    pass


# --- Internal helpers -------------------------------------------------------

def _load(request_id):
    """Fetch a request or raise a clear error."""
    req = get_request(request_id)
    if req is None:
        raise WorkflowError(f"No request found with id={request_id!r}")
    return req


def _require_status(req, expected):
    """Guard: fail loudly if the record is not in the expected state."""
    actual = req.get("status")
    if actual != expected:
        raise WorkflowError(
            f"Illegal transition for id={req['id']!r}: "
            f"expected status={expected!r}, got {actual!r}"
        )


# --- Public API -------------------------------------------------------------

def approve_request(request_id, approved_by):
    """requested -> approved.

    Requires a non-empty approver name. Does not mutate on failure.
    """
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise WorkflowError("approve_request: 'approved_by' must be non-empty.")

    req = _load(request_id)
    _require_status(req, "requested")

    update_request(
        request_id,
        status="approved",
        approved_by=approved_by.strip(),
    )
    return _load(request_id)


def issue_card(request_id):
    """approved -> issued.

    Only an approved request can have a card issued. A non-empty approver
    must already be recorded (defensive check).
    """
    req = _load(request_id)
    _require_status(req, "approved")

    if not req.get("approved_by"):
        raise WorkflowError(
            f"issue_card: id={request_id!r} is approved but has no approver."
        )

    update_request(request_id, status="issued")
    return _load(request_id)


def return_card(request_id):
    """issued -> returned. 'returned' is final."""
    req = _load(request_id)
    _require_status(req, "issued")

    update_request(request_id, status="returned")
    return _load(request_id)


def reject_request(request_id, reason=""):
    """Any non-terminal state -> rejected. 'returned' cannot be rejected."""
    req = _load(request_id)
    if req.get("status") in ("returned", "rejected"):
        raise WorkflowError(
            f"reject_request: id={request_id!r} is already {req['status']!r}."
        )

    update_request(request_id, status="rejected", reason=reason)
    return _load(request_id)