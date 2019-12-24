from flask import session, request
from flask_socketio import emit, join_room, leave_room, send
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import text
from .. import socketio
from . import main
from .. import db


from ..models import User
from ..models import Message
from ..models import MesssageSchema
import json
import os
import flask

import base64
from base64 import b64decode

from flask import send_file, send_from_directory, safe_join, abort

userConnect = []
userRoom = []
@socketio.on('connect', namespace='/chat')
def on_connect():
    if current_user.is_authenticated :
        print(request.sid)

        if(current_user.id not in userConnect):
            userConnect.append(current_user.id)
            userRoom.append(request.sid)
        else :
            for i, user in enumerate(userConnect):
                if(current_user.id == user):
                    userRoom.remove(userRoom[i])
                    userConnect.remove(current_user.id)
                    userConnect.append(current_user.id)
                    userRoom.append(request.sid)
        msg = {'connected_id' : userConnect}
        emit('response_connect',msg, broadcast = True)
# @socketio.on('disconnect', namespace = '/chat')
# def on_disconnect():
#     print('Client disconnected id : ' + str(current_user.id))
#     if(current_user.id in userConnect):
#         for i, user in enumerate(userConnect):
#             if(current_user.id == user):
#                 userRoom.remove(userRoom[i])
#         userConnect.remove(current_user.id)
#     msg = {'disconnect_id' : current_user.id}
#     emit('response_disconnect', msg , broadcast = True)

@socketio.on('logout_account', namespace = '/chat')
def logout(msg):
    logout_id = int(msg['logout_id']);
    for i,user in enumerate(userConnect):
        if(logout_id == user):
            userRoom.remove(userRoom[i])
    userConnect.remove(logout_id)
    msg = {'disconnect_id' : logout_id}
    emit('response_disconnect', msg , broadcast = True)
    print("nguoi dung da thoat")

@socketio.on('my_event_chat', namespace='/chat')
def chat(msg):
    if current_user.is_authenticated :
        id_receiver = int(msg['receiver']);
        id_sender = int(msg['sender']);
        messageReceiver = msg['message'];
        time1 =  msg['time']
        # print(msg)
        message = Message(user_1=id_receiver , user_2=id_sender ,content=messageReceiver, datetime=time1) 
        db.session.add(message)
        db.session.commit()
        for i, user in enumerate(userConnect):
            if(int(msg['receiver']) == user):
                emit('my_response_chat', msg , room=userRoom[i])

@socketio.on('chat_history', namespace='/chat')
def history(msg):
    if current_user.is_authenticated :
        sql = text('SELECT * FROM message WHERE (user_1 = :x AND user_2 = :y) OR (user_1 = :y AND user_2 = :x) AND content IS NOT NULL ORDER BY datetime  LIMIT 20' )
        historyChat = db.engine.execute(sql, x=int(msg['receiver']), y=int(msg['sender'])).fetchall()
        history_schema = MesssageSchema(many=True)
        json = history_schema.dump(historyChat)
        # print(json)
        for i, user in enumerate(userConnect):
            if (msg['sender'] == user):
                emit('response_chat_history', json, room = userRoom[i])

@socketio.on('update_account', namespace='/chat')
def updateAcount(msg):
    if current_user.is_authenticated :
        id_update   = msg['id']
        username    = msg['myName']
        email       = msg['myEmail']
        phone       = msg['myPhone']
        password    = msg['myPassword']
        image       = msg['myImage']
        update_data = User.query.filter_by(id=id_update).first()
        if(password ==""):
            update_data.username = username
            update_data.email = email
            update_data.phone = phone
            update_data.image = image
            db.session.commit()
            print("update without password")
        else :
            update_data.username = username
            update_data.email = email
            update_data.phone = phone
            update_data.image = image
            update_data.password = generate_password_hash(password,method='sha256')
            db.session.commit()
            print("update with password")
            
        for i, user in enumerate(userConnect):
            if (msg['id'] == user):
                message  = "Update Successful"
                emit('update_successful', message, room = userRoom[i])

        
@socketio.on('slice_upload', namespace='/chat')
def updaloadAvatar(msg):
    if current_user.is_authenticated :
        nameImage = msg['name']
        data = msg['data']
        dataImg = data.split(",")
        decode = base64.urlsafe_b64decode(dataImg[1])

        save_path = 'C:/Users/ACER/Documents/DEV/Web-chat-project-1/app/static'
        completeName  = os.path.join(save_path,nameImage)
        f = open(completeName, 'wb')
        f.write(decode)
        f.close()
        print("save  image thanh cong")

@socketio.on('slice_upload_file', namespace='/chat')
def slice_upload_file(msg):
    if current_user.is_authenticated :
        namfile = msg['name']
        data = msg['data']
        dataFile = data.split(",")
        decode = base64.urlsafe_b64decode(dataFile[1])

        # Save data 
        save_path = 'C:/Users/ACER/Documents/DEV/Web-chat-project-1/app/static/file'
        completeName  = os.path.join(save_path,namfile)
        f = open(completeName, 'wb')
        f.write(decode)
        f.close()

        # Save history
        id_receiver = int(msg['receiver']);
        id_sender = int(msg['sender']);
        filename = 'namefile#'+msg['name'];
        time =  msg['time']
        # print(msg)
        message = Message(user_1=id_receiver , user_2=id_sender ,content=filename , datetime=time) 
        db.session.add(message)
        db.session.commit()
        # Display  receiver message
        for i, user in enumerate(userConnect):
            if(int(msg['receiver']) == user):
                emit('my_response_chat', msg , room=userRoom[i])

        print("save file thanh cong")

@socketio.on('download_file', namespace='/chat')
def sendFile(filename):
    save_path = "C:/Users/ACER/Documents/DEV/Web chat project 1/app/static/file"
    
    try:
        print("Name :"+ filename)
        # return flask.send_from_directory('C:\\Users\\ACER\\Documents\\DEV\Web_chat_project_1\\app\\static', 'image.png', as_attachment=True)
        return flask.send_from_directory('C:\\Users\\ACER\\Documents\\DEV\Web_chat_project_1\\app\\static\\file', filename, as_attachment=True)
    except FileNotFoundError as err:
        abort(404)