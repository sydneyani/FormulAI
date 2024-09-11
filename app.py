from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import logging
from werkzeug.utils import secure_filename
from utils.formula_generation import generate_formula

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Store columns and sample data globally (for simplicity)
uploaded_file_data = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/taskpane')
def taskpane():
    return render_template('taskpane.html')

# Endpoint for uploading Excel files
@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_data  # Use global dictionary to store file data

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Ensure the file is an Excel file
    if file and (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the uploaded file
        file.save(file_path)

        try:
            # Read the Excel file
            df = pd.read_excel(file_path)

            # Convert NaN to None (which becomes null in JSON)
            df = df.where(pd.notnull(df), None)

            # Extract column names and a sample of the data
            columns = df.columns.tolist()
            sample_data = df.head(5).to_dict(orient='records')  # Limit to first 5 rows for sample

            # Store the data globally for access when generating the formula
            uploaded_file_data['columns'] = columns
            uploaded_file_data['sample_data'] = sample_data

            return jsonify({'message': f'File {filename} uploaded successfully!'})

        except Exception as e:
            return jsonify({'message': f'Error processing file: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Invalid file type. Please upload an Excel file.'}), 400


# Endpoint for generating formula using the uploaded file's context and user's query
@app.route('/generate', methods=['POST'])
def generate():
    global uploaded_file_data  # Use the uploaded file data

    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"message": "Query is missing"}), 400

    columns = uploaded_file_data.get('columns')
    sample_data = uploaded_file_data.get('sample_data')

    if not columns or not sample_data:
        return jsonify({"message": "No file uploaded or file data missing"}), 400

    # Call the function to generate the formula using query, columns, and sample data
    formula = generate_formula(query, columns, sample_data)

    return jsonify({"formula": formula})


if __name__ == '__main__':
    app.run(debug=True)
