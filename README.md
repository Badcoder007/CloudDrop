# ☁️ CloudDrop

CloudDrop is a cloud-based file storage application developed using
Python Flask and Amazon S3.

## 🚀 Features

- Upload files
- Download files
- Delete files
- View stored files
- File count
- Storage usage calculation
- Cloud-based storage using Amazon S3

## 🛠️ Technologies

- Python
- Flask
- HTML
- CSS
- JavaScript
- Boto3
- Amazon S3
- AWS IAM

## 🏗️ Architecture

User
↓
Flask Web Application
↓
Boto3
↓
AWS IAM
↓
Amazon S3

## ⚙️ Installation

Clone the repository:

git clone YOUR_REPOSITORY_URL

Create a virtual environment:

python -m venv venv

Activate it:

Windows:
venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Configure environment variables.

Run:

python app.py

## 🔐 Security

AWS credentials are stored using environment variables
and are not included in the repository.

## 🔮 Future Scope

- User authentication
- File sharing
- EC2 deployment
- Docker containerization
- CloudWatch monitoring
- Database integration
- CI/CD pipeline
