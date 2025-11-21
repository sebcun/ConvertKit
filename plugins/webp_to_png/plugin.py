# TITLE: WEBP to PNG
# AUTHOR: @sebastian

from PIL import Image

title = "WEBP to PNG"
input_format = "webp"
output_format = "png"


def convert(file_path):
    img = Image.open(file_path)
    new_path = file_path.replace(".webp", "_converted.png")
    img.save(new_path, "PNG")
    return new_path