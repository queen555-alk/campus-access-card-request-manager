"""Entry point for the Campus Access CLI.

Keeps startup trivial: initialize storage (if needed), then hand control
to the menu loop in cli.py. All user-facing behavior lives in cli.py.
"""

import sys

from cli import run_menu


def main():
    try:
        run_menu()
    except SystemExit:
        # cli.run_menu() raises SystemExit(0) on Quit / Ctrl-C.
        raise
    except KeyboardInterrupt:
        # Extra safety net in case Ctrl-C escapes the menu loop.
        print("\n[interrupted]")
        sys.exit(130)


if __name__ == "__main__":
    main()