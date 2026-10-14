# AI Learning Log

## Engineer A

### Cycle 1

- **Question I asked AI:**

  How can I validate request IDs in Python using regular expressions, and how can I ensure that a request record contains all the required fields before saving it?

- **AI explanation (summary):**

  AI explained that regular expressions can be used to check whether a request ID follows a specific format. In my solution, `re.compile(r"A[0-9]{3,}")` defines the required pattern, while `fullmatch()` ensures that the entire ID matches the pattern. AI also explained that dictionaries can be validated by checking their data types, required keys, and allowed values before they are stored.

- **My prediction before testing:**

  I predicted that valid IDs such as `A001` and `A123` would pass validation, while IDs such as `B001`, `A12`, and `A001X` would raise a `ValueError`. I also expected records with missing or extra fields to fail validation.

- **My own experiment (what I ran):**

  I tested the ID validation function with different IDs and checked how the program handled valid and invalid request records.

  ```python
  import re

  ID_PATTERN = re.compile(r"A[0-9]{3,}")

  def check_id(request_id):
      if not isinstance(request_id, str) or not ID_PATTERN.fullmatch(request_id):
          raise ValueError(f"Malformed request ID: {request_id!r}")

  test_ids = ["A001", "A123", "B001", "A12", "A001X"]

  for request_id in test_ids:
      try:
          check_id(request_id)
          print(request_id, "is valid")
      except ValueError as error:
          print(error)
  ```

- **Result / verification:**

  The expected result was that `A001` and `A123` would pass, while `B001`, `A12`, and `A001X` would raise a `ValueError`. This would confirm that `fullmatch()` checks the entire string against the specified ID pattern.

- **Final decision (used, adjusted or rejected, and why):**

  I decided to use the validation approach because it helps prevent malformed request IDs and incomplete records from entering the system. I also retained the record validation function to check the required keys, card types, statuses, and approval information before storing or loading requests.

### Cycle 2

- **Question I asked AI:**

  How can I save Python request records to a JSON file safely and load them back without losing valid data if the file contains invalid records?

- **AI explanation (summary):**

  AI explained that Python's `json` module can convert dictionaries and lists into JSON data for storage. It also explained that writing to a temporary file before replacing the original file helps protect the existing saved data if writing fails before the replacement. When loading data, the program should validate all records before changing the current in-memory storage.

- **My prediction before testing:**

  I predicted that saving and loading valid requests would preserve their data. I also expected that a file containing invalid records would raise an error and that the existing in-memory requests would remain unchanged if validation failed.

- **My own experiment (what I ran):**

  I created a request, saved it to a JSON file, reset the in-memory storage, and loaded the file again. I then planned to test loading a file containing an invalid request record.

  ```python
  import json
  import os

  test_path = "test_requests.json"

  # Run these tests using the project's request-management module.
  reset()

  request = create_request("F001", "student")
  save_requests(test_path)

  reset()
  load_requests(test_path)

  print(list_requests())

  # Create an invalid file to test validation.
  with open(test_path, "w") as file:
      json.dump([{"id": "A001"}], file)

  try:
      load_requests(test_path)
  except ValueError as error:
      print("Loading failed:", error)

  os.remove(test_path)
  ```

- **Result / verification:**

  The expected result was that the valid request would be restored after loading the saved file. The invalid file should raise a `ValueError` because the record does not contain the required fields. Since the loading function validates records before clearing and replacing the existing storage, the previous in-memory requests should remain unchanged when validation fails.

- **Final decision (used, adjusted or rejected, and why):**

  I decided to use the JSON storage approach because it allows request records to persist between program runs. I retained temporary-file replacement for saving and validation-before-replacement for loading to improve data safety. I would also test file-writing failures and malformed JSON separately to verify the error-handling behaviour.
  
# Engineer B
My first AI-assisted cycle was designing the state machine for workflow.py.
I asked the AI to enumerate every legal and illegal transition for a four-state
system (requested, approved, issued, returned, plus rejected), and it
produced a clean table I could turn into test cases. What I learned is that the
AI is very good at exhaustive enumeration but bad at knowing which states are
terminal in our domain — it suggested allowing rejected → approved, which I
had to reject because a rejected request is history in this app. The lesson:
use the AI to widen the space of options, then narrow it myself with domain
judgment.

My second cycle was about error handling in cli.py. I initially wrote a menu
that let WorkflowError propagate and crash the app, and I asked the AI why
that felt wrong. It walked me through the "strict core, forgiving shell" pattern
— validate hard in the workflow layer, catch and translate at the boundary —
and I restructured run_menu to catch WorkflowError and a last-resort
Exception inside the loop. What I learned is that I was conflating two
concerns (correctness and user experience) in one place, and the AI's framing
made the split obvious. I also learned to distrust the AI's first suggestion:
it wanted to silently retry the failed operation, which I rejected because
blind retries hide problems from the user.

My third cycle was writing tests/test_workflow.py, specifically the atomicity
test. I asked the AI how to prove that a failed transition leaves the record
untouched, and it suggested snapshotting the record before the failing call and
comparing dicts afterward — simple and effective. But the AI also suggested
mocking update_request to assert it was never called, which is stronger but
couples the test to implementation details. I chose the snapshot approach
because it tests behavior, not internals. The broader lesson from this cycle is
that the AI is a fast source of options — including ones I wouldn't have
thought of — but the choice between them is mine, and it has to be driven by
what I actually want the code to guarantee.
