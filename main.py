# main.py

from flask import Flask, request, redirect, url_for, render_template, send_file, flash
from google.cloud import storage, bigquery
import os
from datetime import datetime, timedelta
import utils

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# クライアントを初期化し、認証情報を設定します
bigquery_client = bigquery.Client()
storage_client = storage.Client()

dataset_name = 'my-project-46138-427502.dataset'
register_table = 'register'
bucket_name = 'text_upload'
bucket = storage_client.bucket(bucket_name)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        button_time = datetime.now()
        email = request.form['email']
        password = request.form['password']
        if not utils.is_valid_password(password):
            flash('パスワードは4文字以上で、アルファベットと数字が少なくとも1文字以上含まれている必要があります。')
            return redirect(url_for('register'))
        if utils.is_email_registered(email):
            flash('このメールアドレスはすでに登録されています。')
            return redirect(url_for('register'))
        utils.insert_register_to_bigquery(email, button_time, password)
        flash('登録が完了しました。ログインしてください。')
        return 'a'
        # return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not utils.authenticate_user(email, password, dataset_name, register_table, bigquery_client):
            flash('メールアドレスかパスワードが異なります。')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('main'))
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