from flask import session, redirect ,url_for, render_template, request, Blueprint, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from . import main
from .. import db 
from ..models import User
from .events import userConnect
from flask import send_file, send_from_directory, safe_join, abort
from sqlalchemy import text
from ..models import UserSchema
@main.route('/')
def index():
    return render_template('sign-in.html')

#  đăng nhập web chat
@main.route('/login')
def login():
    return render_template('sign-in.html')
    
@main.route('/login', methods=['POST','GET'])
def login_post():
    email = request.form.get('inputEmail')
    password = request.form.get('inputPassword')

    user = User.query.filter_by(email=email).first()
    if(user.id not in userConnect):
        if (user and check_password_hash(user.password, password)):
            login_user(user)
            return redirect(url_for('main.chat'))
        else:
            flash('Incorrect username or password.')
            return redirect(url_for('main.login'))
    else:
        print("da dang nhap")
        flash('Your Account has logged.')
        return redirect(url_for('main.login'))


# Đăng ký tài khoản
@main.route('/signup')
def signup():
    return render_template('sign-up.html')

@main.route('/signup', methods=['POST','GET'])
def signup_post():
    email = request.form.get('inputEmail')
    username = request.form.get('inputName')
    password = request.form.get('inputPassword')
    phone = request.form.get('inputPhone')

    if(email =='' or username == '' or password=='' or phone==''):
        flash('Please fill all required fields ')
        return redirect(url_for('main.signup'))
    #Kiem tra xem co email co trong database chua 
    user = User.query.filter_by(email=email).first()
    if user : 
        flash('Email address already exists.')
        return redirect(url_for('main.signup'))
    new_user = User(email=email, phone=phone, username=username, password=generate_password_hash(password,method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('main.login'))


# Out tài khoản
@main.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    logout_user()
    return render_template('login.html')



# khung chat
@main.route('/chat')
@login_required
def chat():
    if not session.get('logged_in'):

        # sql1 = text('SELECT id FROM User WHERE username = :x')
        # id_user = db.engine.execute(sql1, x=current_user.username).fetchall()
        # user_schema = UserSchema(many=True)
        # json = user_schema.dump(id_user)
        # print("USER_ID :"+json)

        # sql = text('SELECT * FROM message WHERE  content IS NOT NULL ORDER BY datetime DESC LIMIT 1' )
        # historyChat = db.engine.execute(sql, x=int(msg['receiver'])).fetchall()
        # history_schema = MesssageSchema(many=True)
        # json = history_schema.dump(historyChat)
        # print(json)
        user = current_user
        users = User.query.filter(User.email != current_user.email).all()

        return render_template('index-2.html',user = user, users = users)

@main.route('/chat',methods=['POST','GET'])
@login_required
def chat_in():
    if not session.get('logged_in'):
        user = current_user
        users = User.query.filter(User.email != current_user.email).all()

        email = request.form.get('myEmail')
        username = request.form.get('myName')
        password = request.form.get('myPassword')
        phone = request.form.get('myPhone')
        image = request.form.get('Avatar')
        # print(image);
        # print(email + "-"+ username +'-' + password +'-'+ phone)
        return render_template('index-2.html',user = user, users = users)

@main.route("/chat/<name1>")
@login_required
def send_file(name1):
    save_path = "C:/Users/ACER/Documents/DEV/Web-chat-project-1/app/static/file"
    try:
        print("Download file :"+name1 )
        return send_from_directory(save_path, filename=name1, as_attachment=True)
    except FileNotFoundError as err:
        abort(404)