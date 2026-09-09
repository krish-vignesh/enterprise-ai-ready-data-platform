from minio import Minio
from app.config.settings import settings

client = Minio(
    endpoint=f"{settings.minio_host}:{settings.minio_port}", #give the endpoint in the .env file as minio_host=localhost and minio_port=9000
    access_key=settings.minio_username, #give the access key in the .env file as minio_username=minio
    secret_key=settings.minio_password, #give the secret key in the .env file as minio_password=minio123
    secure=False, #set to True if using https
  )
bucket_name = "ai-data" #created manually for sprint 1, but can be created automatically if not exists for future sprints

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' created.")
else:
    print(f"Bucket '{bucket_name}' already exists.")
print("MinIO endpoint:", f"{settings.minio_host}:{settings.minio_port}")
print("MinIO client created successfully!")