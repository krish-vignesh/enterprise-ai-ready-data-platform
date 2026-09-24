# ==========================================
# MinIO Bucket Initialization Container
# ==========================================

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY init_minio.py .

ENTRYPOINT ["python", "init_minio.py"]