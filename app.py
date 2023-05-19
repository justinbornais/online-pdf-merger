import os
import csv
from flask import Flask, flash, request, render_template, send_file
import requests
from PyPDF2 import PdfMerger
import random
import string


app = Flask(__name__)
merged = []

UPLOAD_FOLDER = 'Uploads'
ALLOWED_EXTENSIONS = {'csv'}
# Define HTTP Headers
headers = {
    "User-Agent": "Chrome/51.0.2704.103",
}

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def download_pdf(url, file_name):

    # Send GET request
    try:
        response = requests.get(url)#, headers=headers)

        # Save the PDF
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
        else:
            print(response.status_code)
        return 0
    except:
        return 1

@app.route('/')
def index():
    return render_template("index.html", data="All Systems Functioning Properly")

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST': # Check if the user posted a file.
        numFiles = int(request.form['numFiles']) # Get the initial number of files from the form.
        files = [] # Initialize the array of file links.
        saved_files = [] # Array of files saved.
        temp = 0 # Temporary but actual number of files uploaded.
        filename = get_random_string(16) # Get random unique filename to facilitate multiple clients at once.
        saved_name = f'{filename}result'
        
        if len(request.form['filename']) > 0:
            print(request.form['filename'])
            saved_name = str(request.form['filename'])

        for i in range(1, numFiles):
            if len(request.form['link'+str(i)]) == 0: continue # Skip empty inputs.
            files.append(request.form['link'+str(i)]) # Add to array.
            temp += 1
        
        numFiles = temp # Update numFiles with the actual number of files uploaded.

        if numFiles <= 0:
            return render_template("index.html", data="No files given.")

        # Make the "static" directory in this project if it doesn't exist.
        if not os.path.isdir('static'):
            os.mkdir('static')
        
        # Try downloading the PDFs.
        for i in range(numFiles):
            if download_pdf(files[i], f"static/{filename}{i}.pdf") == 1:
                return render_template("index.html", data="Unable to download files.")
            saved_files.append(f"static/{filename}{i}.pdf")
            
        
        # Merge PDFs.
        try:
            merger = PdfMerger()
            for pdf in saved_files:
                merger.append(pdf)
            
            merger.write(f"static/{saved_name}.pdf")
            merger.close()

            for file in saved_files:
                os.remove(file)
            
            currentSize = len(merged)
            merged.append(f"static/{saved_name}.pdf")

            return send_file(merged[currentSize], as_attachment=True)
        except:
            return render_template("index.html", data="Failed to create PDF document.")

if __name__ == "__main__":
    app.run(debug=True)