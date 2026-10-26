import os
import hashlib
from flask import Flask, request, render_template_string,redirect,url_for,session
from urllib.parse import urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from s3_service import (
    upload_file,
    get_storage_info,
    download_file,
    delete_file,
    # find_duplicate
)
from db_service import (
    get_or_create_user,
    file_exists_for_user,
    save_file_metadata,
    get_file_for_user,
    delete_file_metadata
)

load_dotenv(override=True)

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)

# app.config["SESSION_COOKIE_NAME"] = "clouddrop_session"
# app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# app.config["SESSION_COOKIE_SECURE"] = False


COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")

COGNITO_ISSUER = (
    f"https://cognito-idp.us-east-1.amazonaws.com/"
    f"{COGNITO_USER_POOL_ID}"
)

oauth.register(
    name="cognito",
    client_id=COGNITO_CLIENT_ID,
    client_secret=COGNITO_CLIENT_SECRET,
    server_metadata_url=(
        f"{COGNITO_ISSUER}/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)

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
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
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
    width: 100%;
    box-sizing: border-box;
    margin-top: 20px;
    padding: 18px 24px;
    background: #ecfdf3;
    color: #15803d;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.5;
    min-height: 55px;
    display: flex;
    align-items: center;
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

        .share-btn {
                text-decoration: none;
                padding: 8px 14px;
                border-radius: 8px;
                background: #eef2ff;
                color: #4f46e5;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #c7d2fe;
            }

        .share-btn:hover {
                background: #e0e7ff;
            }
            
        .share-box {
    margin: 20px 0;
    padding: 20px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
}

.share-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 12px;
}

.share-box input {
    width: 70%;
    padding: 10px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

.share-box button {
    padding: 10px 16px;
    margin-left: 8px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

.share-expiry {
    margin-top: 10px;
    font-size: 13px;
    color: #64748b;
}

.analytics-section {
    margin-top: 30px;
    width: 100%;
}

.analytics-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(250px, 1fr));
    gap: 18px;
    margin-top: 15px;
}

.analytics-card {
    padding: 20px;
    border-radius: 14px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    min-width: 0;
}

.analytics-label {
    color: #64748b;
    font-size: 14px;
}

.analytics-value {
    margin-top: 8px;
    font-size: 26px;
    font-weight: 700;
}

.analytics-content {
    display: grid;
    grid-template-columns: minmax(280px, 1fr) minmax(350px, 1.3fr);
    gap: 20px;
    margin-top: 20px;
    width: 100%;
}

.analytics-box {
    padding: 20px;
    border-radius: 14px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    min-width: 0;
}

.analytics-box h3 {
    margin-top: 0;
    margin-bottom: 15px;
}

.type-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 14px;
}

.type-row span:first-child {
    overflow-wrap: anywhere;
}

.type-row span:last-child {
    white-space: nowrap;
}

@media (max-width: 800px) {

    .analytics-grid,
    .analytics-content {
        grid-template-columns: 1fr;
    }

}    </style>
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

            {% if share_url %}
            <div class="share-box">
                <div class="share-title">🔗 Secure Share Link</div>

             <input
             type="text"
            id="shareLink"
            value="{{ share_url }}"
            readonly
            >

            <button onclick="copyShareLink()">
                Copy Link
            </button>

            <div class="share-expiry">
            ⏱ This link expires in 5 minutes.
                </div>
            </div>
            {% endif %}

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
                
                <div class="analytics-section">

                    <div class="section-title">
                        📊 Storage Analytics
                    </div>

                    <div class="analytics-grid">

                    <div class="analytics-card">
                        <div class="analytics-label">
                            Total Files
                        </div>

                        <div class="analytics-value">
                            {{ storage.file_count }}
                        </div>
                    </div>

                    <div class="analytics-card">
                        <div class="analytics-label">
                            Storage Used
                        </div>

                        <div class="analytics-value">
                            {{ "%.2f"|format(storage.total_size / 1024 / 1024) }} MB
                        </div>
                    </div>

                </div>


                <div class="analytics-content">

                    <div class="analytics-box">

                        <h3>File Types</h3>

                        {% if storage.file_types %}

                            {% for type, size in storage.file_types.items() %}

                                <div class="type-row">

                                    <span>
                                        {{ type }}
                                    </span>

                                    <span>
                                        {{ "%.2f"|format(size / 1024 / 1024) }} MB
                                    </span>

                                </div>

                            {% endfor %}

                        {% else %}

                            <p>No files uploaded yet.</p>

                        {% endif %}

                    </div>


                    <div class="analytics-box">

                        <h3>Largest Files</h3>

                        {% if storage.largest_files %}

                            {% for file in storage.largest_files %}

                                <div class="type-row">

                                    <span>
                                        {{ file.name }}
                                    </span>

                                    <span>
                                        {{ "%.2f"|format(file.size / 1024 / 1024) }} MB
                                    </span>

                                </div>

                            {% endfor %}

                        {% else %}

                            <p>No files uploaded yet.</p>

                        {% endif %}

                    </div>

                </div>

            </div>

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
            
            {% if session.get("user") %}
<div style="
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <span>
        👤 {{ session["user"].get("email", "User") }}
    </span>

    <a
        href="/logout"
        style="
            text-decoration: none;
            color: #ef4444;
            font-weight: 600;
        "
    >
        Logout
    </a>
</div>
{% endif %}


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
    href="/download/{{ file.s3_key }}"
    style="
        text-decoration: none;
        color: #5b67f1;
        font-weight: 600;
    "
>
    Download
</a>

<a
    href="/share/{{ file.s3_key }}"
    style="
        text-decoration: none;
        color: #10b981;
        font-weight: 600;
        margin-left: 15px;
    "
>
    Share
</a>

<form
    action="/delete/{{ file.s3_key }}" method="POST"
    style="display: inline; margin-left: 15px;"
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
    
    <script>
function copyShareLink() {
    const link = document.getElementById("shareLink");

    navigator.clipboard.writeText(link.value);

    alert("Secure share link copied!");
}
</script>

</body>

</html>
"""

@app.route("/login")
def login():
    redirect_uri = "http://localhost:5000/callback"
    return oauth.cognito.authorize_redirect(redirect_uri)

    
@app.route("/callback")
def callback():

    token = oauth.cognito.authorize_access_token()

    user = token.get("userinfo")

    if not user:
        return "Authentication failed.", 401

    cognito_sub = user.get("sub")
    email = user.get("email")

    user_id = get_or_create_user(
        cognito_sub,
        email
    )

    session["user"] = user
    session["user_id"] = user_id

    return redirect(url_for("index"))

@app.route("/")
def index():

    if "user" not in session:
        return redirect(url_for("login"))

    cognito_sub = session["user"]["sub"]

    user_prefix = f"users/{cognito_sub}/"

    storage = get_storage_info(user_prefix)

    return render_template_string(
        HTML,
        message=None,
        uploaded_file=None,
        storage=storage,
        share_url=None
    )

@app.route("/logout")
def logout():

    session.clear()

    logout_params = urlencode({
        "client_id": COGNITO_CLIENT_ID,
        "logout_uri": "http://localhost:5000/"
    })

    logout_url = (
        f"{COGNITO_DOMAIN}/logout?"
        f"{logout_params}"
    )

    return redirect(logout_url)

@app.route("/upload", methods=["POST"])
def upload():

    # Make sure user is logged in
    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files.get("file")

    cognito_sub = session["user"]["sub"]
    user_id = session["user_id"]

    user_prefix = f"users/{cognito_sub}/"

    if not file:
        storage = get_storage_info(user_prefix)

        return render_template_string(
            HTML,
            message="Please select a file.",
            uploaded_file=None,
            storage=storage,
            share_url=None
        )

    try:

        # ------------------------------------------------
        # STEP 1: Read file into memory
        # ------------------------------------------------

        file_data = file.read()

        file_size = len(file_data)

        # ------------------------------------------------
        # STEP 2: Calculate SHA-256 hash
        # ------------------------------------------------

        file_hash = hashlib.sha256(
            file_data
        ).hexdigest()
        
        print("UPLOADED FILE HASH:", file_hash)
        # ------------------------------------------------
        # STEP 3: Check duplicate in RDS
        # ------------------------------------------------

        existing_file = file_exists_for_user(
            user_id,
            file_hash
        )
        
        print("USER ID:", user_id)
        print("HASH:", file_hash)
        print("EXISTING FILE:", existing_file)

        if existing_file:

            print("DUPLICATE DETECTED - STOPPING UPLOAD")
            storage = get_storage_info(
                user_prefix
            )

            return render_template_string(
                HTML,
                message=(
                    f"Duplicate file detected! "
                    f"This file already exists as "
                    f"'{existing_file['filename']}'."
                ),
                uploaded_file=None,
                storage=storage,
                share_url=None
            )

        # ------------------------------------------------
        # STEP 4: Create user-specific S3 key
        # ------------------------------------------------

        filename = file.filename

        s3_key = (
            f"users/{cognito_sub}/{filename}"
        )

        # ------------------------------------------------
        # STEP 5: Upload file to S3
        # ------------------------------------------------

        from io import BytesIO

        file_stream = BytesIO(file_data)

        message = upload_file(
            file_stream,
            s3_key
        )

        # ------------------------------------------------
        # STEP 6: Determine file type
        # ------------------------------------------------

        if "." in filename:
            file_type = filename.rsplit(
                ".",
                1
            )[1].lower()
        else:
            file_type = "unknown"

        # ------------------------------------------------
        # STEP 7: Save metadata in RDS
        # ------------------------------------------------

        save_file_metadata(
            user_id=user_id,
            filename=filename,
            s3_key=s3_key,
            file_hash=file_hash,
            file_size=file_size,
            file_type=file_type
        )

        # ------------------------------------------------
        # STEP 8: Refresh user's storage
        # ------------------------------------------------

        storage = get_storage_info(
            user_prefix
        )

        return render_template_string(
            HTML,
            message=(
                f"File uploaded successfully: "
                f"{filename}"
            ),
            uploaded_file=filename,
            storage=storage,
            share_url=None
        )

    except Exception as e:

        print(
            "UPLOAD ERROR:",
            str(e)
        )

        storage = get_storage_info(
            user_prefix
        )

        return render_template_string(
            HTML,
            message=f"Upload failed: {str(e)}",
            uploaded_file=None,
            storage=storage,
            share_url=None
        )
                
@app.route("/download/<path:filename>")
def download(filename):

    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    file_record = get_file_for_user(
        user_id,
        filename
    )

    if not file_record:
        return "Access denied.", 403

    try:

        url = download_file(
            file_record["s3_key"]
        )

        return redirect(url)

    except Exception as e:

        return f"Download failed: {str(e)}"

@app.route("/share/<path:filename>")
def share(filename):

    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    file_record = get_file_for_user(
        user_id,
        filename
    )

    if not file_record:
        return "Access denied.", 403

    try:

        url = download_file(
            file_record["s3_key"]
        )

        storage = get_storage_info(
            f"users/{session['user']['sub']}/"
        )

        return render_template_string(
            HTML,
            message="Secure share link generated!",
            uploaded_file=None,
            storage=storage,
            share_url=url
        )

    except Exception as e:

        return f"Share failed: {str(e)}"

@app.route("/delete/<path:filename>", methods=["POST"])
def delete(filename):

    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    file_record = get_file_for_user(
        user_id,
        filename
    )

    if not file_record:
        return "Access denied.", 403

    try:

        delete_file(
            file_record["s3_key"]
        )
        delete_file_metadata(
        user_id,
        file_record["s3_key"]
)
        return redirect(url_for("index"))

    except Exception as e:

        return f"Delete failed: {str(e)}"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )