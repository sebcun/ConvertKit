from flask import Flask, render_template, request, send_file, jsonify
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

@app.route("/", methods=["GET"])
def index():
    plugins_data = [
        {
            "input": p["input"],
            "output": p["output"],
            "name": p["name"],
            "module": p["module"].__name__,
        }
        for p in plugins
    ]
    return render_template("index.html", plugins=plugins_data)


@app.route("/convert", methods=["POST"])
def convert():
    uploaded = request.files.get("file")
    module_name = request.form.get("module_name")
    get_link = request.form.get("get_link") == "true"

    if not uploaded or uploaded.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = uploaded.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join("uploads", filename)
    uploaded.save(path)

    plugin = next((p for p in plugins if p["module"].__name__ == module_name), None)
    if not plugin:
        if os.path.exists(path):
            os.remove(path)
        return jsonify({"error": "Invalid plugin"}), 400

    output_file = plugin["module"].convert(path)

    name, ext_in = os.path.splitext(uploaded.filename)
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

        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(output_file) and output_file != stored_path:
            os.remove(output_file)

        download_link = request.host_url + f"download/{file_uuid}"
        return jsonify({"download_link": download_link})

    with open(output_file, "rb") as f:
        file_data = f.read()

    try:
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        print(f"Error cleaning up files: {e}")

    from io import BytesIO

    return send_file(
        BytesIO(file_data),
        as_attachment=True,
        download_name=attachment_filename,
        mimetype="application/octet-stream",
    )
                        


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
