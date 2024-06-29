# main.py

from flask import Flask, request, redirect, url_for, render_template
from google.cloud import storage
import os

app = Flask(__name__)

# Google Cloud Storageのクライアントを初期化
storage_client = storage.Client()
bucket_name = 'your-bucket-name'
bucket = storage_client.bucket(bucket_name)

@app.route('/')
def hello():
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=8080)