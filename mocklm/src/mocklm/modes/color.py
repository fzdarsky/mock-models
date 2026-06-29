from mocklm.colors import average_color, nearest_color
from mocklm.models import Message, extract_images
from mocklm.modes.base import Mode


class ColorMode(Mode):
    def generate(self, messages: list[Message]) -> str:
        images = extract_images(messages)
        if not images:
            return "No image provided."

        img = images[0]
        if img.is_url_ref:
            return "URL image (not fetched)."

        avg_r, avg_g, avg_b = average_color(img.image.convert("RGB"))
        name, (cr, cg, cb) = nearest_color(avg_r, avg_g, avg_b)
        return f"The dominant color in this image is '{name}' (RGB: {cr}, {cg}, {cb})."
