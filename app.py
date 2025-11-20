from flask import Flask, render_template, request, send_file
import os
import uuid
import shutil
import json
from core.loader import load_plugins

app = Flask(__name__)
plugins = load_plugins()
print(f"Loaded Plugins: {plugins}")

STORED_FILES_PATH = "stored_files.json"


def load_stored_files():
    if os.path.exists(STORED_FILES_PATH):
        with open(STORED_FILES_PATH, "r") as f:
            return json.load(f)
    return {}


def save_stored_files(stored_files):
    with open(STORED_FILES_PATH, "w") as f:
        json.dump(stored_files, f)


stored_files = load_stored_files()


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
    get_link = request.form.get("get_link") == "true"

    plugin = next(p for p in plugins if p["module"].__name__ == module_name)
    output_file = plugin["module"].convert(file_path)

    name, ext_in = os.path.splitext(original_filename)
    ext_in = ext_in.lstrip(".")
    output_ext = plugin["output"]

    if output_ext == ext_in:
        attachment_filename = f"{name}_converted.{output_ext}"
    else:
        attachment_filename = f"{name}.{output_ext}"

    if get_link:
        file_uuid = str(uuid.uuid4())
        stored_path = os.path.join("downloads", f"{file_uuid}.{output_ext}")
        os.makedirs("downloads", exist_ok=True)
        shutil.copy(output_file, stored_path)

        stored_files[file_uuid] = {"path": stored_path, "filename": attachment_filename}
        save_stored_files(stored_files)

        download_link = request.host_url + f"download/{file_uuid}"
        return render_template("link.html", download_link=download_link)

    return send_file(output_file, as_attachment=True, download_name=attachment_filename)


@app.route("/download/<file_id>")
def download(file_id):
    if file_id not in stored_files:
        return "File not found", 404

    file_info = stored_files[file_id]
    return send_file(
        file_info["path"], as_attachment=True, download_name=file_info["filename"]
    )


@app.route("/framework")
def framework():
    return render_template("framework.html")


if __name__ == "__main__":
    app.run(debug=True)
