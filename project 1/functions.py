
from flask import Flask,request,redirect, url_for, render_template, flash, session
from flask.json import jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
import os



functions = Flask(__name__)
functions.config['SECRET_KEY'] = 'top secret!'
functions.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
functions.config['OAUTH_CREDENTIALS'] = {
    'github': {
        'id': '4d08ab3b69881a406b10',
        'secret': '37ce557dccd9537b46eead4866e847a7bb6074f9'
    }
 }






db = SQLAlchemy(functions)
lm = LoginManager(functions)
lm.login_view = 'homepage'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)




@lm.user_loader
def load_user(id):
    return User.query.get(int(id))



@functions.route('/')
def index():
    return render_template('homepage.html')


@functions.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage.html'))


 




@functions.route('/authorize/<provider>')
def oauth_authorize(provider):      #oauth start
    oauth = OAuthSignIn.get_provider(provider)
    session['state'] = oauth.state
    session['next'] = request.args.get('next', '')
    return oauth.authorize()


@functions.route('/callback/<provider>')
def oauth_callback(provider):       #oauth callback
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, url, jsonme = oauth.callback()    
    return oauth_callback(provider)


@functions.route('/sum/<int:a>/<int:b>',methods = ["GET"])
def sum(a,b):
    answer = a+b
    return jsonify(answer)


@functions.route('/multiply/<int:a>/<int:b>/<int:c>',methods = ["GET"])
def multiply(a,b,c):
    answer = a*b*c
    return jsonify(answer)



@functions.route('/divide/<int:a>/<int:b>/<int:c>',methods = ["GET"])
def divide(a,b,c):
    answer = a/b/c
    return jsonify(answer)



@functions.route('/modulus/<int:a>/<int:b>',methods = ["GET"])
def modulus(a,b):
    answer = a%b
    return jsonify(answer)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
if __name__ == '__main__':
    db.create_all()
    functions.run(debug = True)






