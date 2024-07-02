# main.py

from flask import Flask, request, redirect, url_for, render_template, send_file
from google.cloud import storage
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# クライアントを初期化し、認証情報を設定します
storage_client = storage.Client()
bucket_name = 'text_upload'
bucket = storage_client.bucket(bucket_name)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def index():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.methods == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.txt'):
            # ファイルを一時的に保存
            file_path = os.path.join('/tmp', file.filename)
            file.save(file_path)

            # クラウドストレージにアップロード
            blob = bucket.blob(file.filename)
            blob.upload_from_filename(file_path)

            # 一時ファイルを削除
            os.remove(file_path)

            return redirect(url_for('list_files'))
        return '無効なファイル形式です。'
    return render_template('upload.html')

@app.route('/list')
def list_files():
    blobs = bucket.list_blobs()
    file_list = []
    for blob in blobs:
        if blob.name.endswith('.txt'):
            file_list.append(blob.name)

    return render_template('list_files.html', files=file_list)

@app.route('/download/<filename>')
def download_file(filename):
    blob = bucket.blob(filename)
    file_path = os.path.join('/tmp', filename)
    blob.download_to_filename(file_path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(port=8080)