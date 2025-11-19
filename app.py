from flask import Flask, render_template, request
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

        return render_template("index.html", message=f"File uploaded as {filename}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
