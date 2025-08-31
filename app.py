from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from routes.analysis import analysis_bp
from routes.community import community_bp
from routes.history import history_bp
from routes.index import index_bp
from routes.insights import insights_bp
from routes.LLM import llm_bp
from routes.login import login_bp
from routes.map import map_bp
from routes.signup import signup_bp
from routes.suggestions import suggestions_bp
from routes.auth import auth_bp
from routes.delete_user import delete_user_bp
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

mysql = MySQL(app)

@app.context_processor
def inject_config():
    return dict(config=Config)

app.register_blueprint(delete_user_bp, url_prefix='/delete_user')
app.register_blueprint(analysis_bp, url_prefix='/analysis')
app.register_blueprint(community_bp, url_prefix='/community')
app.register_blueprint(index_bp, url_prefix='/')
app.register_blueprint(insights_bp, url_prefix='/insights')
app.register_blueprint(llm_bp, url_prefix='/LLM')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(map_bp, url_prefix='/map')
app.register_blueprint(signup_bp, url_prefix='/signup')
app.register_blueprint(suggestions_bp, url_prefix='/suggestions')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(history_bp, url_prefix='/history')
if __name__ == '__main__':
    app.run(debug=True)