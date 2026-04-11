"""Tests for services/__init__.py auto-discovery."""

import pytest
from services import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


class TestAutoDiscovery:
    """Validate that auto-discovery loads all services without errors."""

    def test_import_succeeds(self):
        """services/__init__.py should import without crashing."""
        assert NODE_CLASS_MAPPINGS is not None
        assert NODE_DISPLAY_NAME_MAPPINGS is not None

    def test_class_mappings_is_dict(self):
        assert isinstance(NODE_CLASS_MAPPINGS, dict)

    def test_display_name_mappings_is_dict(self):
        assert isinstance(NODE_DISPLAY_NAME_MAPPINGS, dict)

    def test_not_empty(self):
        """At least some nodes should be registered."""
        assert len(NODE_CLASS_MAPPINGS) > 0

    def test_no_duplicate_node_names(self):
        """Every key in NODE_CLASS_MAPPINGS should be unique (dicts enforce this,
        but verify none were silently overwritten from different services)."""
        # Collect keys from each service individually
        from services.kling.nodes import NODE_CLASS_MAPPINGS as kling_map
        from services.elevenlabs.nodes import NODE_CLASS_MAPPINGS as el_map
        from services.gemini.nodes import NODE_CLASS_MAPPINGS as gemini_map

        all_keys = list(kling_map.keys()) + list(el_map.keys()) + list(gemini_map.keys())
        assert len(all_keys) == len(set(all_keys)), "Duplicate node names found across services"

    def test_every_class_has_display_name(self):
        """Every node in CLASS_MAPPINGS must have a corresponding display name."""
        missing = [
            name for name in NODE_CLASS_MAPPINGS
            if name not in NODE_DISPLAY_NAME_MAPPINGS
        ]
        assert not missing, f"Nodes missing display names: {missing}"

    def test_total_node_count(self):
        """Combined total should match sum of all services (32 + 15 + 13 = 60)."""
        assert len(NODE_CLASS_MAPPINGS) == 60

    def test_display_names_not_empty(self):
        """Every display name should be a non-empty string."""
        for key, name in NODE_DISPLAY_NAME_MAPPINGS.items():
            assert isinstance(name, str) and len(name) > 0, (
                f"Display name for {key} is empty or not a string"
            )
