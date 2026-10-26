FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY s3_service.py .
COPY db_service.py .

EXPOSE 5000

CMD ["python", "app.py"]