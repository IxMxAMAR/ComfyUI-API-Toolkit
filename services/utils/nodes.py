"""Utility nodes — image processing helpers useful alongside API generation."""

import json
import logging
from typing import Optional

import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Palette snapping (with optional cKDTree acceleration)
# ---------------------------------------------------------------------------

try:
    from scipy.spatial import cKDTree
    _HAVE_KDTREE = True
except ImportError:
    _HAVE_KDTREE = False


def _build_palette(small_img: Image.Image, max_colors: int) -> np.ndarray:
    """Quantize a PIL image and return its unique palette as [P, 3] float32."""
    quantized = small_img.quantize(colors=max_colors, method=Image.Quantize.FASTOCTREE)
    restored = quantized.convert("RGB")
    palette_raw = np.array(restored).reshape(-1, 3).astype(np.float32)
    return np.unique(palette_raw, axis=0)


def _snap_to_palette(frame_pixels: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Snap each pixel to the nearest palette color.

    frame_pixels: [H, W, 3] uint8
    palette:      [P, 3] float32
    Returns:      [H, W, 3] uint8
    """
    sh, sw = frame_pixels.shape[:2]
    flat = frame_pixels.reshape(-1, 3).astype(np.float32)

    if _HAVE_KDTREE and palette.shape[0] > 16:
        # KDTree is faster for large palettes
        tree = cKDTree(palette)
        _, nearest_idx = tree.query(flat, k=1)
    else:
        # Einsum vectorized distance — faster than np.sum for small palettes
        diff = flat[:, np.newaxis, :] - palette[np.newaxis, :, :]
        dist = np.einsum("ijk,ijk->ij", diff, diff)
        nearest_idx = np.argmin(dist, axis=1)

    snapped = palette[nearest_idx].astype(np.uint8)
    return snapped.reshape(sh, sw, 3)


def _floyd_steinberg_dither(image_np: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Apply Floyd-Steinberg dithering against a fixed palette.

    image_np: [H, W, 3] uint8
    palette:  [P, 3] float32
    Returns:  [H, W, 3] uint8
    """
    h, w = image_np.shape[:2]
    out = image_np.astype(np.float32).copy()

    for y in range(h):
        for x in range(w):
            old = out[y, x].copy()
            # Find nearest palette color
            diff = palette - old[np.newaxis, :]
            idx = np.argmin(np.einsum("ij,ij->i", diff, diff))
            new = palette[idx]
            out[y, x] = new
            err = old - new
            if x + 1 < w:
                out[y, x + 1] += err * (7 / 16)
            if y + 1 < h:
                if x > 0:
                    out[y + 1, x - 1] += err * (3 / 16)
                out[y + 1, x] += err * (5 / 16)
                if x + 1 < w:
                    out[y + 1, x + 1] += err * (1 / 16)

    return np.clip(out, 0, 255).astype(np.uint8)


def _rgb_to_hex(palette: np.ndarray) -> list:
    """Convert [P, 3] palette to list of #RRGGBB hex codes."""
    out = []
    for row in palette.astype(np.uint8):
        out.append("#{:02X}{:02X}{:02X}".format(int(row[0]), int(row[1]), int(row[2])))
    return out


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

class AIS_Utils_PixelArtResize:
    """Convert an image (or batch) into pixel art.

    Downscales using nearest-neighbor (creating chunky pixels), optionally
    quantizes to a fixed color palette for frame-to-frame consistency, optionally
    applies Floyd-Steinberg dithering, then upscales back with nearest-neighbor.

    Great for post-processing AI-generated pixel art to lock colors across a
    batch, or for turning any photo into a retro sprite look.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Source image or batch to pixelate.",
                }),
                "downscale_factor": ("INT", {
                    "default": 8, "min": 1, "max": 64,
                    "tooltip": "How much to shrink. 8 = each output pixel represents an 8x8 block of the original.",
                }),
                "upscale_factor": ("INT", {
                    "default": 8, "min": 1, "max": 64,
                    "tooltip": "How much to scale back up. Same as downscale = output matches original size but pixelated. Set to 1 for raw pixelated output.",
                }),
                "palette_mode": (["none", "shared_batch", "per_frame"], {
                    "default": "shared_batch",
                    "tooltip": "none = no color quantization. shared_batch = palette from frame 0 applied to all (best for animations, prevents color shimmer). per_frame = each frame gets its own palette.",
                }),
                "max_palette_size": ("INT", {
                    "default": 32, "min": 2, "max": 256,
                    "tooltip": "Max distinct colors in palette. 16-32 for classic SNES look, 64+ for richer art.",
                }),
            },
            "optional": {
                "dithering": (["none", "floyd_steinberg"], {
                    "default": "none",
                    "tooltip": "Floyd-Steinberg adds error diffusion for smoother color gradients at small palette sizes. Slower but prettier.",
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("image", "small_image", "palette_json")
    FUNCTION = "execute"
    CATEGORY = "API Toolkit/Utils/Image"

    def execute(
        self,
        image: torch.Tensor,
        downscale_factor: int,
        upscale_factor: int,
        palette_mode: str,
        max_palette_size: int,
        dithering: str = "none",
    ):
        # Convert to uint8 numpy
        image_np = (image.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)

        batch, h, w = image_np.shape[:3]
        small_w = max(1, w // downscale_factor)
        small_h = max(1, h // downscale_factor)
        target_w = small_w * upscale_factor
        target_h = small_h * upscale_factor

        if small_w * downscale_factor != w or small_h * downscale_factor != h:
            logger.info(
                f"[PixelArtResize] Input {w}x{h} not evenly divisible by {downscale_factor}; "
                f"using {small_w}x{small_h} small / {target_w}x{target_h} final."
            )

        # Build shared palette once (from frame 0) when shared_batch
        shared_palette: Optional[np.ndarray] = None
        if palette_mode == "shared_batch":
            first_img = Image.fromarray(image_np[0])
            first_small = first_img.resize((small_w, small_h), Image.NEAREST)
            shared_palette = _build_palette(first_small, max_palette_size)

        small_frames = []
        final_frames = []

        for i in range(batch):
            frame = image_np[i]
            img = Image.fromarray(frame)
            small = img.resize((small_w, small_h), Image.NEAREST)
            small_np = np.array(small)

            # Choose the palette to snap against (if any)
            palette_to_use: Optional[np.ndarray] = None
            if palette_mode == "shared_batch":
                palette_to_use = shared_palette
            elif palette_mode == "per_frame":
                palette_to_use = _build_palette(small, max_palette_size)

            if palette_to_use is not None and palette_to_use.shape[0] > 0:
                if dithering == "floyd_steinberg":
                    small_np = _floyd_steinberg_dither(small_np, palette_to_use)
                else:
                    small_np = _snap_to_palette(small_np, palette_to_use)

            small_frames.append(small_np)
            # Upscale
            result_img = Image.fromarray(small_np).resize(
                (target_w, target_h), Image.NEAREST
            )
            final_frames.append(np.array(result_img))

        # Stack and convert back to torch
        final_stack = np.stack(final_frames, axis=0).astype(np.float32) / 255.0
        small_stack = np.stack(small_frames, axis=0).astype(np.float32) / 255.0

        # Palette JSON (first frame's palette or shared)
        palette_for_output = shared_palette
        if palette_for_output is None and palette_mode == "per_frame":
            # Report the palette from the last frame
            first_small = Image.fromarray(image_np[0]).resize((small_w, small_h), Image.NEAREST)
            palette_for_output = _build_palette(first_small, max_palette_size)

        if palette_for_output is not None:
            palette_json = json.dumps({
                "size": int(palette_for_output.shape[0]),
                "colors": _rgb_to_hex(palette_for_output),
            })
        else:
            palette_json = json.dumps({"size": 0, "colors": []})

        return (
            torch.from_numpy(final_stack),
            torch.from_numpy(small_stack),
            palette_json,
        )


NODE_CLASS_MAPPINGS = {
    "AIS_Utils_PixelArtResize": AIS_Utils_PixelArtResize,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AIS_Utils_PixelArtResize": "Pixel Art Resize",
}
