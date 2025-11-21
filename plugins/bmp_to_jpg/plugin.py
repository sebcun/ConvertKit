# TITLE: BMP to JPG
# AUTHOR: @sebastian

from PIL import Image

title = "BMP to JPG"
input_format = "bmp"
output_format = "jpg"


def convert(file_path):
    img = Image.open(file_path)
    new_path = file_path.replace(".bmp", "_converted.jpg")
    img.convert("RGB").save(new_path, "JPEG")
    return new_path
