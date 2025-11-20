from flask import Flask, render_template, request, send_file
import os
import uuid
from core.loader import load_plugins

app = Flask(__name__)
plugins = load_plugins()
print(f"Loaded Plugins: {plugins}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded = request.files.get("file")

        if not uploaded or uploaded.filename == "":
            return render_template("index.html", message="No file selected")

        ext = uploaded.filename.split(".")[-1]

        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join("uploads", filename)
        uploaded.save(path)

        available = [p for p in plugins if p["input"] == ext]

        return render_template(
            "result.html",
            file_path=path,
            plugins=available,
            original_filename=uploaded.filename,
        )

    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    file_path = request.form["file_path"]
    module_name = request.form["module_name"]
    original_filename = request.form["original_filename"]

    plugin = next(p for p in plugins if p["module"].__name__ == module_name)
    output_file = plugin["module"].convert(file_path)

    name, ext_in = os.path.splitext(original_filename)
    ext_in = ext_in.lstrip(".")
    output_ext = plugin["output"]

    if output_ext == ext_in:
        attachment_filename = f"{name}_converted.{output_ext}"
    else:
        attachment_filename = f"{name}.{output_ext}"

    return send_file(output_file, as_attachment=True, download_name=attachment_filename)


@app.route("/framework")
def framework():
    return render_template("framework.html")


if __name__ == "__main__":
    app.run(debug=True)
