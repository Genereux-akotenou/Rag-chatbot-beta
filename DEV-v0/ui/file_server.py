from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os

app = Flask(__name__, static_folder='../database/document')
UPLOAD_FOLDER = '../database/document'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """
    Check if the file is a PDF.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/<path:filename>')
def serve_file(filename):
    """
    Serve files from the specified directory.
    """
    return send_from_directory(app.static_folder, filename)

@app.route('/static/file/<path:filename>')
def serve_static_file(filename):
    """
    Serve files from the static folder.
    """
    static_folder = './static'
    return send_from_directory(static_folder, filename)

@app.route('/ui/file_manager', methods=['GET', 'POST'])
def file_manager():
    """
    Provide a UI for uploading and deleting PDF files.
    """
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return "No file part in the request", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            on_new_upload(filepath)  # Placeholder for additional processing
            return redirect(url_for('file_manager'))
        return "File not allowed", 400

    # List available files
    files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    
    # HTML template for file manager
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Manager</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f9;
            }
            h1 {
                text-align: center;
            }
            .loader {
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                border: 6px solid #f3f3f3;
                border-top: 6px solid #3498db;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            form {
                text-align: center;
                margin-bottom: 20px;
            }
            .file-list {
                margin-top: 20px;
            }
            .file-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 5px 10px;
                border: 1px solid #ddd;
                margin-bottom: 5px;
                border-radius: 5px;
                background-color: #fff;
            }
            .file-item button {
                background-color: red;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                cursor: pointer;
            }
            .file-item button:hover {
                background-color: darkred;
            }
            ul{
                padding-left: 0;
            }
            #upload{
                width: 23em;
                padding: 1.2em;
                background-color: color(srgb 0.9999 1 1);
                margin: auto;
            }
            #upload input{
                font-size: 1em;
            }
        </style>
    </head>
    <body>
        <div class="loader" id="loader"></div>
        <h1>File Manager</h1>
        <form id="upload" method="POST" enctype="multipart/form-data" onsubmit="showLoader()">
            <input type="file" name="file" accept=".pdf">
            <button type="submit">Upload</button>
        </form>
        <div class="file-list">
            <h2>Available Files:</h2>
            <ul>
                {% for file in files %}
                <li class="file-item">
                    <a href="/{{file}}">{{file}}</a>
                    <form method="POST" action="{{ url_for('delete_file', filename=file) }}" style="display:inline;" onsubmit="showLoader()">
                        <button type="submit">Delete</button>
                    </form>
                </li>
                {% endfor %}
            </ul>
        </div>
        <script>
            function showLoader() {
                document.getElementById('loader').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, files=files)

@app.route('/ui/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    """
    Delete the specified file from the directory.
    """
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        on_delete(filepath)  # Placeholder for additional processing
    return redirect(url_for('file_manager'))

@app.route('/')
def list_files():
    """
    List all files in the specified directory as hyperlinks.
    """
    files = [f for f in os.listdir(app.static_folder) if os.path.isfile(os.path.join(app.static_folder, f))]
    file_links = '\n'.join([f'<li><a href="/{f}">{f}</a></li>' for f in files])
    
    static_folder = './static'
    static_files = [f for f in os.listdir(static_folder) if os.path.isfile(os.path.join(static_folder, f))]
    static_file_links = '\n'.join([f'<li><a href="/static/file/{f}">{f}</a></li>' for f in static_files])
    
    return f"<h3>Files in ../database/document folder:</h3><ul>{file_links}</ul><h3>Files in ./static folder:</h3><ul>{static_file_links}</ul>"

def on_new_upload(filepath):
    """
    Placeholder function to handle actions after a new upload.
    """
    print(f"New file uploaded: {filepath}")

def on_delete(filepath):
    """
    Placeholder function to handle actions after a file deletion.
    """
    print(f"File deleted: {filepath}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
