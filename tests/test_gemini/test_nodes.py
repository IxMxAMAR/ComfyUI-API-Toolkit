"""Validation tests for Gemini nodes."""

import pytest
from services.gemini.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


EXPECTED_NODE_COUNT = 13
CATEGORY_PREFIX = "API Toolkit/Gemini"

# Auth node
AUTH_NODE_NAMES = ["AIS_Gemini_APIKey"]

# Config/selector nodes that do NOT call external APIs
CONFIG_NODE_NAMES = {
    "AIS_Gemini_APIKey",
    "AIS_Gemini_ModelSelector",
    "AIS_Gemini_SafetySettings",
    "AIS_Gemini_ThinkingConfig",
}


class TestGeminiNodeCount:
    def test_expected_count(self):
        assert len(NODE_CLASS_MAPPINGS) == EXPECTED_NODE_COUNT


class TestGeminiNodeAttributes:
    """Every Gemini node must have required ComfyUI attributes."""

    @pytest.fixture(params=list(NODE_CLASS_MAPPINGS.items()), ids=lambda x: x[0])
    def node_entry(self, request):
        return request.param

    def test_has_input_types_classmethod(self, node_entry):
        name, cls = node_entry
        assert hasattr(cls, "INPUT_TYPES"), f"{name} missing INPUT_TYPES"
        assert callable(getattr(cls, "INPUT_TYPES")), f"{name}.INPUT_TYPES not callable"

    def test_has_return_types(self, node_entry):
        name, cls = node_entry
        assert hasattr(cls, "RETURN_TYPES"), f"{name} missing RETURN_TYPES"

    def test_has_function(self, node_entry):
        name, cls = node_entry
        assert hasattr(cls, "FUNCTION"), f"{name} missing FUNCTION"

    def test_has_category(self, node_entry):
        name, cls = node_entry
        assert hasattr(cls, "CATEGORY"), f"{name} missing CATEGORY"

    def test_function_method_exists(self, node_entry):
        """The method named by FUNCTION must exist on the class."""
        name, cls = node_entry
        func_name = cls.FUNCTION
        assert hasattr(cls, func_name), (
            f"{name}.FUNCTION = '{func_name}' but method does not exist"
        )

    def test_category_prefix(self, node_entry):
        name, cls = node_entry
        assert cls.CATEGORY.startswith(CATEGORY_PREFIX), (
            f"{name}.CATEGORY = '{cls.CATEGORY}' does not start with '{CATEGORY_PREFIX}'"
        )


class TestGeminiAuthPassword:
    """Auth nodes must use password: True for api_key input."""

    @pytest.fixture(params=AUTH_NODE_NAMES)
    def auth_cls(self, request):
        return NODE_CLASS_MAPPINGS[request.param]

    def test_api_key_password(self, auth_cls):
        inputs = auth_cls.INPUT_TYPES()
        required = inputs.get("required", {})
        assert "api_key" in required, "Auth node missing api_key input"
        config = required["api_key"]
        opts = config[1] if isinstance(config, (list, tuple)) else {}
        assert opts.get("password") is True, "api_key must have password: True"


class TestGeminiISChanged:
    """Generative nodes (those calling APIs) should have IS_CHANGED."""

    @pytest.fixture(
        params=[
            (name, cls) for name, cls in NODE_CLASS_MAPPINGS.items()
            if name not in CONFIG_NODE_NAMES
        ],
        ids=lambda x: x[0],
    )
    def generative_node(self, request):
        return request.param

    def test_has_is_changed(self, generative_node):
        name, cls = generative_node
        assert hasattr(cls, "IS_CHANGED"), (
            f"Generative node {name} should have IS_CHANGED method"
        )
