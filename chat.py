from app import create_app, socketio

app = create_app(debug=True)
print(app.root_path)
if __name__ == "__main__":
    socketio.run(app ,host='localhost', port=5000)