import json
import psycopg2
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):

    print("Starting Lambda: Curated ERP SP Loader...")

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


        # --- List of ERP Stored Procedures ---
        sp_list = [
            "curated.load_erp_cust_az12()",
            "curated.load_erp_loc_a101()",
            "curated.load_erp_px_cat_g1v2()"
        ]


        # --- Execute each SP ---
        for sp in sp_list:
            print(f"Executing SP: {sp}")
            cursor.execute(f"CALL {sp};")

            # Derive table name
            sp_name = sp.split(".")[-1]      # e.g., load_erp_cust_az12()
            table_name = sp_name.replace("load_", "").replace("()", "")

            # Check row count
            cursor.execute(f"SELECT COUNT(*) FROM curated.{table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Table curated.{table_name} row count: {row_count}")


        cursor.close()
        conn.close()
        print("All ERP SPs executed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps('Curated ERP SPs executed successfully!')
        }


    except Exception as e:
        print(f"Error executing ERP SPs: {e}")
        raise e
