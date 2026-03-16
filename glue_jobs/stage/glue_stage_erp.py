import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# RDS connection info
jdbc_url = "jdbc:postgresql://enterprise-sales-dwh-db.c2xwy26cgriw.us-east-1.rds.amazonaws.com:5432/enterprise_db"

db_properties = {
    "user": "dwh_admin",
    "password": "Dashboard#48",
    "driver": "org.postgresql.Driver"
}

# S3 ERP files
# tables = {
#     "erp_cust_az12": "s3://enterprise-db-stage/datasets/source_erp/CUST_AZ12.csv",
#     "erp_loc_a101": "s3://enterprise-db-stage/datasets/source_erp/LOC_A101.csv",
#     "erp_px_cat_g1v2": "s3://enterprise-db-stage/datasets/source_erp/PX_CAT_G1V2.csv"
# }

tables = {
    "erp_cust_az12": "s3a://enterprise-db-stage/datasets/source_erp/CUST_AZ12.csv",
    "erp_loc_a101": "s3a://enterprise-db-stage/datasets/source_erp/LOC_A101.csv",
    "erp_px_cat_g1v2": "s3a://enterprise-db-stage/datasets/source_erp/PX_CAT_G1V2.csv"
}

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

job.commit()
