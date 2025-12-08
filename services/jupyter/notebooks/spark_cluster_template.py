from pyspark.sql import SparkSession

## Function
def create_spark_session(app_name: str = "ClientModeS3App") -> SparkSession:
    """
    Initialize SparkSession configured for cluster mode with S3 access.
    """
    spark = (
        SparkSession.builder.appName(app_name)
        .master("spark://master:7077")  # Spark master URL for cluster
        .config("spark.driver.memory", "4G")  # Driver memory allocation
        .config("spark.executor.instances", "2")  # Number of executors
        .config("spark.executor.cores", "1")  # Cores per executor
        .config("spark.executor.memory", "1G")  # Executor memory
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio-cs:9990")  # S3 endpoint
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")  # Disable SSL
        .config("spark.hadoop.fs.s3a.path.style.access", "true")  # Path-style S3 access
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
        )
        .config("spark.hadoop.fs.s3a.access.key", "minio")  # S3 access key
        .config("spark.hadoop.fs.s3a.secret.key", "minio123")  # S3 secret key
        .config("spark.eventLog.enabled", "true")  # Enable event logging
        .config("spark.eventLog.dir", "file:/tmp/spark-events")  # Event log directory
        .getOrCreate()
    )
    return spark

def create_sample_dataframe(spark: SparkSession):
    """
    Create a sample DataFrame with test data.
    """
    data = [
        (1, "Alice", 23),
        (2, "Bob", 30),
        (3, "Charlie", 28)
    ]
    columns = ["id", "name", "age"]
    df = spark.createDataFrame(data, columns)
    return df

def write_to_s3(df, path: str):
    """
    Write DataFrame to S3 in Parquet format.
    """
    df.write.mode("overwrite").parquet(path)
    print(f"DataFrame successfully written to {path}")


# Main
if __name__ == "__main__":
    spark = create_spark_session()
    try:
        df = create_sample_dataframe(spark)
        write_to_s3(df, "s3a://corin/corin_test_2.parquet")
    finally:
        spark.stop()