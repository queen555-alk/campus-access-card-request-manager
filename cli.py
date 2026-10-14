"""Interactive menu for the campus access app.

Engineer B owns this file. The menu must never crash on bad input —
errors are caught, printed, and the loop continues.
"""

from storage import add_request, list_requests
from workflow import (
    WorkflowError,
    approve_request,
    issue_card,
    return_card,
    reject_request,
)


MENU = """
=== Campus Access ===
1) Create request
2) List requests
3) Approve request
4) Issue card
5) Return card
6) Reject request
0) Quit
"""


def _prompt(label):
    """Read a line, stripped. Never raises."""
    try:
        return input(label).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[bye]")
        raise SystemExit(0)


def _print_request(req):
    if not req:
        print("  (no such request)")
        return
    print(
        f"  id={req.get('id')}  status={req.get('status')}  "
        f"holder={req.get('holder', '?')}  approved_by={req.get('approved_by') or '-'}"
    )


def run_menu():
    """Loop: show options, read input, call functions, catch errors."""
    while True:
        print(MENU)
        choice = _prompt("Choose: ")

        try:
            if choice == "0":
                print("Bye.")
                return

            elif choice == "1":
                holder = _prompt("Holder name: ")
                if not holder:
                    print("! Holder name cannot be blank.")
                    continue
                req = add_request(holder=holder)
                print("Created:")
                _print_request(req)

            elif choice == "2":
                rows = list_requests()
                if not rows:
                    print("  (no requests)")
                for r in rows:
                    _print_request(r)

            elif choice == "3":
                rid = _prompt("Request id: ")
                approver = _prompt("Approved by: ")
                _print_request(approve_request(rid, approver))

            elif choice == "4":
                rid = _prompt("Request id: ")
                _print_request(issue_card(rid))

            elif choice == "5":
                rid = _prompt("Request id: ")
                _print_request(return_card(rid))

            elif choice == "6":
                rid = _prompt("Request id: ")
                reason = _prompt("Reason (optional): ")
                _print_request(reject_request(rid, reason))

            else:
                print(f"! Unknown option: {choice!r}")

        except WorkflowError as e:
            # Illegal transition — record was NOT changed. Retry the menu.
            print(f"! {e}")
        except Exception as e:  # last-resort safety net
            print(f"! Unexpected error: {e}")