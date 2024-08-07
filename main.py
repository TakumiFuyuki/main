# main.py

from flask import Flask, request, redirect, url_for, render_template, send_file, flash, session
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
upload_file_table = 'upload_file'
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
        if utils.is_email_registered(email, dataset_name , register_table):
            flash('このメールアドレスはすでに登録されています。')
            return redirect(url_for('register'))
        utils.insert_registration_to_bigquery(email, button_time, password, dataset_name, register_table)
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not utils.authenticate_user(email, password, dataset_name, register_table):
            flash('メールアドレスかパスワードが異なります。')
            return redirect(url_for('login'))
        else:
            session['logged_in'] = True
            session['user'] = email
            return redirect(url_for('upload_file'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('ログアウトしました。')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if not session.get('logged_in'):
        flash('セッションが切れました')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.txt'):
            # ファイルを一時的に保存
            original_filename = file.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{original_filename}"
            file_path = os.path.join('/tmp', unique_filename)
            file.save(file_path)

            # クラウドストレージにアップロード
            blob = bucket.blob(unique_filename)
            blob.upload_from_filename(file_path)

            # BigQuery にレコードを挿入
            email = session.get('user')
            upload_time = datetime.now()
            utils.insert_file_upload_to_bigquery(email, upload_time, unique_filename, dataset_name, upload_file_table)

            # 一時ファイルを削除
            os.remove(file_path)

            return redirect(url_for('list_files'))
        return '無効なファイル形式です。'
    return render_template('upload.html')

@app.route('/list', methods=['GET'])
def list_files():
    if not session.get('logged_in'):
        flash('セッションが切れました')
        return redirect(url_for('login'))

    email = session.get('user')

    # BigQuery から該当ユーザーのファイルリストを取得
    query = f"""
        SELECT filename FROM `{dataset_name}.upload_file`
        WHERE email = '{email}'
    """

    query_job = bigquery_client.query(query)
    results = query_job.result()

    # ファイル名のリストを作成
    file_names = [row['filename'] for row in results]

    blobs = bucket.list_blobs()
    file_list = []
    for blob in blobs:
        if blob.name.endswith('.txt') and blob.name in file_names:
            file_list.append(blob.name)

    return render_template('list_files.html', files=file_list)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if not session.get('logged_in'):
        flash('セッションが切れました')
        return redirect(url_for('login'))

    blob = bucket.blob(filename)
    file_path = os.path.join('/tmp', filename)
    blob.download_to_filename(file_path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(port=8080)