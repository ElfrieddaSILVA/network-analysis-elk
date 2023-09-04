from flask import Flask
import os

app = Flask(__name__)


name = os.environ['SRVNAME']

@app.route('/')
def hello():
    return f"Hello, World! I'm {name}!\n"
