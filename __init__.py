"""ComfyUI-AI-Suite: Kling AI, ElevenLabs, and Google Gemini nodes for ComfyUI."""

# Only import services when loaded as a ComfyUI custom node package
# (i.e., when this package has a parent, meaning it's inside custom_nodes/)
try:
    from .services import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError:
    # Running standalone (e.g., during testing) -- provide empty mappings
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
