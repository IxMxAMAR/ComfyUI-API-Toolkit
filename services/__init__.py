"""
Auto-discovery scanner for API Toolkit services.

Imports each service subfolder, merges NODE_CLASS_MAPPINGS, and gracefully
handles missing dependencies with clear console messages.
"""

import importlib
import os
import sys

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_SERVICE_DIRS = ["kling", "elevenlabs", "gemini"]
_PACKAGE = __name__  # "services" when loaded as part of ComfyUI-AI-Suite

# Use ASCII-safe markers that work on all console encodings (including cp1252 on Windows)
_CHECK = "[OK]"
_CROSS = "[!!]"


def _safe_print(msg: str):
    """Print with fallback for encoding issues on Windows consoles."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def _discover_services():
    total = 0
    loaded = []
    failed = []

    for service_name in _SERVICE_DIRS:
        try:
            mod = importlib.import_module(f".{service_name}", package=_PACKAGE)
        except ImportError as exc:
            _safe_print(f"[API Toolkit] {_CROSS} {service_name} disabled -- missing dependency: {exc}")
            failed.append(service_name)
            continue
        except Exception as exc:
            _safe_print(f"[API Toolkit] {_CROSS} {service_name} disabled -- error: {exc}")
            failed.append(service_name)
            continue

        svc_classes = getattr(mod, "NODE_CLASS_MAPPINGS", {})
        svc_names = getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})

        count = len(svc_classes)
        NODE_CLASS_MAPPINGS.update(svc_classes)
        NODE_DISPLAY_NAME_MAPPINGS.update(svc_names)
        total += count

        _safe_print(f"[API Toolkit] {_CHECK} {service_name} loaded ({count} nodes)")
        loaded.append(service_name)

    _safe_print(f"[API Toolkit] Ready -- {total} nodes registered")


_discover_services()
