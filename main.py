# main.py

from flask import Flask, request, redirect, url_for, render_template, send_file
from google.cloud import storage
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# # サービスアカウントキーの JSON ファイルのパスを指定します
# key_path = 'C:\\Users\\taku0\\OneDrive\\デスクトップ\\tasks\\main\\service_account_key.json'
# # あなたのプロジェクト ID を指定
# project_id = 'my-project-46138-427502'

# # JSONファイルが存在するか確認
# if os.path.exists(key_path):
#     print('kon')

# print("Current working directory:", os.getcwd())

# サービスアカウントキーの JSON ファイルのパスを環境変数に設定します
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C://Users//taku0//OneDrive//デスクトップ//tasks//main//service_account_key.json"

# クライアントを初期化し、認証情報を設定します
# storage_client = storage.Client.from_service_account_json(key_path, project=project_id)
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

# @app.route('/download/<filename>')
# def download_file(filename):
#     blob = bucket.blob(filename)
#     file_path = os.path.join('/tmp', filename)
#     blob.download_to_filename(file_path)
#     return send_file(file_path, as_attachment=True)

@app.route('/download/<filename>')
def download_file(filename):
    # ダウンロード対象のファイルのblobオブジェクトを取得
    blob = bucket.blob(filename)

    # ダウンロード用の一時URLを生成する
    expiration = datetime.now() + timedelta(hours=1)  # 現在時刻から1時間有効
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=expiration,
        method="GET",
    )

    # 生成したURLをリダイレクトしてダウンロードさせる
    return redirect(signed_url)

if __name__ == '__main__':
    app.run(port=8080)