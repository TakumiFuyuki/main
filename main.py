# main.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World! This is a Flask main running on Google main Engine.'

if __name__ == '__main__':
    app.run(port=8080)