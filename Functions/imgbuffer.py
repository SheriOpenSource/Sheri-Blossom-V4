import io
from io import BytesIO

from pil import Image


def render_image(bg):
    buffer = BytesIO()

    bg = Image.open(bg).convert("RGBA")
    x = bg.size[0]
    y = bg.size[1]
    bg.save(io.BytesIO(), format="PNG")
    im = Image.new("RGBA", (x, y), (0, 0, 0, 0))
    im.paste(bg, (0, 0), bg)
    im.save(buffer, format="png")
    buffer.seek(0)

    return buffer
