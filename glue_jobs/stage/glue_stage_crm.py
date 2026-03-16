import sys
import boto3
import json
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

print("Starting CRM Stage Load...")

# -----------------------------
# Fetch Secrets
# -----------------------------
secret_name = "enterprise-sales-dwh-credentials"
region_name = "us-east-1"

session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

response = client.get_secret_value(SecretId=secret_name)
secret = json.loads(response['SecretString'])

username = secret['username']
password = secret['password']
host = secret['host']
port = secret['port']
dbname = secret['dbname']

print("Successfully retrieved database credentials")

# -----------------------------
# JDBC Connection
# -----------------------------
jdbc_url = f"jdbc:postgresql://{host}:{port}/{dbname}"

db_properties = {
    "user": username,
    "password": password,
    "driver": "org.postgresql.Driver"
}

# -----------------------------
# S3 CRM Files
# -----------------------------
tables = {
    "crm_cust_info": "s3://enterprise-db-stage/datasets/source_crm/cust_info.csv",
    "crm_prd_info": "s3://enterprise-db-stage/datasets/source_crm/prd_info.csv",
    "crm_sales_details": "s3://enterprise-db-stage/datasets/source_crm/sales_details.csv"
}

# -----------------------------
# Load Each Table
# -----------------------------
for table, path in tables.items():

    print(f"Loading {table} from {path}")

    df = spark.read.option("header", True).csv(path)

    df.write.jdbc(
        url=jdbc_url,
        table=f"stage.{table}",
        mode="overwrite",
        properties=db_properties
    )

    print(f"{table} loaded successfully")

print("CRM Stage Load Completed")

job.commit()
