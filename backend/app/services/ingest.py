from app.storage.ingest import save_data



def ingest_data(request): #Service travel in the route to storage
    file_path = save_data(request)
    return {
        "status": "completed",
        "message": f"Data {request.dataset}ingestion completed successfully"
    }