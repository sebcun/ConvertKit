from PIL import Image

input_format = "jpg"
output_format = "png"


def convert(file_path):
    img = Image.open(file_path)
    new_path = file_path.replace(".jpg", "_converted.png")
    img.save(new_path, "PNG")
    return new_path
