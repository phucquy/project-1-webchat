from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import session
from flask_session import Session
# import redis
# import eventlet
socketio = SocketIO()
db = SQLAlchemy()
ma = Marshmallow()
sess = Session()

def create_app(debug=False):

    app = Flask(__name__)
    app.debug = debug
    
    #flask-socketio
    app.config['SECRET_KEY'] = 'leagueoflegends'
    app.config['SESSION_TYPE'] = 'filesystem'
    socketio.init_app(app)

    # redis.Redis(host='localhost', port=5000)
    # app.config['SESSION_TYPE'] = 'redis'
    

    # flask-session
    sess.init_app(app)


    #flask-sqlalchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:admin@127.0.0.1/chatapp'
    db.init_app(app)
    ma.init_app(app)

    # flask-login
    login_manager = LoginManager()
    login_manager.login_view ='main.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app