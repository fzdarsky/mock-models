import math

from mocklm.colors import nearest_color, rgb_to_hex
from mocklm.models import Message, extract_images
from mocklm.modes.base import Mode


def _grid_colors(image, grid_size: int = 3) -> list[tuple[int, int, int]]:
    img = image.convert("RGB")
    w, h = img.size
    colors = []
    for row in range(grid_size):
        for col in range(grid_size):
            x0 = col * w // grid_size
            y0 = row * h // grid_size
            x1 = (col + 1) * w // grid_size
            y1 = (row + 1) * h // grid_size
            region = img.crop((x0, y0, x1, y1))
            pixels = list(region.get_flattened_data())
            n = len(pixels)
            if n == 0:
                colors.append((0, 0, 0))
                continue
            avg_r = sum(p[0] for p in pixels) // n
            avg_g = sum(p[1] for p in pixels) // n
            avg_b = sum(p[2] for p in pixels) // n
            colors.append((avg_r, avg_g, avg_b))
    return colors


def _select_distinct(colors: list[tuple[int, int, int]], count: int) -> list[tuple[int, int, int]]:
    if not colors:
        return []
    selected = [colors[0]]
    remaining = list(colors[1:])
    while len(selected) < count and remaining:
        best_idx = 0
        best_min_dist = -1.0
        for i, c in enumerate(remaining):
            min_dist = min(
                math.sqrt((c[0] - s[0]) ** 2 + (c[1] - s[1]) ** 2 + (c[2] - s[2]) ** 2)
                for s in selected
            )
            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_idx = i
        selected.append(remaining.pop(best_idx))
    return selected


def _orientation(w: int, h: int) -> str:
    if w > h:
        return "landscape"
    if h > w:
        return "portrait"
    return "square"


class DescribeMode(Mode):
    def generate(self, messages: list[Message]) -> str:
        images = extract_images(messages)
        if not images:
            return "No image provided."

        img = images[0]
        if img.is_url_ref:
            return "URL image (not fetched)."

        w, h = img.width, img.height
        fmt = img.format
        orient = _orientation(w, h)

        grid = _grid_colors(img.image)
        top3 = _select_distinct(grid, 3)

        color_parts = []
        for r, g, b in top3:
            name, named_rgb = nearest_color(r, g, b)
            hex_val = rgb_to_hex(*named_rgb)
            color_parts.append(f"{name} ({hex_val})")

        if len(color_parts) > 1:
            colors_str = ", ".join(color_parts[:-1]) + ", and " + color_parts[-1]
        elif color_parts:
            colors_str = color_parts[0]
        else:
            colors_str = ""

        return (
            f"This is a {w}x{h} {fmt} image in {orient} orientation. "
            f"The dominant colors are {colors_str}."
        )
