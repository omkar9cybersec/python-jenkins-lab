import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Secret sirf environment variable se aayega, code mein kabhi nahi
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
APP_VERSION = os.environ.get("APP_VERSION", "1.0")


@app.get("/")
def home():
    return render_template("index.html", version=APP_VERSION)


@app.get("/about")
def about():
    return render_template("about.html")


@app.get("/health")
def health():
    return jsonify(status="ok"), 200
