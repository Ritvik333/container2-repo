from flask import Flask, request, jsonify
import os
import csv

app = Flask(__name__)

# Persistent storage path
PERSISTENT_STORAGE_PATH = "/ritvik_PV_dir"

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data or 'file' not in data or 'product' not in data:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400

    filename = data.get('file')
    product = data.get('product')
    
    file_path = os.path.join(PERSISTENT_STORAGE_PATH, filename)
    if not os.path.exists(file_path):
        return jsonify({"file": filename, "error": "File not found."}), 404

    try:
        total = 0
        with open(file_path, 'r', encoding='utf-8') as f:  # Explicit encoding
            contents = f.read()
            print(f"File contents: {contents}")  # Debug: Full contents
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(contents)
                print(f"Detected dialect: {dialect}")  # Debug: Dialect
                f.seek(0)
            except csv.Error as e:
                print(f"Sniff error: {e}")  # Debug: Sniff failure reason
                return jsonify({"file": filename, "error": "Input file not in CSV format."}), 400

            reader = csv.DictReader(f)
            print(f"Fieldnames: {reader.fieldnames}")  # Debug: Detected headers
            if not {'product', 'amount'}.issubset(reader.fieldnames or []):
                print(f"Missing required headers: expected {'product, amount'}, got {reader.fieldnames}")
                return jsonify({"file": filename, "error": "Input file not in CSV format."}), 400

            for row in reader:
                if row.get('product') == product:
                    total += int(row.get('amount', 0))

        return jsonify({"file": filename, "sum": total}), 200
    except (ValueError, csv.Error, KeyError) as e:
        print(f"Parsing error: {e}")  # Debug: Parsing failure
        return jsonify({"file": filename, "error": "Input file not in CSV format."}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug: Other errors
        return jsonify({"file": filename, "error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)