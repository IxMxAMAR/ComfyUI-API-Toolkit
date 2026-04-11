"""Tests for shared.conversions module."""

import base64
import io

import numpy as np
import pytest
import torch
from PIL import Image

from shared.conversions import (
    tensor_to_pil,
    pil_to_tensor,
    tensor_to_base64,
    tensor_to_jpeg_bytes,
    bytes_to_tensor,
)


def _make_test_tensor(h=64, w=64):
    """Create a random test image tensor [1, H, W, 3]."""
    return torch.rand(1, h, w, 3, dtype=torch.float32)


class TestTensorToPil:
    def test_basic_conversion(self):
        t = _make_test_tensor()
        img = tensor_to_pil(t)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size == (64, 64)

    def test_takes_first_from_batch(self):
        t = torch.rand(3, 32, 32, 3)
        img = tensor_to_pil(t)
        assert img.size == (32, 32)


class TestPilToTensor:
    def test_basic_conversion(self):
        img = Image.new("RGB", (48, 48), color=(128, 64, 32))
        t = pil_to_tensor(img)
        assert t.shape == (1, 48, 48, 3)
        assert t.dtype == torch.float32
        assert t.min() >= 0.0
        assert t.max() <= 1.0

    def test_rgba_converted_to_rgb(self):
        img = Image.new("RGBA", (16, 16), color=(255, 0, 0, 128))
        t = pil_to_tensor(img)
        assert t.shape == (1, 16, 16, 3)


class TestTensorRoundtrip:
    def test_roundtrip_preserves_shape(self):
        original = _make_test_tensor(50, 70)
        img = tensor_to_pil(original)
        restored = pil_to_tensor(img)
        assert restored.shape == (1, 50, 70, 3)

    def test_roundtrip_values_close(self):
        original = _make_test_tensor(32, 32)
        img = tensor_to_pil(original)
        restored = pil_to_tensor(img)
        # uint8 quantization means max error of 1/255
        assert torch.allclose(original, restored, atol=1.0 / 255 + 1e-6)


class TestTensorToBase64:
    def test_returns_none_for_none(self):
        assert tensor_to_base64(None) is None

    def test_returns_valid_base64(self):
        t = _make_test_tensor()
        b64 = tensor_to_base64(t, fmt="PNG")
        assert isinstance(b64, str)
        # Verify it decodes to valid PNG
        decoded = base64.b64decode(b64)
        img = Image.open(io.BytesIO(decoded))
        assert img.format == "PNG"

    def test_jpeg_format(self):
        t = _make_test_tensor()
        b64 = tensor_to_base64(t, fmt="JPEG")
        decoded = base64.b64decode(b64)
        img = Image.open(io.BytesIO(decoded))
        assert img.format == "JPEG"


class TestTensorToJpegBytes:
    def test_returns_jpeg_bytes(self):
        t = _make_test_tensor()
        data = tensor_to_jpeg_bytes(t, quality=85)
        assert isinstance(data, bytes)
        img = Image.open(io.BytesIO(data))
        assert img.format == "JPEG"


class TestBytesToTensor:
    def test_from_png(self):
        img = Image.new("RGB", (40, 30), color=(100, 200, 50))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        t = bytes_to_tensor(buf.getvalue())
        assert t.shape == (1, 30, 40, 3)

    def test_from_jpeg(self):
        img = Image.new("RGB", (20, 20), color=(50, 100, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        t = bytes_to_tensor(buf.getvalue())
        assert t.shape == (1, 20, 20, 3)
