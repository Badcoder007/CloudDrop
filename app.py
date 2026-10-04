from flask import Flask, request, render_template_string,redirect
from s3_service import upload_file,get_storage_info,download_file,delete_file

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>CloudDrop | Cloud Storage</title>

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #f4f7fb;
            color: #172033;
            min-height: 100vh;
        }

        .navbar {
            height: 70px;
            background: white;
            border-bottom: 1px solid #e7ebf2;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 7%;
        }

        .logo {
            font-size: 25px;
            font-weight: 700;
            color: #172033;
        }

        .logo span {
            color: #5b67f1;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #596579;
        }

        .status-dot {
            width: 9px;
            height: 9px;
            background: #22c55e;
            border-radius: 50%;
        }

        .container {
            width: 86%;
            max-width: 1100px;
            margin: 45px auto;
        }

        .hero {
            margin-bottom: 30px;
        }

        .hero h1 {
            font-size: 38px;
            margin-bottom: 10px;
        }

        .hero p {
            color: #697586;
            font-size: 16px;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 25px;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 28px;
            border: 1px solid #e7ebf2;
            box-shadow: 0 8px 30px rgba(30, 45, 70, 0.06);
        }

        .upload-card {
            min-height: 370px;
        }

        .upload-title {
            font-size: 21px;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .drop-zone {
            border: 2px dashed #b9c1d0;
            border-radius: 18px;
            min-height: 240px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            transition: 0.25s;
            padding: 25px;
        }

        .drop-zone:hover {
            border-color: #5b67f1;
            background: #f8f9ff;
        }

        .cloud-icon {
            font-size: 55px;
            margin-bottom: 12px;
        }

        .drop-zone h2 {
            font-size: 20px;
            margin-bottom: 8px;
        }

        .drop-zone p {
            color: #7a8494;
            margin-bottom: 20px;
            font-size: 14px;
        }

        input[type="file"] {
            display: none;
        }

        .choose-btn {
            display: inline-block;
            background: #5b67f1;
            color: white;
            padding: 12px 22px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            border: none;
        }

        .choose-btn:hover {
            background: #4854dc;
        }

        .upload-btn {
            margin-top: 15px;
            width: 100%;
            padding: 13px;
            background: #172033;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 15px;
        }

        .upload-btn:hover {
            background: #273149;
        }

        .message {
            margin-top: 15px;
            padding: 12px;
            background: #ecfdf3;
            color: #15803d;
            border-radius: 10px;
            font-size: 14px;
        }

        .side-card h3 {
            margin-bottom: 22px;
            font-size: 18px;
        }

        .storage-number {
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .storage-text {
            color: #7a8494;
            font-size: 14px;
        }

        .progress {
            height: 9px;
            background: #e9edf4;
            border-radius: 20px;
            margin: 18px 0 10px;
            overflow: hidden;
        }

        .progress-bar {
            width: 38%;
            height: 100%;
            background: #5b67f1;
            border-radius: 20px;
        }

        .connection {
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid #edf0f5;
        }

        .connection-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 13px;
            font-size: 14px;
        }

        .connected {
            color: #16a34a;
            font-weight: 600;
        }

        .files-card {
            margin-top: 25px;
        }

        .files-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .files-header h2 {
            font-size: 20px;
        }

        .file-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 5px;
            border-bottom: 1px solid #edf0f5;
        }

        .file-name {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
        }

        .file-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: #eef0ff;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .file-status {
            color: #16a34a;
            font-size: 13px;
            font-weight: 600;
        }

        .architecture {
            margin-top: 25px;
            text-align: center;
        }

        .architecture h2 {
            margin-bottom: 8px;
        }

        .architecture p {
            color: #7a8494;
            margin-bottom: 25px;
        }

        .architecture-flow {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        .architecture-box {
            padding: 16px 22px;
            background: #f6f7ff;
            border: 1px solid #dfe2ff;
            border-radius: 12px;
            font-weight: 600;
        }

        .arrow {
            font-size: 22px;
            color: #7b8494;
        }

        footer {
            text-align: center;
            color: #8992a1;
            font-size: 13px;
            margin: 35px 0;
        }

        @media (max-width: 800px) {

            .main-grid {
                grid-template-columns: 1fr;
            }

            .container {
                width: 92%;
            }

            .hero h1 {
                font-size: 30px;
            }

            .navbar {
                padding: 0 4%;
            }
        }

    </style>
</head>


<body>

    <nav class="navbar">

        <div class="logo">
            ☁ Cloud<span>Drop</span>
        </div>

        <div class="status">
            <div class="status-dot"></div>
            S3 Connected
        </div>

    </nav>


    <main class="container">

        <section class="hero">

            <h1>Your cloud. Your files.</h1>

            <p>
                Securely upload and manage your files using Amazon S3.
            </p>

        </section>


        <div class="main-grid">


            <!-- UPLOAD -->

            <div class="card upload-card">

                <div class="upload-title">
                    Upload a file
                </div>


                <form action="/upload"
                      method="POST"
                      enctype="multipart/form-data">


                    <div class="drop-zone">

                        <div class="cloud-icon">
                            ☁️
                        </div>

                        <h2>
                            Drop your file here
                        </h2>

                        <p>
                            or choose a file from your computer
                        </p>


                        <label class="choose-btn"
                               for="file">

                            Choose File

                        </label>


                        <input
                            type="file"
                            id="file"
                            name="file"
                            required
                        >

                    </div>


                    <button
                        class="upload-btn"
                        type="submit">

                        Upload to Cloud

                    </button>


                </form>


                {% if message %}

                <div class="message">

                    ✓ {{ message }}

                </div>

                {% endif %}


            </div>


            <!-- STORAGE -->

            <div class="card side-card">

                <h3>
                    Cloud Storage
                </h3>


               <div class="storage-number">
                   {{ "%.2f"|format(storage.total_size / 1024 / 1024) }} MB
               </div>

               <div class="storage-text">
                  of 10 GB quota
               </div>


                <div class="progress">

                    <div class="progress-bar"></div>

                </div>


                <div class="storage-text">
                    38% of storage used
                </div>


                <div class="connection">

                    <h3>
                        Cloud Connection
                    </h3>


                    <div class="connection-row">

                        <span>
                            Storage
                        </span>

                        <span class="connected">
                            ● Online
                        </span>

                    </div>


                    <div class="connection-row">

                        <span>
                            Provider
                        </span>

                        <span>
                            Amazon S3
                        </span>

                    </div>


                    <div class="connection-row">

                        <span>
                            Region
                        </span>

                        <span>
                            Mumbai
                        </span>

                    </div>

                </div>

            </div>


        </div>


        <!-- RECENT FILES -->

        <div class="card files-card">

            <div class="files-header">

                <h2>
                    Recent Files
                </h2>

                <span class="storage-text">
                    Cloud storage
                </span>

            </div>


           {% if storage.files %}

   {% for file in storage.files %}

    <div class="file-row">

        <div class="file-name">

            <div class="file-icon">
                📄
            </div>

            <span>
                {{ file.name }}
            </span>

        </div>

        <div style="display: flex; align-items: center; gap: 15px;">

            <span class="file-status">
                {{ "%.2f"|format(file.size / 1024 / 1024) }} MB
            </span>

            <a
                href="/download/{{ file.name }}"
                style="
                    text-decoration: none;
                    color: #5b67f1;
                    font-weight: 600;
                "
            >
                Download
            </a>

            <form
                action="/delete/{{ file.name }}"
                method="POST"
                style="display: inline;"
                onsubmit="return confirm('Delete this file?');"
            >

                <button
                    type="submit"
                    style="
                        border: none;
                        background: none;
                        color: #ef4444;
                        cursor: pointer;
                        font-weight: 600;
                    "
                >
                    Delete
                </button>

            </form>

        </div>

    </div>

{% endfor %}

{% else %}

    <div class="file-row">

        <div class="file-name">

            <div class="file-icon">
                ☁️
            </div>

            <span>
                No files uploaded yet
            </span>

        </div>

    </div>

{% endif %}


        </div>


        <!-- ARCHITECTURE -->

        <div class="card architecture">

            <h2>
                Cloud Architecture
            </h2>

            <p>
                How CloudDrop communicates with AWS
            </p>


            <div class="architecture-flow">

                <div class="architecture-box">
                    👤 User
                </div>

                <div class="arrow">
                    →
                </div>

                <div class="architecture-box">
                    ⚙️ Flask
                </div>

                <div class="arrow">
                    →
                </div>

                <div class="architecture-box">
                    🔗 Boto3
                </div>

                <div class="arrow">
                    →
                </div>

                <div class="architecture-box">
                    ☁️ Amazon S3
                </div>

            </div>

        </div>


        <footer>

            CloudDrop • Built with Python, Flask & AWS

        </footer>


    </main>

</body>

</html>
"""


@app.route("/")
def home():

    storage = get_storage_info()

    return render_template_string(
        HTML,
        message=None,
        uploaded_file=None,
        storage=storage
    )


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    if not file:

        storage = get_storage_info()

        return render_template_string(
            HTML,
            message="Please select a file.",
            uploaded_file=None,
            storage=storage
        )

    try:

        message = upload_file(
            file,
            file.filename
        )

        storage = get_storage_info()

        return render_template_string(
            HTML,
            message=message,
            uploaded_file=file.filename,
            storage=storage
        )

    except Exception as e:

        return render_template_string(
            HTML,
            message=f"Upload failed: {str(e)}",
            uploaded_file=None,
            storage={
                "total_size": 0,
                "file_count": 0,
                "files": []
            }
        )

@app.route("/download/<path:filename>")
def download(filename):

    try:
        url = download_file(filename)

        return redirect(url)

    except Exception as e:
        return f"Download failed: {str(e)}"

@app.route("/delete/<path:filename>", methods=["POST"])
def delete(filename):

    try:
        message = delete_file(filename)

        return redirect("/")

    except Exception as e:
        return f"Delete failed: {str(e)}"

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )