from flask import Flask, render_template, redirect, request, url_for
#from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import obter_conexão

#login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'

#login_manager.init_app(app)
#@login_manager.user_loader
#def load_user(user_id):
  #  return User.get(user_id)

@app.route('/')
def index():
    return 'Bem vindo ao projeto de reservas de hoteís. '