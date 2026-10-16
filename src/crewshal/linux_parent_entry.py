"""Finite installed parent entry for isolated Python execution."""

import os
import sys


def main() -> None:
    """Check isolated startup before importing the inventoried application."""
    # CPython can add this locale after an empty-environment exec.
    if os.environ:
        if (
            sys.platform != "linux"
            or not sys.flags.isolated
            or not sys.flags.no_site
            or not sys.flags.dont_write_bytecode
            or dict(os.environ) != {"LC_CTYPE": "C.UTF-8"}
        ):
            raise ValueError("The isolated entry inherited an environment.")
        with open("/proc/self/environ", "rb") as inherited:
            if inherited.read(1):
                raise ValueError("The isolated entry inherited an environment.")
        del os.environ["LC_CTYPE"]
    if (
        sys.platform != "linux"
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or os.environ
        or len(sys.argv) != 1
        or sys.argv[0] != "/opt/crewshal/lib/crewshal/linux_parent_entry.py"
    ):
        raise ValueError("installed parent requires exact isolated credential-free startup")
    # The qualified copied root supplies this exact readonly installed directory.
    sys.path.insert(0, "/opt/crewshal/lib")
    from crewshal.linux_parent import run_installed_namespace_parent

    run_installed_namespace_parent(cancelled=lambda: False)


if __name__ == "__main__":
    main()
