# utils.py

from google.cloud import bigquery, storage
import re
bigquery_client = bigquery.Client()
storage_client = storage.Client()

def is_valid_password(password):
    if len(password) < 4:
        return False
    if not re.search('[A-Za-z]', password):
        return False
    if not re.search('[0-9]', password):
        return False
    return True

# def is_email_registered(email, dataset_name , register_table, bigquery_client):
def is_email_registered(email, dataset_name , register_table):
    query = f"""
    SELECT COUNT(1) as count FROM `{dataset_name}.{register_table}`
    WHERE e-mail = '{email}'
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    for row in results:
        if row['count'] > 0:
            return True
    return False

# def insert_registration_to_bigquery(email, button_time, password, dataset_name, register_table, bigquery_client):
def insert_registration_to_bigquery(email, button_time, password, dataset_name, register_table):
    button_time_iso = button_time.isoformat()
    rows_to_insert = [
        {
            'datetime': button_time_iso,
            'e-mail': email,
            'password': password
        }
    ]
    table_id = f'{dataset_name}.{register_table}'
    errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        raise Exception(f'BigQueryへのデータ挿入中にエラーが発生しました: {errors}')

def authenticate_user(email, password, dataset_name, register_table, bigquery_client):
    query = f"""
    SELECT password FROM `{dataset_name}.{register_table}`
    WHERE e-mail = '{email}'
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    for row in results:
        if row['password'] == password:
            return True
    return False