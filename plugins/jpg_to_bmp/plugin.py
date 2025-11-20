from PIL import Image

input_format = "jpg"
output_format = "bmp"


def convert(file_path):
    img = Image.open(file_path)
    new_path = file_path.replace(".jpg", "_converted.bmp")
    img.save(new_path, "BMP")
    return new_path
