from flask import Flask, request, jsonify
import os
import csv

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    filename = data.get('file')
    product = data.get('product')
    base_filename = os.path.basename(filename)
    if not os.path.exists(filename):
        return jsonify({"file": base_filename, "error": "File not found."}), 404

    try:
        total = 0
        with open(filename, 'r') as f:
            try:
                csv.Sniffer().sniff(f.read(1024))
                f.seek(0)
            except csv.Error:
                raise ValueError("Invalid CSV format")

            reader = csv.DictReader(f)
            if not {'product', 'amount'}.issubset(reader.fieldnames or []):
                raise ValueError("Missing required headers")

            for row in reader:
                if row.get('product') == product:
                    total += int(row.get('amount', 0))

        return jsonify({"file": base_filename, "sum": total})
    except (ValueError, csv.Error, KeyError):
        return jsonify({"file": base_filename, "error": "Input file not in CSV format."}), 400
    except Exception:
        return jsonify({"file": base_filename, "error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)