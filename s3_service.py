import os
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

print("S3 REGION:", AWS_REGION)
print("S3 BUCKET:", S3_BUCKET)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_file(file, filename):
    s3.upload_fileobj(
        file,
        S3_BUCKET,
        filename
    )

    return f"File uploaded successfully: {filename}"


def get_storage_info():
    total_size = 0
    file_count = 0
    files = []

    response = s3.list_objects_v2(
        Bucket=S3_BUCKET
    )

    for obj in response.get("Contents", []):

        total_size += obj["Size"]
        file_count += 1

        files.append({
            "name": obj["Key"],
            "size": obj["Size"]
        })

    return {
        "total_size": total_size,
        "file_count": file_count,
        "files": files
    }
    
def download_file(filename):
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": filename
        },
        ExpiresIn=300
    )


def delete_file(filename):
    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=filename
    )

    return f"File deleted successfully: {filename}"