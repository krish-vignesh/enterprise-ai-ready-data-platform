from io import BytesIO
from app.storage.minio_client import client


buckets = client.list_buckets()

print("Connected to MinIO successfully!")
print("MinIO client created successfully!")

for bucket in buckets:
    bucket_name = "ai-data" # Temporarily hardcoding the bucket name for testing purposes
    object_name = "test.txt" #Temporarily hardcoding the object name for testing purposes

    data = b"Hello from Sprint 0!"
    data_stream = BytesIO(data)

    client.put_object( #Sdk method to upload the object to the specified bucket
        bucket_name=bucket_name, #Bucket name to which the object will be uploaded
        object_name=object_name, #Name of the object to be uploaded
        data=data_stream, #Data stream containing the object data
        length=len(data),
        content_type="text/plain",
    )

    print(f"Object '{object_name}' uploaded successfully!")