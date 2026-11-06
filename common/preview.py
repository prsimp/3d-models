"""Render a part to a PNG preview, for its README and pull requests.

A small software renderer: it shades the part's faces from orthographic
isometric views and outlines each face, so the image needs nothing beyond
numpy and Pillow, and comes out the same on every machine.
"""

from pathlib import Path

import numpy as np
from build123d import Shape
from PIL import Image

# Views as (azimuth, elevation) in degrees. Azimuth 0 looks along +Y, from
# the front; positive azimuths swing the camera round to the right.
VIEWS = ((-35, 25), (145, 25))
SIZE = 600  # pixels, each view square
SUPERSAMPLE = 3  # rendered this many times larger, then scaled down
MARGIN = 0.06  # of the view's width

BACKGROUND = (255, 255, 255)
COLOUR = np.array((150, 175, 205), dtype=float)  # light steel blue
OUTLINE = (40, 45, 55)
AMBIENT = 0.45
LIGHT = np.array((-0.4, -0.5, 0.75))  # roughly over the viewer's left shoulder


def preview(part: Shape, source: str, views=VIEWS) -> None:
    """Write views of part side by side to preview.png beside the model.

    source is the model script's __file__.
    """
    triangles, face_ids = _triangles(part)
    images = [_render(triangles, face_ids, *view) for view in views]
    sheet = Image.new("RGB", (SIZE * len(images), SIZE), BACKGROUND)
    for i, image in enumerate(images):
        sheet.paste(image, (i * SIZE, 0))
    sheet.save(Path(source).resolve().parent / "preview.png", optimize=True)


def _triangles(part: Shape) -> tuple[np.ndarray, np.ndarray]:
    """Every face's triangles, as an (n, 3, 3) array, and each one's face."""
    triangles, face_ids = [], []
    for face_id, face in enumerate(part.faces()):
        vertices, indices = face.tessellate(0.05, 0.2)
        points = np.array([tuple(v) for v in vertices])
        for index in indices:
            triangles.append(points[list(index)])
            face_ids.append(face_id)
    return np.array(triangles), np.array(face_ids)


def _camera(azimuth: float, elevation: float) -> np.ndarray:
    """Rows: the screen's right, up and depth (away from the viewer)."""
    a, e = np.radians(azimuth), np.radians(elevation)
    forward = np.array((np.sin(a) * np.cos(e), np.cos(a) * np.cos(e), -np.sin(e)))
    right = np.cross(forward, (0, 0, 1))
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    return np.array((right, up, forward))


def _render(
    triangles: np.ndarray, face_ids: np.ndarray, azimuth: float, elevation: float
) -> Image.Image:
    camera = _camera(azimuth, elevation)
    size = SIZE * SUPERSAMPLE
    view = triangles @ camera.T  # (n, 3, [right, up, depth])

    # Fit the part in the view, centred.
    flat = view.reshape(-1, 3)
    low, high = flat.min(axis=0), flat.max(axis=0)
    scale = size * (1 - 2 * MARGIN) / max(high[0] - low[0], high[1] - low[1])
    centre = (low + high) / 2
    x = (view[:, :, 0] - centre[0]) * scale + size / 2
    y = size / 2 - (view[:, :, 1] - centre[1]) * scale
    depth = view[:, :, 2]

    # Lambert shading, lit from either side so face orientation cannot matter.
    normals = np.cross(
        triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
    )
    normals /= np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    light = camera.T @ (LIGHT / np.linalg.norm(LIGHT))
    shade = AMBIENT + (1 - AMBIENT) * np.abs(normals @ light)

    depth_buffer = np.full((size, size), np.inf)
    shade_buffer = np.zeros((size, size))
    face_buffer = np.full((size, size), -1)
    for i in range(len(triangles)):
        _fill(
            x[i], y[i], depth[i], shade[i], face_ids[i],
            depth_buffer, shade_buffer, face_buffer,
        )  # fmt: skip

    covered = face_buffer >= 0
    pixels = np.empty((size, size, 3))
    pixels[:] = BACKGROUND
    pixels[covered] = COLOUR * shade_buffer[covered, None]

    # Outline every face: wherever a pixel's face differs from a neighbour's.
    edges = np.zeros((size, size), dtype=bool)
    for axis in (0, 1):
        change = np.diff(face_buffer, axis=axis) != 0
        if axis == 0:
            edges[1:] |= change
            edges[:-1] |= change
        else:
            edges[:, 1:] |= change
            edges[:, :-1] |= change
    pixels[edges] = OUTLINE

    image = Image.fromarray(pixels.astype(np.uint8))
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def _fill(xs, ys, zs, shade, face_id, depth_buffer, shade_buffer, face_buffer):
    """Rasterise one triangle into the buffers, nearest surface winning."""
    size = depth_buffer.shape[0]
    x0, x1 = max(int(xs.min()), 0), min(int(np.ceil(xs.max())), size - 1)
    y0, y1 = max(int(ys.min()), 0), min(int(np.ceil(ys.max())), size - 1)
    if x1 < x0 or y1 < y0:
        return
    (ax, bx, cx), (ay, by, cy) = xs, ys
    area = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(area) < 1e-12:
        return
    px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / area
    w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / area
    w2 = 1 - w0 - w1
    inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
    window = (slice(y0, y1 + 1), slice(x0, x1 + 1))
    nearer = inside & (z < depth_buffer[window])
    depth_buffer[window][nearer] = z[nearer]
    shade_buffer[window][nearer] = shade
    face_buffer[window][nearer] = face_id
