import json
import psycopg2
import boto3
from botocore.exceptions import ClientError

# --- Lambda Handler ---
def lambda_handler(event, context):
    print("Starting Lambda: Curated CRM SP Loader...")

    # --- Secrets Manager Config ---
    secret_name = "enterprise-sales-dwh-credentials"
    region_name = "us-east-1"

    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        secret_value = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(secret_value['SecretString'])
        print("Successfully retrieved database credentials")
    except ClientError as e:
        print(f"Error fetching secret: {e}")
        raise e

    # --- Extract DB Credentials ---
    db_host = secret_dict['host']
    db_port = secret_dict['port']
    db_user = secret_dict['username']
    db_pass = secret_dict['password']
    db_name = secret_dict['dbname']

    try:
        # --- Connect to RDS PostgreSQL ---
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to PostgreSQL successfully")

        # --- List of SPs ---
        sp_list = [
            "curated.load_crm_cust_info()",
            "curated.load_crm_prd_info()",
            "curated.load_crm_sales_details()"
        ]

        # --- Execute each SP ---
        for sp in sp_list:
            print(f"Executing SP: {sp}")
            cursor.execute(f"CALL {sp};")
            # Optional: fetch row count of corresponding table
            table_name = sp.split(".")[-1].replace("load_", "")
            cursor.execute(f"SELECT COUNT(*) FROM curated.{table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Table curated.{table_name} row count: {row_count}")

        cursor.close()
        conn.close()
        print("All CRM SPs executed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps('Curated CRM SPs executed successfully!')
        }

    except Exception as e:
        print(f"Error executing SPs: {e}")
        raise e
    