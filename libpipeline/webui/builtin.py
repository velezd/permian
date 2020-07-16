from flask import Blueprint, render_template

from .server import WebUI
from .request import currentWebUI

main = Blueprint('main', __name__)
WebUI.registerBlueprint(main)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/webUIuuid')
def webUIuuid():
    return currentWebUI().uuid
