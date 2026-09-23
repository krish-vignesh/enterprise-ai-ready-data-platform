from app.storage.ingest import save_data, save_file



def ingest_data(request): #Service travel in the route to storage
    file_path = save_data(request)
    return {
        "status": "completed",
        "message": f"Data {request.dataset}ingestion completed successfully"
    }

def ingest_file_data(metadata, file):
    file_path = save_file(metadata, file)

    return {
        "status": "completed",
        "message": f"File {metadata.dataset} ingestion completed successfully"
    }