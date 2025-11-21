# TITLE: TXT to TXT (uppercase)
# AUTHOR: @sebastian


title = "TXT to TXT (uppercase)"
input_format = "txt"
output_format = "txt"


def convert(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_path = file_path.replace(".txt", "_converted.txt")
    with open(new_path, "w", encoding="utf-8") as f:
        f.write(content.upper())

    return new_path
