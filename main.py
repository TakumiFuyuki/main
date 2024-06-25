from flask import Flask, request, render_template, flash, redirect, url_for
from google.cloud import storage
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Google Cloud Storage の設定
bucket_name = 'text_upload'  # 自分のバケット名に置き換える
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'  # サービスアカウントキーのパスに置き換える

# Google Cloud Storage クライアントの初期化
client = storage.Client()

@app.route('/')
def upload_form():
    return render_template('upload.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)

#     file = request.files['file']

#     if file.filename == '':
#         flash('No selected file')
#         return redirect(request.url)

#     # Google Cloud Storage にファイルをアップロード
#     bucket = client.get_bucket(bucket_name)
#     blob = bucket.blob(file.filename)
#     blob.upload_from_file(file)

#     flash('File successfully uploaded to Cloud Storage')
#     return redirect(url_for('upload_form'))

if __name__ == '__main__':
    app.run(debug=True)