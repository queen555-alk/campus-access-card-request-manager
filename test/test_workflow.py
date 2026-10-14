"""Tests for Engineer B's workflow module.

Assumes storage has a reset/in-memory mode for test isolation.
If your storage module exposes a different reset hook, adapt `setup_function`.
"""

import pytest

from storage import reset_storage, add_request, get_request
from workflow import (
    WorkflowError,
    approve_request,
    issue_card,
    return_card,
    reject_request,
)


@pytest.fixture(autouse=True)
def clean():
    reset_storage()
    yield
    reset_storage()


def _new_request(holder="Ada"):
    return add_request(holder=holder)


# --- approve_request --------------------------------------------------------

def test_approve_happy_path():
    r = _new_request()
    out = approve_request(r["id"], "Boss")
    assert out["status"] == "approved"
    assert out["approved_by"] == "Boss"


def test_approve_rejects_blank_approver():
    r = _new_request()
    with pytest.raises(WorkflowError):
        approve_request(r["id"], "   ")
    # Record unchanged
    assert get_request(r["id"])["status"] == "requested"


def test_approve_rejects_none_approver():
    r = _new_request()
    with pytest.raises(WorkflowError):
        approve_request(r["id"], None)
    assert get_request(r["id"])["status"] == "requested"


def test_approve_unknown_id():
    with pytest.raises(WorkflowError):
        approve_request("nope", "Boss")


def test_approve_twice_is_illegal():
    r = _new_request()
    approve_request(r["id"], "Boss")
    with pytest.raises(WorkflowError):
        approve_request(r["id"], "Boss")


# --- issue_card -------------------------------------------------------------

def test_issue_happy_path():
    r = _new_request()
    approve_request(r["id"], "Boss")
    out = issue_card(r["id"])
    assert out["status"] == "issued"


def test_issue_from_requested_is_illegal():
    r = _new_request()
    with pytest.raises(WorkflowError):
        issue_card(r["id"])
    assert get_request(r["id"])["status"] == "requested"


def test_issue_from_returned_is_illegal():
    r = _new_request()
    approve_request(r["id"], "Boss")
    issue_card(r["id"])
    return_card(r["id"])
    with pytest.raises(WorkflowError):
        issue_card(r["id"])


# --- return_card ------------------------------------------------------------

def test_return_happy_path():
    r = _new_request()
    approve_request(r["id"], "Boss")
    issue_card(r["id"])
    out = return_card(r["id"])
    assert out["status"] == "returned"


def test_return_twice_is_illegal():
    r = _new_request()
    approve_request(r["id"], "Boss")
    issue_card(r["id"])
    return_card(r["id"])
    with pytest.raises(WorkflowError):
        return_card(r["id"])


def test_return_from_approved_is_illegal():
    r = _new_request()
    approve_request(r["id"], "Boss")
    with pytest.raises(WorkflowError):
        return_card(r["id"])
    assert get_request(r["id"])["status"] == "approved"


# --- reject_request ---------------------------------------------------------

def test_reject_from_requested():
    r = _new_request()
    out = reject_request(r["id"], "duplicate")
    assert out["status"] == "rejected"


def test_reject_from_approved():
    r = _new_request()
    approve_request(r["id"], "Boss")
    out = reject_request(r["id"], "policy")
    assert out["status"] == "rejected"


def test_reject_returned_is_illegal():
    r = _new_request()
    approve_request(r["id"], "Boss")
    issue_card(r["id"])
    return_card(r["id"])
    with pytest.raises(WorkflowError):
        reject_request(r["id"])
    assert get_request(r["id"])["status"] == "returned"


def test_reject_twice_is_illegal():
    r = _new_request()
    reject_request(r["id"])
    with pytest.raises(WorkflowError):
        reject_request(r["id"])


# --- failure atomicity ------------------------------------------------------

def test_failed_transition_leaves_record_untouched():
    r = _new_request()
    snapshot = dict(get_request(r["id"]))
    with pytest.raises(WorkflowError):
        issue_card(r["id"])  # illegal from 'requested'
    assert get_request(r["id"]) == snapshot