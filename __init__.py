from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_PORT'] = 3306 
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '!S6@d1#Qe$02%vL^0r&06*a'
    app.config['MYSQL_DB'] = 'terragen'
    app.config['SECRET_KEY'] = 'super-secret-key'

    mysql.init_app(app)

    from .routes.community import community_bp
    app.register_blueprint(community_bp, url_prefix='/community')

    # register other blueprints...

    return app
