import json
import psycopg2
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print("Starting Lambda: Consumption Dim Products Loader...")

    secret_name = "enterprise-sales-dwh-credentials"
    region_name = "us-east-1"

    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        secret_value = client.get_secret_value(SecretId=secret_name)
        db_creds = json.loads(secret_value['SecretString'])
        print("Successfully retrieved database credentials")
    except ClientError as e:
        print(f"Error fetching secret: {e}")
        raise e

    try:
        conn = psycopg2.connect(
            host=db_creds['host'],
            port=db_creds['port'],
            database=db_creds['dbname'],
            user=db_creds['username'],
            password=db_creds['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to PostgreSQL successfully")

        sp_name = event.get('sp_name', 'consumption.load_dim_products()')
        print(f"Executing SP: {sp_name}")
        cursor.execute(f"CALL {sp_name};")

        # Optional: row count check
        table_name = sp_name.split('.')[-1].replace('load_', '').replace('()', '')
        cursor.execute(f"SELECT COUNT(*) FROM consumption.{table_name};")
        row_count = cursor.fetchone()[0]
        print(f"Table consumption.{table_name} row count: {row_count}")

        cursor.close()
        conn.close()

        return {"status": "success", "table": table_name, "row_count": row_count}

    except Exception as e:
        print(f"Error executing SP: {e}")
        raise e
