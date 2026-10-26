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


def upload_file(file, s3_key):
    s3.upload_fileobj(
        file,
        S3_BUCKET,
        s3_key
    )

    return f"File uploaded successfully: {s3_key}"


def get_storage_info(prefix=None):

    total_size = 0
    file_count = 0
    files = []
    file_types = {}

    list_params = {
        "Bucket": S3_BUCKET
    }

    # Only show files belonging to this user
    if prefix:
        list_params["Prefix"] = prefix

    response = s3.list_objects_v2(**list_params)

    for obj in response.get("Contents", []):

        s3_key = obj["Key"]
        size = obj["Size"]

        # Don't treat folder markers as files
        if s3_key.endswith("/"):
            continue

        # Display only the filename, not the complete S3 path
        filename = s3_key.split("/")[-1]

        total_size += size
        file_count += 1

        if "." in filename:
            extension = "." + filename.rsplit(".", 1)[1].lower()
        else:
            extension = "Other"

        file_types[extension] = (
            file_types.get(extension, 0) + size
        )

        files.append({
            "name": filename,
            "s3_key": s3_key,
            "size": size,
            "type": extension
        })

    largest_files = sorted(
        files,
        key=lambda x: x["size"],
        reverse=True
    )[:5]

    return {
        "total_size": total_size,
        "file_count": file_count,
        "files": files,
        "file_types": file_types,
        "largest_files": largest_files
    }


def download_file(s3_key):

    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": s3_key
        },
        ExpiresIn=300
    )


def delete_file(s3_key):

    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=s3_key
    )

    return f"File deleted successfully: {s3_key}"