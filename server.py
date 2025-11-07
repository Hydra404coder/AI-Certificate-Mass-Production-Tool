from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/start', methods=['POST'])
def start_certificate_tool():
    try:
        # Get the directory where server.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_py_path = os.path.join(current_dir, 'main.py')
        
        # Execute main.py
        subprocess.Popen(['python', main_py_path])
        
        return jsonify({
            'status': 'success',
            'message': 'Certificate Mass Production Tool started successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
