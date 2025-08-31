from flask import Blueprint, render_template

# Create a Blueprint instance for the index routes.
# The name 'index_bp' is used to register it in app.py.
# The __name__ argument is the name of the blueprint's module.
# The template_folder and static_folder arguments tell Flask where to find
# the templates and static files specifically for this blueprint.
index_bp = Blueprint('index_bp', __name__, template_folder='../templates', static_folder='../static')

# Define a route for the blueprint
# The route path is relative to the url_prefix set in app.py.
# Since we set the prefix for this blueprint to '/', this route will be at '/'.
@index_bp.route('/')
def index():
    # render_template will look for the file in the 'templates' directory
    return render_template('index.html')
