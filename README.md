# CloudDrop — Secure Cloud-Based File Storage and Management System

CloudDrop is a cloud-based file storage and management application built using Python, Flask, and Amazon Web Services (AWS). It enables authenticated users to upload, download, share, and delete files while monitoring storage usage and detecting duplicate uploads.

The project demonstrates cloud storage, authentication, database integration, event-driven processing, monitoring, and containerization.

## Key Features

- **User Authentication:** Registration and login using Amazon Cognito.
- **Cloud File Storage:** Upload and store files in Amazon S3.
- **User-Specific Storage:** Organize files under user-specific S3 prefixes.
- **File Management:** Upload, download, share, and delete files.
- **Secure File Sharing:** Generate temporary S3 presigned URLs.
- **Duplicate Detection:** Use SHA-256 file hashes to identify duplicate uploads.
- **Storage Analytics:** Display file counts, storage usage, file types, and large files.
- **Database Integration:** Store user information and file metadata in Amazon RDS MySQL.
- **Event-Driven Processing:** Use AWS Lambda to process configured S3 events.
- **Email Notifications:** Send configured notifications using Amazon SNS.
- **Monitoring and Logging:** Use Amazon CloudWatch to inspect Lambda logs and monitor activity.
- **Containerization:** Package the application using Docker.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Cloud Storage | Amazon S3 |
| Database | Amazon RDS MySQL |
| Authentication | Amazon Cognito |
| Serverless Processing | AWS Lambda |
| Notifications | Amazon SNS |
| Monitoring | Amazon CloudWatch |
| AWS SDK | Boto3 |
| Database Connector | PyMySQL |
| Containerization | Docker |
| Networking and Access Control | Amazon VPC, Security Groups, IAM |

## System Architecture

1. Users access CloudDrop through the web application.
2. Amazon Cognito authenticates users.
3. Flask handles application routes and authenticated requests.
4. Amazon S3 stores files under user-specific prefixes.
5. Amazon RDS MySQL stores user records and file metadata used for duplicate detection and file management.
6. S3 events trigger the configured AWS Lambda function.
7. Lambda can publish notifications through Amazon SNS.
8. Amazon CloudWatch collects Lambda logs for troubleshooting and monitoring.

## Project Structure

The main application files include:

- `app.py` — Flask application, routes, authentication, and file operations.
- `s3_service.py` — S3 storage and file operations.
- `db_service.py` — MySQL connectivity, user records, metadata, and duplicate detection.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — Instructions for building the Docker image.
- `.dockerignore` — Files excluded from the Docker build context.
- `.gitignore` — Files excluded from Git tracking.

HTML templates, static assets, and additional configuration files may also be present in the repository.

## Prerequisites

- Python 3.11 or another compatible Python version.
- An AWS account.
- An appropriately configured Amazon S3 bucket.
- An Amazon RDS MySQL database.
- An Amazon Cognito user pool and app client.
- AWS credentials with least-privilege permissions.
- Docker, if using the containerized version.

## Local Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Badcoder007/CloudDrop.git
cd CloudDrop
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the variable names expected by the application.

Typical settings include:

- `AWS_REGION`
- `S3_BUCKET`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `FLASK_SECRET_KEY`
- Cognito user pool, client, and hosted UI configuration

Use your own environment-specific values. Never commit `.env` or other secret credentials to GitHub.

### 5. Configure AWS resources

Configure the required IAM permissions, S3 bucket, RDS database, and Cognito app client. Ensure the application can reach RDS through appropriately restricted network rules.

Set Cognito callback and sign-out URLs to match the address used to run the application.

### 6. Run the application

```powershell
python app.py
```

Open the local application at:

http://localhost:5000

## Docker Setup

Build the Docker image from the project directory:

```bash
docker build -t clouddrop:latest .
```

Run the container using a local environment file:

```bash
docker run -d --name clouddrop --env-file .env -p 5000:5000 clouddrop:latest
```

Ensure the container has network connectivity to the required AWS services. Do not include `.env` or credentials in the Docker image.

## Security Considerations

- Use Amazon Cognito for authentication.
- Restrict file operations to resources owned by the authenticated user.
- Use short-lived presigned URLs for temporary file access.
- Apply least-privilege IAM policies.
- Restrict RDS access with security groups.
- Keep AWS credentials, database passwords, Cognito client secrets, and Flask session secrets out of source control.
- Use HTTPS for publicly deployed applications.
- Avoid exposing the MySQL port to unrestricted internet access.

## Future Enhancements

Potential improvements include:

- Public deployment using Vercel or an AWS-hosted application environment.
- Custom domain configuration using Amazon Route 53.
- Centralized secret management using AWS Secrets Manager.
- Load balancing and automatic scaling.
- CDN integration using Amazon CloudFront.
- AI-powered file classification and intelligent search.
- Improved direct-to-S3 uploads for larger files.

## Project Status

CloudDrop is a cloud computing project combining a Flask web application with AWS storage, authentication, database, notification, and monitoring services.

Deployment configuration and future enhancements should be validated in the target environment before being considered production-ready.
