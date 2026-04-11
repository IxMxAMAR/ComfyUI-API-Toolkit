"""Validation tests for Kling AI nodes."""

import pytest
from services.kling.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


EXPECTED_NODE_COUNT = 32
CATEGORY_PREFIX = "API Toolkit/Kling AI"

# Auth node that should have password: True on key inputs
AUTH_NODE_NAMES = ["AIS_Kling_Auth"]

# Config/selector nodes that do NOT call external APIs
CONFIG_NODE_NAMES = {
    "AIS_Kling_Auth",
    "AIS_Kling_VideoLoader",
    "AIS_Kling_RawFileLoader",
    "AIS_Kling_RawFileSaver",
    "AIS_Kling_ElementSelector",
    "AIS_Kling_CameraControl",
    "AIS_Kling_VoiceSelector",
    "AIS_Kling_FastVideoSaver",
}


class TestKlingNodeCount:
    def test_expected_count(self):
        assert len(NODE_CLASS_MAPPINGS) == EXPECTED_NODE_COUNT


class TestKlingNodeAttributes:
    """Every Kling node must have required ComfyUI attributes."""

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


class TestKlingAuthPassword:
    """Auth nodes must use password: True for key inputs."""

    @pytest.fixture(params=AUTH_NODE_NAMES)
    def auth_cls(self, request):
        return NODE_CLASS_MAPPINGS[request.param]

    def test_access_key_password(self, auth_cls):
        inputs = auth_cls.INPUT_TYPES()
        required = inputs.get("required", {})
        assert "access_key" in required, "Auth node missing access_key input"
        config = required["access_key"]
        # config is ("STRING", {opts})
        opts = config[1] if isinstance(config, (list, tuple)) else {}
        assert opts.get("password") is True, "access_key must have password: True"

    def test_secret_key_password(self, auth_cls):
        inputs = auth_cls.INPUT_TYPES()
        required = inputs.get("required", {})
        assert "secret_key" in required, "Auth node missing secret_key input"
        config = required["secret_key"]
        opts = config[1] if isinstance(config, (list, tuple)) else {}
        assert opts.get("password") is True, "secret_key must have password: True"


class TestKlingISChanged:
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
