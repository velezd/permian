import os
import threading
from flask import Blueprint, render_template

from ..api.webui import register_blueprint

TEMPLATES_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
debug = Blueprint('debug', __name__, template_folder=TEMPLATES_DIR)
register_blueprint(debug, '/debug')

@debug.route('/')
def index():
    return render_template('debug.html')

@debug.route('/threads')
def threads():
    return render_template('threads.html', threads=threading.enumerate())
