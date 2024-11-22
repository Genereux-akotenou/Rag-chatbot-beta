from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../database/document')

# Serve files from the ../database/document folder
@app.route('/<path:filename>')
def serve_file(filename):
    """
    Serve files from the specified directory.
    """
    return send_from_directory(app.static_folder, filename)

# Serve files from the ./static folder
@app.route('/static/file/<path:filename>')
def serve_static_file(filename):
    """
    Serve files from the static folder.
    """
    static_folder = './static'
    return send_from_directory(static_folder, filename)

@app.route('/')
def list_files():
    """
    List all files in the specified directory as hyperlinks.
    """
    # Get the list of files from the ../database/document folder
    files = [f for f in os.listdir(app.static_folder) if os.path.isfile(os.path.join(app.static_folder, f))]
    
    # Create HTML list of file links for files in the ../database/document folder
    file_links = '\n'.join([f'<li><a href="/{f}">{f}</a></li>' for f in files])
    
    # Get the list of files from the ./static folder
    static_folder = './static'
    static_files = [f for f in os.listdir(static_folder) if os.path.isfile(os.path.join(static_folder, f))]
    
    # Add links for files in the ./static folder
    static_file_links = '\n'.join([f'<li><a href="/static/file/{f}">{f}</a></li>' for f in static_files])
    
    return f"<h3>Files in ../database/document folder:</h3><ul>{file_links}</ul><h3>Files in ./static folder:</h3><ul>{static_file_links}</ul>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)