import json
from app.storage.minio_client import client
from io import BytesIO

def save_data(request):
    bucket_name = "ai-data"  # Hardcoding the bucket name for now, can be made dynamic in future sprints
    object_name = f"{request.dataset}.json"  #Using dataset as it gives the name of the dataset


   # Convert the request payload to JSON and then to bytes
    data = json.dumps(request.payload).encode('utf-8') #using payload because it contains the actual data to be stored in the minio bucket, and we are converting it to bytes because the put_object method requires a bytes-like object
    data_stream = BytesIO(data) #BytesIO is used to create a file-like object from the bytes data, which can be passed to the put_object method

    # Upload the object to MinIO
    client.put_object( #Sdk method to upload the object to the specified bucket
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream,
        length=len(data),   
        content_type="application/json",
    )

    print(f"Object '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

    return object_name  # Return the object name for reference


def save_file(metadata, file):
    bucket_name = "ai-data"  # Hardcoding the bucket name for now, can be made dynamic in future sprints
    object_name = f"{metadata.dataset}/{file.filename}"  # Using dataset as it gives the name of the dataset and file.filename to get the name of the file

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    # Upload the file to MinIO
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=file.file,  # Using file.file to get the actual file object
        length=file_size,  # Using file.content_length to get the size of the file
        content_type=file.content_type,  # Using file.content_type to get the content type of the file
    )

    print(f"File '{file.filename}' uploaded successfully to bucket '{bucket_name}' under '{metadata.dataset}'.")

    return object_name  # Return the object name for reference