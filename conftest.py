"""Pytest configuration -- add project root to sys.path so tests can import shared.*"""

import sys
import os

# Add project root to path so `from shared import ...` works in tests
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

collect_ignore_glob = ["__init__.py", "services/*"]
