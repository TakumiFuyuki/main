# main.py

from flask import Flask, request, redirect, url_for, render_template
from google.cloud import storage
import os

app = Flask(__name__)

# Google Cloud Storageのクライアントを初期化
storage_client = storage.Client()
bucket_name = 'text_upload'
bucket = storage_client.bucket(bucket_name)

@app.route('/')
def hello():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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

@app.route('/list')
def list_files():
    blobs = bucket.list_blobs()
    file_list = []
    for blob in blobs:
        if blob.name.endswith('.txt'):
            file_list.append(blob.name)

    return render_template('list_files.html', files=file_list)

if __name__ == '__main__':
    app.run(port=8080)