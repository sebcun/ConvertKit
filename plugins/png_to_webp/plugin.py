# TITLE: PNG to WEBP
# AUTHOR: @sebastian

from PIL import Image

title = "PNG to WEBP"
input_format = "png"
output_format = "webp"


def convert(file_path):
    img = Image.open(file_path)
    new_path = file_path.replace(".png", "_converted.webp")
    img.save(new_path, "WEBP", quality=85)
    return new_path